#! /usr/bin/env python3

# SPDX-FileCopyrightText: 2025 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from pydantic import ValidationError
import pytest


from generator import models as m


def test_package_name_string_validator():
    assert m.package_name_string_validator("valid-name_123") == "valid-name_123"
    assert m.package_name_string_validator("valid/name_123") == "valid/name_123"
    assert m.package_name_string_validator("valid name") == "valid name"

    with pytest.raises(ValueError):
        m.package_name_string_validator("invalid,name")
    with pytest.raises(ValueError):
        m.package_name_string_validator("invalid\\name")
    with pytest.raises(ValueError):
        m.package_name_string_validator("invalid))name")


def test_ensure_env_key_pair():
    assert m.ensure_env_pair("KEY=VALUE") == "KEY=VALUE"
    with pytest.raises(ValueError):
        m.ensure_env_pair("KEYVALUE")
    with pytest.raises(ValueError):
        m.ensure_env_pair("=VALUE")
    with pytest.raises(ValueError):
        m.ensure_env_pair("KEY=")


def test_bash_item_list(subtests):
    with subtests.test("Valid BashItemList"):
        bil = m.BashItemList.model_validate({
            "name": "bash",
            "items": [
                {
                    "name": "some",
                    "command": "some --command",
                    "info": "Some info about the package",
                },
                {
                    "name": "package",
                    "command": """package --with
    multiline --command
    """,
                },
                {"name": "package", "command": "another-package --with --command"},
            ],
        })

        expected_shortened = """some --command;\\
    package --with;\\
        multiline --command;\\
    another-package --with --command"""

        assert bil.to_shortened_dockerfile_directive() == expected_shortened
        assert bil.to_dockerfile_directive() == f"""RUN {expected_shortened}"""

    with subtests.test("Extra key in item"):
        with pytest.raises(ValidationError):
            m.BashItemList.model_validate({
                "name": "bash",
                "items": [
                    {"name": "invalid", "command": "invalid command", "extra": "key"},
                    {"name": "invalid", "command": "another invalid command"},
                ],
            })


def test_apt_get_item(subtests):
    with subtests.test("Full definition with single item"):
        a = m.AptGetItem(name="abc", provides="def")
        assert a.provides == "def"

    with subtests.test("Full definition with items"):
        a = m.AptGetItem(name="abc", provides=["def", "ghi"])
        assert a.provides == ["def", "ghi"]

    with subtests.test("Minimal definition"):
        a = m.AptGetItem(name="abc")  # type: ignore
        assert a.provides == "abc"

    with subtests.test("Invalid keys"):
        with pytest.raises(ValidationError):
            m.AptGetItem.model_validate({
                "b1": "invalid",
                "name": "abc",
                "info": "Some info",
                "provides": "def",
            })


def test_apt_get_item_list(subtests):
    with subtests.test("Valid configs"):
        a = m.AptGetItemList.model_validate({
            "name": "apt-get", "items": [{"name": "abc"}, {"name": "def"}, "ghi"]
        })

        assert (
            a.to_shortened_dockerfile_directive()
            == """apt-get --yes update && apt-get --yes install abc def ghi;\\
    rm -rf /var/lib/apt/lists"""
        )
        assert (
            a.to_dockerfile_directive()
            == """RUN apt-get --yes update && apt-get --yes install abc def ghi;\\
    rm -rf /var/lib/apt/lists"""
        )
    with subtests.test("Extra keys"):
        with pytest.raises(ValidationError):
            m.AptGetItemList.model_validate({
                "name": "apt-get",
                "items": [
                    {"name": "abc"},
                    {"name": "def"},
                    "ghi",
                ],
                "extra": "key",
            })
    with subtests.test("Invalid item format"):
        with pytest.raises(ValidationError):
            m.AptGetItemList.model_validate({
                "name": "apt-get",
                "items": ["abc", {"name": "def"}, "((asd))"],
            })


