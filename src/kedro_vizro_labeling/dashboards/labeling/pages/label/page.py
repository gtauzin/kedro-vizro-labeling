import pandas as pd
import vizro.models as vm

from kedro_vizro_labeling.dashboards.actions import (
    replot,
    toggle_tabs,
    update_dragmode,
    update_legend_checklist_value,
    update_plot,
    zoom_in,
    zoom_out,
)
from kedro_vizro_labeling.dashboards.components import Card, FlexContainer, IdTabs, LegendChecklist, Store, TabsGraph, TabStore
from kedro_vizro_labeling.dashboards.graphs import plot_empty
from kedro_vizro_labeling.dashboards.labeling.pages.label.actions import (
    create_tabs,  # TODO: Merge with general action
    get_new_event_group,
    process_selection,
    submit_label,
    update_tab_titles,
)
from kedro_vizro_labeling.dashboards.labeling.pages.label.components import EventAccordion, EventAccordionItem
from kedro_vizro_labeling.dashboards.labeling.pages.label.utils import MAX_N_EVENTS, event_colors
from kedro_vizro_labeling.dashboards.utils import MAX_N_TABS, get_checklist_options, get_checklist_value

vm.Page.add_type("components", FlexContainer)
vm.Container.add_type("components", Store)
vm.Page.add_type("controls", vm.Container)
vm.Page.add_type("controls", vm.Dropdown)
vm.Page.add_type("controls", vm.Button)
vm.Page.add_type("controls", EventAccordion)
vm.Container.add_type("components", vm.Container)
vm.Container.add_type("components", vm.Dropdown)
vm.Container.add_type("components", vm.Button)
vm.Container.add_type("components", EventAccordion)


