#! /usr/bin/env python3

from pathlib import Path
import pytest

from generator import models as m


def test_package_name_string_validator():
    assert m.package_name_string_validator("valid-name_123") == "valid-name_123"
    with pytest.raises(ValueError):
        m.package_name_string_validator("invalid name")
    with pytest.raises(ValueError):
        m.package_name_string_validator("invalid,name")
    with pytest.raises(ValueError):
        m.package_name_string_validator("invalid\\name")


def test_ensure_env_key_pair():
    assert m.ensure_env_key_pair("KEY=VALUE") == "KEY=VALUE"
    with pytest.raises(ValueError):
        m.ensure_env_key_pair("KEYVALUE")
    with pytest.raises(ValueError):
        m.ensure_env_key_pair("=VALUE")
    with pytest.raises(ValueError):
        m.ensure_env_key_pair("KEY=")


def test_bash_item_list():
    bil = m.BashItemList(
        name="bash",
        items=[
            {
                "name": "some",
                "command": "some --command",
                "info": "Some info about the package",
            },
            {
                "name": "package",
                "command": """package --with \\
    --multiline --command
""",
            },
            {"name": "package", "command": "another-package --with --command"},
        ],
    )

    expected_shortened = """some --command;\\
    package --with \\
        --multiline --command;\\
    another-package --with --command"""

    assert bil.to_shortened_containerfile_directive() == expected_shortened
    assert bil.to_containerfile_directive() == f"""RUN {expected_shortened}"""


def test_apt_get_item(subtests):
    with subtests.test("Full definition with single item"):
        a = m.AptGetItem(name="abc", provides="def")
        assert a.provides == "def"

    with subtests.test("Full definition with items"):
        a = m.AptGetItem(name="abc", provides=["def", "ghi"])
        assert a.provides == ["def", "ghi"]

    with subtests.test("Minimal definition"):
        a = m.AptGetItem(name="abc")
        assert a.provides == "abc"


def test_apt_get_item_list():
    a = m.AptGetItemList(
        name="apt-get", items=[{"name": "abc"}, {"name": "def"}, "ghi"]
    )

    assert (
        a.to_shortened_containerfile_directive()
        == "apt-get update -y && apt-get install -y abc def ghi"
    )
    assert (
        a.to_containerfile_directive()
        == "RUN apt-get update -y && apt-get install -y abc def ghi"
    )


def test_curl_item(subtests):
    with subtests.test("Full definition"):
        c = m.CurlItem.model_validate(
            {
                "name": "curl",
                "version": "123",
                "from": "http://example.com/pkg/{version}",
                "to": "/tmp/pkg-123",
                "command": "ls -la /tmp/pkg-123",
            }
        )
        assert str(c.source) == "http://example.com/pkg/123"
        assert c.to == Path("/tmp/pkg-123")
        assert (
            c.command
            == "curl -sLf http://example.com/pkg/123 -o /tmp/pkg-123 && ls -la /tmp/pkg-123"
        )

    with subtests.test("Full multiline command"):
        c = m.CurlItem.model_validate(
            {
                "name": "curl",
                "version": "123",
                "from": "http://example.com/pkg/{version}",
                "to": "/tmp/pkg-123",
                "command": """ls -la /tmp/pkg-123\\
echo""",
            }
        )
        assert str(c.source) == "http://example.com/pkg/123"
        assert c.to == Path("/tmp/pkg-123")
        assert (
            c.command
            == """curl -sLf http://example.com/pkg/123 -o /tmp/pkg-123 && ls -la /tmp/pkg-123\\
    echo"""
        )
    with subtests.test("Minimal definition"):
        c = m.CurlItem.model_validate(
            {
                "name": "curl-cmd",
                "from": "http://example.com/pkg{version}",
            }
        )
        assert str(c.source) == "http://example.com/pkg"
        assert c.to == Path("/bin/curl-cmd")
        assert (
            c.command
            == "curl -sLf http://example.com/pkg -o /bin/curl-cmd && chmod 755 /bin/curl-cmd"
        )


def test_curl_item_list():
    cil = m.CurlItemList(
        name="curl",
        items=[
            {
                "name": "curl1",
                "from": "http://example.com/pkg1",
            },
            {
                "name": "curl2",
                "from": "http://example.com/pkg2",
            },
        ],
    )

    short = """curl -sLf http://example.com/pkg1 -o /bin/curl1 && chmod 755 /bin/curl1;\\
    curl -sLf http://example.com/pkg2 -o /bin/curl2 && chmod 755 /bin/curl2"""
    assert cil.to_shortened_containerfile_directive() == short
    assert cil.to_containerfile_directive() == f"RUN {short}"


def test_env_item_list():
    eil = m.EnvItemList(
        name="env",
        items=["ENV_VAR1=value1", "ENV_VAR2=value2"],
    )

    assert (
        eil.to_shortened_containerfile_directive() == "ENV_VAR1=value1 ENV_VAR2=value2"
    )
    assert eil.to_containerfile_directive() == "ENV ENV_VAR1=value1 ENV_VAR2=value2"


def test_copy_item(subtests, mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)
    with subtests.test("Has command"):
        copy_item = m.CopyItem.model_validate(
            {
                "from": "/my/path",
                "to": "/my/dest",
                "command": "--chown=65532:65532",
            }
        )
        assert (
            copy_item.to_containerfile_directive()
            == "COPY --chown=65532:65532 /my/path /my/dest"
        )
    with subtests.test("Does not have command"):
        copy_item = m.CopyItem.model_validate(
            {
                "from": "/my/path",
                "to": "/my/dest",
            }
        )
        assert copy_item.to_containerfile_directive() == "COPY /my/path /my/dest"


def test_copy_item_list(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)

    cil = m.CopyItemList(
        name="copy",
        items=[
            {"from": "/path/to/file1", "to": "/dest/file1"},
            {
                "from": "/path/to/file2",
                "to": "/dest/file2",
                "command": "--chown=1000:1000",
            },
        ],
    )

    assert cil.to_shortened_containerfile_directive() == (
        """COPY /path/to/file1 /dest/file1
COPY --chown=1000:1000 /path/to/file2 /dest/file2"""
    )