def test_shell_aware_http_url(subtests):
    with subtests.test("Valid URL"):
        url = m.ShellAwareHttpUrl("http://example.com")
        assert str(url) == "http://example.com"

    with subtests.test("URL with shell expansion"):
        url = m.ShellAwareHttpUrl(
            "http://example.com/pkg$(echo ${{TARGETARCH}} | sed 's/x86_64/amd64/;s/arm64/arm/')"
        )
        assert (
            str(url)
            == "http://example.com/pkg$(echo ${{TARGETARCH}} | sed 's/x86_64/amd64/;s/arm64/arm/')"
        )

    with subtests.test("Invalid URL raises ValueError"):
        with pytest.raises(ValueError):
            m.ShellAwareHttpUrl("invalid-url")


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
                "command": """ls -la /tmp/pkg-123
echo""",
            }
        )
        assert str(c.source) == "http://example.com/pkg/123"
        assert c.to == Path("/tmp/pkg-123")
        assert (
            c.command
            == """curl -sLf http://example.com/pkg/123 -o /tmp/pkg-123 && ls -la /tmp/pkg-123;\\
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

    with subtests.test("Minimal definition with shell expansion"):
        c = m.CurlItem.model_validate(
            {
                "name": "curl-cmd",
                "version": "1.0",
                "from": "http://example.com/pkg$(echo ${{TARGETARCH}} |sed 's/x86_64/amd64/;s/arm64/arm/')",
            }
        )
        assert (
            str(c.source)
            == "http://example.com/pkg$(echo ${TARGETARCH} |sed 's/x86_64/amd64/;s/arm64/arm/')"
        )
        assert c.to == Path("/bin/curl-cmd")
        assert (
            c.command
            == "curl -sLf http://example.com/pkg$(echo ${TARGETARCH} |sed 's/x86_64/amd64/;s/arm64/arm/') -o /bin/curl-cmd && chmod 755 /bin/curl-cmd"
        )

    with subtests.test("Extra keys"):
        with pytest.raises(ValidationError):
            m.CurlItem.model_validate({
                "name": "curl",
                "from": "http://example.com/pkg",
                "to": "/bin/curl",
                "extra": "key",
            })


def test_curl_item_list(subtests):
    with subtests.test("Valid CurlItemList"):
        cil = m.CurlItemList.model_validate({
            "name": "curl",
            "items": [
                {
                    "name": "curl1",
                    "from": "http://example.com/pkg1",
                },
                {
                    "name": "curl2",
                    "from": "http://example.com/pkg2",
                },
            ],
        })

        short = """curl -sLf http://example.com/pkg1 -o /bin/curl1 && chmod 755 /bin/curl1;\\
    curl -sLf http://example.com/pkg2 -o /bin/curl2 && chmod 755 /bin/curl2"""
        assert cil.to_shortened_dockerfile_directive() == short
        assert cil.to_dockerfile_directive() == f"RUN {short}"
    with subtests.test("Extra key"):
        with pytest.raises(ValidationError):
            m.CurlItemList.model_validate({
                "name": "curl",
                "items": [
                    {"name": "curl1", "from": "http://example.com/pkg1"},
                    {"name": "curl2", "from": "http://example.com/pkg2"},
                ],
                "extra": "key",
            })


def test_env_item_list(subtests):
    with subtests.test("Valid EnvItemList"):
        eil = m.EnvItemList(
            name="env",
            items=["ENV_VAR1=value1", "ENV_VAR2=value2"],
        )

        assert (
            eil.to_shortened_dockerfile_directive() == "ENV_VAR1=value1 ENV_VAR2=value2"
        )
        assert eil.to_dockerfile_directive() == "ENV ENV_VAR1=value1 ENV_VAR2=value2"
    with subtests.test("Extra key"):
        with pytest.raises(ValidationError):
            m.EnvItemList.model_validate({
                "name": "env",
                "items": ["ENV_VAR1=value1", "ENV_VAR2=value2"],
                "extra": "key",
            })
    with subtests.test("Invalid item format"):
        with pytest.raises(ValidationError):
            m.EnvItemList.model_validate({
                "name": "env",
                "items": ["ENV_VAR1=value1", "invalid_item_format"],
            })


def test_copy_item(subtests, mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)
    with subtests.test("Has command"):
        copy_item = m.CopyItem.model_validate(
            {
                "name": "copy",
                "from": "/my/path",
                "to": "/my/dest",
                "command": "--chown=65532:65532",
            }
        )
        assert (
            copy_item.to_dockerfile_directive()
            == "COPY --chown=65532:65532 /my/path /my/dest"
        )
    with subtests.test("Does not have command"):
        copy_item = m.CopyItem.model_validate(
            {
                "name": "copy",
                "from": "/my/path",
                "to": "/my/dest",
            }
        )
        assert copy_item.to_dockerfile_directive() == "COPY /my/path /my/dest"

    with subtests.test("Extra key"):
        with pytest.raises(ValidationError):
            m.CopyItem.model_validate({
                "from": "/my/path",
                "to": "/my/dest",
                "extra": "key",
            })


def test_copy_item_list(mocker, subtests):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)

    with subtests.test("Valid CopyItemList"):
        cil = m.CopyItemList.model_validate({
            "name": "copy",
            "items": [
                {"name": "copy1", "from": "/path/to/file1", "to": "/dest/file1"},
                {
                    "name": "copy2",
                    "from": "/path/to/file2",
                    "to": "/dest/file2",
                    "command": "--chown=1000:1000",
                },
            ],
        })

        assert cil.to_shortened_dockerfile_directive() == (
            """COPY /path/to/file1 /dest/file1
COPY --chown=1000:1000 /path/to/file2 /dest/file2"""
        )
    with subtests.test("Extra key"):
        with pytest.raises(ValidationError):
            m.CopyItemList = m.CopyItemList.model_validate({
                "name": "copy",
                "items": [
                    {"from": "/path/to/file1", "to": "/dest/file1"},
                    {
                        "from": "/path/to/file2",
                        "to": "/dest/file2",
                        "command": "--chown=1000:1000",
                    },
                ],
                "extra": "key",
            })

