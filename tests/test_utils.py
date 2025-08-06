#! /usr/bin/env python3

import generator.utils as u
import generator.models as m


def test_can_combine_group_with_previous():
    assert u.can_combine_group_with_previous(
        "RUN", m.BashItemList(name="bash", items=[])
    )
    assert not u.can_combine_group_with_previous(
        "ARG", m.BashItemList(name="bash", items=[])
    )
    assert not u.can_combine_group_with_previous(
        "COPY", m.CopyItemList(name="copy", items=[])
    )


def test_group_components_by_key(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)
    directives = [
        m.BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
        m.ArgItemList(name="arg", items=["ARG_VAR1=value1", "ARG_VAR2"]),
        m.AptGetItemList(name="apt-get", items=["curl", "tree"]),
        m.CopyItemList(
            name="copy",
            items=[
                {"from": "/some/path", "to": "/some/path"},
                {"from": "/another/file", "to": "/yet/another/file"},
            ],
        ),
        m.CurlItemList(
            name="curl",
            items=[
                {"name": "example1", "from": "https://example.com"},
                {"name": "example2", "from": "https://another.example.com"},
            ],
        ),
        m.BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
        m.EnvItemList(name="env", items=["A=B", "C=D"]),
        m.BashItemList(name="bash", items=["pwd"]),
    ]

    grouped = u.group_components_by_key(directives)
    res = [
        {
            "RUN": [
                m.BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
            ],
        },
        {
            "ARG": [
                m.ArgItemList(
                    key="ARG",
                    can_be_combined=False,
                    name="arg",
                    items=["ARG_VAR1=value1", "ARG_VAR2"],
                ),
            ],
        },
        {
            "RUN": [
                m.AptGetItemList(name="apt-get", items=["curl", "tree"]),
            ]
        },
        {
            "COPY": [
                m.CopyItemList(
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
                m.CurlItemList(
                    name="curl",
                    items=[
                        {"name": "example1", "from": "https://example.com"},
                        {"name": "example2", "from": "https://another.example.com"},
                    ],
                ),
                m.BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
            ]
        },
        {
            "ENV": [
                m.EnvItemList(name="env", items=["A=B", "C=D"]),
            ]
        },
        {
            "RUN": [
                m.BashItemList(name="bash", items=["pwd"]),
            ]
        },
    ]

    assert grouped == res


def test_grouped_components_to_container_layers(mocker, subtests):
    """Test grouped_components_to_container_layers with various scenarios using subtests."""
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)

    assert u.grouped_components_to_container_layers([]) == []
    assert u.grouped_components_to_container_layers(
        [
            {
                "RUN": [
                    m.BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
                ],
            },
            {
                "ARG": [
                    m.ArgItemList(
                        key="ARG",
                        can_be_combined=False,
                        name="arg",
                        items=["ARG_VAR1=value1", "ARG_VAR2"],
                    ),
                ],
            },
            {
                "RUN": [
                    m.AptGetItemList(name="apt-get", items=["curl", "tree"]),
                ]
            },
            {
                "COPY": [
                    m.CopyItemList(
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
                    m.CurlItemList(
                        name="curl",
                        items=[
                            {"name": "example1", "from": "https://example.com"},
                            {
                                "name": "example2",
                                "from": "https://another.example.com",
                            },
                        ],
                    ),
                    m.BashItemList(name="bash", items=["ls -la", "touch /dev/null"]),
                ]
            },
            {
                "ENV": [
                    m.EnvItemList(name="env", items=["A=B", "C=D"]),
                ]
            },
            {
                "RUN": [
                    m.BashItemList(name="bash", items=["pwd"]),
                ]
            },
        ]
    ) == [
        m.ContainerLayer(key="RUN", commands=["RUN ls -la;\\\n    touch /dev/null"]),
        m.ContainerLayer(key="ARG", commands=["ARG ARG_VAR1=value1\nARG ARG_VAR2"]),
        m.ContainerLayer(
            key="RUN",
            commands=[
                "RUN apt-get --yes update && apt-get --yes install curl tree;\\\n    rm -rf /var/lib/apt/lists"
            ],
        ),
        m.ContainerLayer(
            key="COPY",
            commands=[
                "COPY /some/path /some/path\nCOPY /another/file /yet/another/file"
            ],
        ),
        m.ContainerLayer(
            key="RUN",
            commands=[
                "RUN curl -sLf https://example.com -o /bin/example1 && chmod 755 /bin/example1;\\\n    curl -sLf https://another.example.com -o /bin/example2 && chmod 755 /bin/example2",
                "    ls -la;\\\n    touch /dev/null",
            ],
        ),
        m.ContainerLayer(key="ENV", commands=["ENV A=B C=D"]),
        m.ContainerLayer(key="RUN", commands=["RUN pwd"]),
    ]
