#! /usr/bin/env python3


import generator.models as m

Components = (
    m.AptGetItemList
    | m.CopyItemList
    | m.CurlItemList
    | m.BashItemList
    | m.EnvItemList
    | m.ArgItemList
    | m.InfoGenerator
)
ComponentsList = list[Components]


def can_combine_group_with_previous(
    prev_key: m.SupportedDockerfileCommands, drv: Components
) -> bool:
    if drv.key != prev_key:
        return False
    return drv.can_be_combined


def group_components_by_key(
    directives: ComponentsList,
) -> list[dict[m.SupportedDockerfileCommands, ComponentsList]]:
    prev_key: m.SupportedDockerfileCommands | None = None
    res: list[dict[m.SupportedDockerfileCommands, ComponentsList]] = []
    current_group: ComponentsList = []

    for drv in directives:
        # First
        if prev_key is None:
            prev_key = drv.key
            current_group.append(drv)
            continue

        if can_combine_group_with_previous(prev_key, drv):
            prev_key = drv.key
            current_group.append(drv)
            continue

        res.append({prev_key: current_group})
        current_group = [drv]
        prev_key = drv.key

    if current_group:
        res.append({prev_key: current_group})

    return res


def grouped_components_to_dockerfile_layers(
    grouped_components: list[dict[m.SupportedDockerfileCommands, ComponentsList]],
) -> list[m.DockerfileLayer]:
    layers = []
    for group in grouped_components:
        for key, items in group.items():
            layers.append(
                m.DockerfileLayer(
                    key=key,
                    commands=[
                        item.to_dockerfile_directive()
                        if idx == 0
                        else f"    {item.to_shortened_dockerfile_directive()}"
                        for idx, item in enumerate(items)
                    ],
                )
            )
    return layers


def directives_to_layers(
    directives: ComponentsList,
) -> list[m.DockerfileLayer]:
    return grouped_components_to_dockerfile_layers(group_components_by_key(directives))