def test_optional_formated_dict():
    assert m.OptionalFormatedDict({"key": "value"}) == {"key": "value"}
    assert m.OptionalFormatedDict()["my_key"] == "{my_key}"
    assert m.OptionalFormatedDict(a="b")["a"] == "b"


def test_multiline_string_validator():
    assert m.multiline_string_validator("single line", "", "") == "single line"
    string = "line1\nline2\nline3"
    assert m.multiline_string_validator(string, "", "") == string
    assert (
        m.multiline_string_validator(string, "  ", "\\")
    ) == "line1\\\n  line2\\\n  line3"
    assert m.multiline_string_validator("a\n\nb", "  ", "\\") == "a\\\n  b"
    assert m.multiline_string_validator("a\n\nb", "", ";") == "a;\nb"


def test_command_multiline_string_validator():
    assert m.command_multiline_string_validator("single line") == "single line"
    string = "line1\nline2\nline3"
    assert (
        m.command_multiline_string_validator(string)
        == "line1;\\\n    line2;\\\n    line3"
    )
    assert m.command_multiline_string_validator("a\n\nb") == "a;\\\n    b"


def test_base_item_dump_ghelp():
    """Test BaseItem dump_ghelp method"""
    # Test with BaseItem directly (using BashItem as concrete implementation)
    item = m.BashItem(name="test-item", command="test command", info="test info")
    result = item.dump_ghelp()
    expected = ("test-item", None, "test info")
    assert result == expected

    # Test with no info
    item_no_info = m.BashItem(name="test-item", command="test command")
    result_no_info = item_no_info.dump_ghelp()
    expected_no_info = ("test-item", None, None)
    assert result_no_info == expected_no_info


def test_bash_item_list_to_ghelp_format():
    """Test BashItemList to_ghelp_format method"""
    bil = m.BashItemList.model_validate({
        "name": "bash",
        "items": [
            {
                "name": "item1",
                "command": "command1",
                "info": "info1",
            },
            {
                "name": "item2",
                "command": "command2",
            },
        ],
    })

    result = bil.to_ghelp_format()
    expected = [
        ("item1", None, "info1"),
        ("item2", None, None),
    ]
    assert result == expected


def test_apt_get_item_dump_ghelp():
    """Test AptGetItem dump_ghelp method"""
    # Test with provides as string
    item = m.AptGetItem(name="package1", provides="binary1")
    result = item.dump_ghelp()
    expected = ("package1", "binary1")
    assert result == expected

    # Test with provides as list
    item_list = m.AptGetItem(name="package2", provides=["binary1", "binary2"])
    result_list = item_list.dump_ghelp()
    expected_list = ("package2", ["binary1", "binary2"])
    assert result_list == expected_list

    # Test with minimal definition (provides defaults to name)
    item_minimal = m.AptGetItem(name="package3")
    result_minimal = item_minimal.dump_ghelp()
    expected_minimal = ("package3", "package3")
    assert result_minimal == expected_minimal


def test_apt_get_item_list_to_ghelp_format():
    """Test AptGetItemList to_ghelp_format method"""
    ail = m.AptGetItemList.model_validate({
        "name": "apt-get",
        "items": [
            {"name": "package1", "provides": "binary1"},
            "package2",  # string item
            {"name": "package3", "provides": ["binary3a", "binary3b"]},
        ],
    })

    result = ail.to_ghelp_format()
    expected = [
        ("package1", "binary1"),
        ("package2", "package2"),  # string items get converted to (name, name)
        ("package3", ["binary3a", "binary3b"]),
    ]
    assert result == expected


