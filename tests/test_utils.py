#! /usr/bin/env python3

import generator.utils as u
from generator.models import (
    AptGetItemList,
    CopyItemList,
    CurlItemList,
    BashItemList,
    EnvItemList,
)


def test_can_combine_group_with_previous():
    assert u.can_combine_group_with_previous("RUN", BashItemList(name="bash", items=[]))
    assert not u.can_combine_group_with_previous(
        "ARG", BashItemList(name="bash", items=[])
    )
    assert not u.can_combine_group_with_previous(
        "COPY", CopyItemList(name="copy", items=[])
    )


def test_group_components_by_key(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)
    directives = [
        BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
        AptGetItemList(name="apt-get", items=["curl", "tree"]),
        CopyItemList(
            name="copy",
            items=[
                {"from": "/some/path", "to": "/some/path"},
                {"from": "/another/file", "to": "/yet/another/file"},
            ],
        ),
        CurlItemList(
            name="curl",
            items=[
                {"name": "example1", "from": "https://example.com"},
                {"name": "example2", "from": "https://another.example.com"},
            ],
        ),
        BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
        EnvItemList(name="env", items=["A=B", "C=D"]),
        BashItemList(name="bash", items=["pwd"]),
    ]

    grouped = u.group_components_by_key(directives)
    res = [
        {
            "RUN": [
                BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
                AptGetItemList(name="apt-get", items=["curl", "tree"]),
            ]
        },
        {
            "COPY": [
                CopyItemList(
                    name="copy",
                    items=[
                        {"from": "/some/path", "to": "/some/path"},
                        {"from": "/another/file", "to": "/yet/another/file"},
                    ],
                )
            ]
        },
        {
            "RUN": [
                CurlItemList(
                    name="curl",
                    items=[
                        {"name": "example1", "from": "https://example.com"},
                        {"name": "example2", "from": "https://another.example.com"},
                    ],
                ),
                BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
            ]
        },
        {
            "ENV": [
                EnvItemList(name="env", items=["A=B", "C=D"]),
            ]
        },
        {
            "RUN": [
                BashItemList(name="bash", items=["pwd"]),
            ]
        },
    ]

    assert grouped == res