def get_label_page():
    page = vm.Page(
        title="Event",
        layout=vm.Flex(),
        components=[
            FlexContainer(
                title="",
                components=[
                    IdTabs(
                        id="label-tabs",
                        tabs=[
                            FlexContainer(
                                title="",
                                components=[
                                    TabStore(
                                        id=f"label-tab-{i_tab}",
                                    )
                                ],
                            )
                            for i_tab in range(MAX_N_TABS)
                        ],
                        actions=[
                            vm.Action(
                                function=toggle_tabs(),
                                inputs=[
                                    "label-tabs.active_tab",
                                    "label-name-dropdown.value",
                                ]
                                + [f"label-tab-{i_tab}_legend_value_store.data" for i_tab in range(MAX_N_TABS)]
                                + [f"label-tab-{i_tab}_relayout_data_store.data" for i_tab in range(MAX_N_TABS)]
                                + ["label-tabs-graph_selection-range-store.data"],
                                outputs=[
                                    "label-tabs-graph.figure",
                                    "label-legend-checklist.value",
                                    "label-legend-checklist.options",
                                    "label-legend-checklist_all_values_store.data",
                                ],
                            )
                        ],
                    ),
                    TabsGraph(
                        id="label-tabs-graph",
                        figure=plot_empty(pd.DataFrame()),
                        stores=[
                            Store(
                                id="label-tabs-graph_selection-range-store",
                                storage_type="session",
                                data=[],
                            )
                        ],
                        relayout_actions=[
                            vm.Action(
                                function=update_plot(),
                                inputs=[
                                    "label-tabs.active_tab",
                                    "label-name-dropdown.value",
                                    "label-tabs-graph.relayoutData",
                                ]
                                + [f"label-tab-{i_tab}_relayout_data_store.data" for i_tab in range(MAX_N_TABS)]
                                + ["label-tabs-graph_selection-range-store.data"],
                                outputs=[
                                    "label-tabs-graph.figure",
                                ]
                                + [f"label-tab-{i_tab}_relayout_data_store.data" for i_tab in range(MAX_N_TABS)],
                            )
                        ],
                        select_actions=[
                            vm.Action(
                                function=process_selection(),
                                inputs=[
                                    "label-tabs-graph.selectedData",
                                    "label-tabs-graph.figure",
                                    "label-tabs-graph_selection-range-store.data",
                                ],
                                outputs=[
                                    "label-tabs-graph.figure",
                                    "label-tabs-graph_selection-range-store.data",
                                    "label-events-accordion.style",
                                ] + [
                                    f"label-event-item-{i_event}.style"
                                    for i_event in range(MAX_N_EVENTS)
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
        controls=[
            vm.Container(
                layout=vm.Flex(),
                components=[
                    vm.Container(
                        layout=vm.Grid(grid=[[0, 1]]),
                        components=[
                            vm.Button(
                                id="label-new-button",
                                text="New event",
                                actions=[
                                    vm.Action(
                                        function=get_new_event_group(),
                                        inputs=["label-new-button.n_clicks"],
                                        outputs=[
                                            "label-name-dropdown.options",
                                            "label-name-dropdown.value",
                                        ],
                                    ),
                                    vm.Action(
                                        function=create_tabs(),
                                        inputs=[
                                            "label-name-dropdown.value",
                                        ],
                                        outputs=[
                                            "label-tabs.active_tab",
                                            "label-tabs-graph.figure",
                                            "label-tab-0_legend_value_store.data",
                                            "label-legend-checklist.value",
                                            "label-legend-checklist.options",
                                            "label-legend.style",
                                            "label-buttons.style",
                                        ]
                                        + [f"label-tab-{i_tab}_relayout_data_store.data" for i_tab in range(MAX_N_TABS)
                                        ] + [
                                            f"label-event-item-{i_event}_device-{i_device}-checklist.style"
                                            for i_event in range(MAX_N_EVENTS)
                                            for i_device in range(MAX_N_TABS)
                                        ] + [
                                            f"label-event-item-{i_event}_device-{i_device}-channel-checklist.options"
                                            for i_event in range(MAX_N_EVENTS)
                                            for i_device in range(MAX_N_TABS)
                                        ],
                                    ),
                                    vm.Action(
                                        function=update_tab_titles(),
                                        inputs=[
                                            "label-name-dropdown.value",
                                        ],
                                        outputs=[f"label-tabs-{i_tab}.label" for i_tab in range(MAX_N_TABS)],
                                    ),
                                ],
                                extra={
                                    "style": {
                                        "padding": "8px 16px",
                                        "font-size": "14px",
                                        "cursor": "pointer",
                                        "text-align": "center",
                                        "min-width": "200px",
                                        "height": "40px",
                                    },
                                },
                            ),
                            vm.Button(
                                id="submit-button",
                                text="Submit",
                                actions=[
                                    vm.Action(
                                        function=submit_label(),
                                        inputs=[
                                            "selection-range-list.data",
                                            "selection-popup-store.data",
                                        ],
                                        outputs=[
                                            "final-label.data",
                                        ],
                                    ),
                                ],
                                extra={
                                    "style": {
                                        "padding": "8px 16px",
                                        "font-size": "14px",
                                        "cursor": "pointer",
                                        "text-align": "center",
                                        "min-width": "200px",
                                        "height": "40px",
                                        "background-color": "red",
                                    },
                                },
                            ),
                        ],
                        extra={"style": {"height": "15px"}},
                    ),
                    vm.Dropdown(
                        id="label-name-dropdown",
                        value=[],
                        multi=True,
                        options=[],
                        actions=[],
                        extra={"style": {"display": "none"}},
                    ),
                    Card(
                        title="Context",
                        description="""
                            Information related to the context in which the event was recorded.
                        """,
                        text="""
                        - Weather:
                            - Condition: Fair
                            - Temperature: 28 °C / 82 °F
                            - Humidity: 62%
                        - Switching operation: None
                        - Equipment: Fully underground section
                        """,
                        extra={"style": {"height": "210px", "min_height": "150px"}},
                    ),
                    vm.Container(
                        id="label-legend",
                        components=[
                            LegendChecklist(
                                id="label-legend-checklist",
                                title="Legend",
                                description="""
                                    Select the channels you want to visualize.

                                    Click on the `Replot` button to apply the changes.
                                """,
                                options=get_checklist_options(),
                                value=get_checklist_value(),
                                extra=dict(inline=True),
                                actions=[
                                    vm.Action(
                                        function=update_legend_checklist_value(),
                                        inputs=[
                                            "label-legend-checklist.value",
                                            "label-legend-checklist_all_values_store.data",
                                            "label-legend-checklist.options",
                                            "label-tabs.active_tab",
                                        ]
                                        + [f"label-tab-{i_tab}_legend_value_store.data" for i_tab in range(MAX_N_TABS)],
                                        outputs=[f"label-tab-{i_tab}_legend_value_store.data" for i_tab in range(MAX_N_TABS)]
                                        + [
                                            "label-legend-checklist.value",
                                            "label-legend-checklist_all_values_store.data",
                                        ],
                                    )
                                ],
                            ),
                        ],
                        extra=dict(
                            style={"display": "none"},
                        ),
                    ),
                    vm.Container(
                        id="label-buttons",
                        title="",
                        layout=vm.Grid(grid=[[0, 1, 2, 3]]),
                        components=[
                            vm.Button(
                                id="label-autoscale-button",
                                text="Replot",
                                actions=[
                                    vm.Action(
                                        function=replot(),
                                        inputs=[
                                            "label-name-dropdown.value",
                                            "label-legend-checklist.value",
                                            "label-tabs.active_tab",
                                        ]
                                        + [f"label-tab-{i_tab}_legend_value_store.data" for i_tab in range(MAX_N_TABS)]
                                        + ["label-tabs-graph_selection-range-store.data"],
                                        outputs=[
                                            "label-tabs-graph.figure",
                                        ]
                                        + [f"label-tab-{i_tab}_legend_value_store.data" for i_tab in range(MAX_N_TABS)],
                                    ),
                                ],
                            ),
                            vm.Button(
                                id="label-zoom-button",
                                text="Zoom",
                                actions=[
                                    vm.Action(
                                        function=update_dragmode(dragmode="zoom"),
                                        inputs=["label-tabs-graph.figure"],
                                        outputs=["label-tabs-graph.figure"],
                                    ),
                                ],
                            ),
                            vm.Button(
                                id="label-pan-button",
                                text="Pan",
                                actions=[
                                    vm.Action(
                                        function=update_dragmode(dragmode="pan"),
                                        inputs=["label-tabs-graph.figure"],
                                        outputs=["label-tabs-graph.figure"],
                                    ),
                                ],
                            ),
                            vm.Button(
                                id="label-select-button",
                                text="Select",
                                actions=[
                                    vm.Action(
                                        function=update_dragmode(dragmode="select"),
                                        inputs=["label-tabs-graph.figure"],
                                        outputs=["label-tabs-graph.figure"],
                                    ),
                                ],
                            ),
                        ],
                        extra=dict(
                            style={"display": "none"},
                        ),
                    ),
                    vm.Container(
                        components=[
                            vm.Button(
                                id="zoomin-button",
                                text="+",
                                actions=[
                                    vm.Action(
                                        function=zoom_in(),
                                        inputs=["label-tabs-graph.figure"],
                                        outputs=["label-tabs-graph.figure"],
                                    ),
                                ],
                            ),
                            vm.Button(
                                id="zoomout-button",
                                text="-",
                                actions=[
                                    vm.Action(
                                        function=zoom_out(),
                                        inputs=["label-tabs-graph.figure"],
                                        outputs=["label-tabs-graph.figure"],
                                    ),
                                ],
                            ),
                        ],
                        extra=dict(
                            style={"display": "none"},
                        ),
                    ),
                    EventAccordion(
                        id="label-events-accordion",
                        title="Events",
                        description="""
                            Once an event is selected on the graph, select the devices that recorded it.

                            Click on the `Label` to open a menu and select the event label.
                        """,
                        items=[
                            EventAccordionItem(
                                id=f"label-event-item-{i_event}",
                                item_id=f"item-{i_event}",
                                title=f"Event #{i_event + 1}",
                                color=event_colors[i_event % len(event_colors)],
                                extra={
                                    "style": {"display": "none"},
                                },
                            )
                            for i_event in range(MAX_N_EVENTS)
                        ],
                        extra={
                            "style": {"display": "none"},
                        },
                    ),
                ],
            ),
        ],
    )

    return page