def test_curl_item_dump_ghelp():
    """Test CurlItem dump_ghelp method"""
    # Test with version
    item_with_version = m.CurlItem.model_validate({
        "name": "tool1",
        "version": "1.2.3",
        "from": "http://example.com/tool1-{version}",
        "info": "Some tool info"
    })
    result_with_version = item_with_version.dump_ghelp()
    expected_with_version = ("tool1", "1.2.3", "Some tool info")
    assert result_with_version == expected_with_version

    # Test without version
    item_no_version = m.CurlItem.model_validate({
        "name": "tool2",
        "from": "http://example.com/tool2",
    })
    result_no_version = item_no_version.dump_ghelp()
    expected_no_version = ("tool2", None, None)
    assert result_no_version == expected_no_version


def test_curl_item_list_to_ghelp_format():
    """Test CurlItemList to_ghelp_format method"""
    cil = m.CurlItemList.model_validate({
        "name": "curl",
        "items": [
            {
                "name": "tool1",
                "version": "1.0.0",
                "from": "http://example.com/tool1-{version}",
                "info": "Tool 1 info"
            },
            {
                "name": "tool2",
                "from": "http://example.com/tool2",
            },
        ],
    })

    result = cil.to_ghelp_format()
    expected = [
        ("tool1", "1.0.0", "Tool 1 info"),
        ("tool2", None, None),
    ]
    assert result == expected


def test_info_generator_to_ghelp_format():
    """Test InfoGenerator to_ghelp_format method"""
    # Test with mixed components
    info_gen = m.InfoGenerator.model_validate({
        "components": [
            {
                "name": "apt-get",
                "items": [
                    {"name": "pkg1", "provides": "bin1"},
                    "pkg2",
                ],
            },
            {
                "name": "curl",
                "items": [
                    {
                        "name": "tool1",
                        "version": "1.0.0",
                        "from": "http://example.com/tool1",
                        "info": "Tool info"
                    },
                ],
            },
            {
                "name": "bash",
                "items": [
                    {
                        "name": "script1",
                        "command": "echo test",
                        "info": "Script info"
                    },
                ],
            },
        ],
    })

    result = info_gen.to_ghelp_format()
    expected = {
        "apt": [
            ("pkg1", "bin1"),
            ("pkg2", "pkg2"),
        ],
        "pip": [],
        "downloaded": [
            ("tool1", "1.0.0", "Tool info"),
            ("script1", None, "Script info"),
        ],
    }
    assert result == expected


def test_info_generator_to_ghelp_format_empty():
    """Test InfoGenerator to_ghelp_format method with empty components"""
    info_gen = m.InfoGenerator.model_validate({
        "components": [],
    })

    result = info_gen.to_ghelp_format()
    expected = {
        "apt": [],
        "pip": [],
        "downloaded": [],
    }
    assert result == expected


def test_info_generator_to_ghelp_format_apt_only():
    """Test InfoGenerator to_ghelp_format method with only apt components"""
    info_gen = m.InfoGenerator.model_validate({
        "components": [
            {
                "name": "apt-get",
                "items": ["pkg1", "pkg2", "pkg3"],
            },
        ],
    })

    result = info_gen.to_ghelp_format()
    expected = {
        "apt": [
            ("pkg1", "pkg1"),
            ("pkg2", "pkg2"),
            ("pkg3", "pkg3"),
        ],
        "pip": [],
        "downloaded": [],
    }
    assert result == expected


def test_info_generator_to_ghelp_format_downloaded_only():
    """Test InfoGenerator to_ghelp_format method with only downloaded components"""
    info_gen = m.InfoGenerator.model_validate({
        "components": [
            {
                "name": "curl",
                "items": [
                    {
                        "name": "tool1",
                        "from": "http://example.com/tool1",
                    },
                ],
            },
            {
                "name": "bash",
                "items": [
                    {
                        "name": "script1",
                        "command": "echo hello",
                    },
                ],
            },
        ],
    })

    result = info_gen.to_ghelp_format()
    expected = {
        "apt": [],
        "pip": [],
        "downloaded": [
            ("tool1", None, None),
            ("script1", None, None),
        ],
    }
    assert result == expected
def test_info_multiline_string_validator():
    assert m.info_multiline_string_validator("single line") == "single line"
    string = "line1\nline2\nline3"
    assert (
        m.info_multiline_string_validator(string)
        == "line1\\nline2\\nline3"
    )
    assert m.info_multiline_string_validator("a\n\nb") == "a\\nb"
