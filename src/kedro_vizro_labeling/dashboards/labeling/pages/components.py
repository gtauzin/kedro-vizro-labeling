from __future__ import annotations

import logging
from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import (
    Input,
    Output,
    callback,
    dcc,
    html,
)
from kedro_vizro_labeling.dashboards.utils import MAX_N_TABS
from pydantic import BeforeValidator, Field, conlist
from pydantic.json_schema import SkipJsonSchema
from vizro.models._components import Container
from vizro.models._models_utils import _log_call, check_captured_callable_model
from vizro.models._tooltip import coerce_str_to_tooltip


def create_title_description_tooltip(id, title, description):
    description = [
        html.Span("Info", id=f"{id}-icon", className="material-symbols-outlined tooltip-icon"),
        dbc.Tooltip(
            target=f"{id}-icon",
            children=dcc.Markdown(children=description, className="card-text"),
            autohide=False,
        ),
    ]

    return dbc.Label(
        children=[
            html.Span(children=title),
            *description,
        ],
    )

class EventAccordionItem(vm.VizroBaseModel):
    type: Literal["event_accordion"] = "event_accordion"

    title: str = Field(
        default="",
        description="Title of the card. If not provided, the card will not have a title.",
    )
    color: Optional[str] = Field(
        default=None,
        description="""Color of the card. If not provided, the card will use the default color.
        Defaults to `None`.""",
    )
    item_id: str = Field(
        default="",
        description="""Unique identifier for the item. If not provided, a default id will be generated.
        Defaults to `""`.""",
    )
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Card` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/card/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        # variants = {"plain": "link", "filled": "primary", "outlined": "secondary"}

        delete_button = dbc.Button(
            id=f"{self.id}_delete-button",
            children="Delete",
            target="_top",
            style={"background-color": "red"},
            # color="red",
        )

        label_button = dbc.Button(
            id=f"{self.id}_label-button",
            children="Label",
            target="_top",
            style={"background-color": "#ffd23f"},
            # color=variants[self.variant],
        )

        label_type = dbc.Row(
            [
                create_title_description_tooltip(
                    id=f"{self.id}_label-type",
                    title="Type",
                    description="Hey",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id=f"{self.id}_label-type",
                        options=[
                            {"label": "Unknown", "value": "unknown"},
                            {"label": "Switch operation", "value": "switch_operation"},
                            {"label": "Permanent fault", "value": "permanent_fault"},
                            {"label": "Incipient fault", "value": "incipient_fault"},
                            {"label": "External", "value": "external"},
                        ],
                        inline=True,
                    ),
                    width=10,
                ),
            ],
            className="mb-3",
        )

        label_equipment = dbc.Row(
            [
                create_title_description_tooltip(
                    id=f"{self.id}_label-equipment",
                    title="Equipment",
                    description="Hey",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id=f"{self.id}_label-equipment",
                        options=[
                            {"label": "Unknown", "value": "unknown"},
                            {"label": "Cable", "value": "cable"},
                            {"label": "Overhead line", "value": "overhead_line"},
                            {"label": "Transformer", "value": "transformer"},
                            {"label": "Arrester", "value": "arrester"},
                            {"label": "Sensor", "value": "sensor"},
                            {"label": "Not applicable", "value": "na"},
                        ],
                        inline=True,
                    ),
                    width=10,
                ),
            ],
            className="mb-3",
        )

        label_physics = dbc.Row(
            [
                create_title_description_tooltip(
                    id=f"{self.id}_label-physics",
                    title="Physics",
                    description="Hey",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id=f"{self.id}_label-physics",
                        options=[
                            {"label": "Unknown", "value": "unknown"},
                            {"label": "Arcing", "value": "arcing"},
                            {"label": "Lightning", "value": "lightning"},
                            {"label": "Animal", "value": "animal"},
                            {"label": "Tree", "value": "tree"},
                            {"label": "Not applicable", "value": "na"},
                        ],
                        inline=True,
                    ),
                    width=10,
                ),
            ],
            className="mb-3",
        )

        label_confidence = dbc.Col(
            [
                create_title_description_tooltip(
                    id=f"{self.id}_label-confidence",
                    title="Confidence",
                    description="Greater is better.",
                ),
                dbc.Row(
                    dbc.RadioItems(
                        id=f"{self.id}_label-confidence",
                        inline=True,
                        options=[1, 2, 3, 4, 5],
                    ),
                ),
            ],
            width=3,
            className="mb-3",
        )

        label_feedback = dbc.Col(
            [
                create_title_description_tooltip(
                    id=f"{self.id}_label-feedback",
                    title="Feedback",
                    description="Hey",
                ),
                dbc.Row(
                    dcc.Textarea(
                        id=f"{self.id}_label-feedback",
                        placeholder="Brifely describe the event...",
                        style={"width": "95%", "height": 100},
                    ),
                ),
            ],
            className="mb-3",
        )

        label_save = dbc.Button(
            id=f"{self.id}_label-save-button",
            children="Save",
            target="_top",
            # color=variants[self.variant],
        )
        label_cancel = dbc.Button(
            id=f"{self.id}_label-cancel-button",
            children="Cancel",
            target="_top",
            # color=variants[self.variant],
        )

        label_form = dbc.Form(
            id=f"{self.id}_label-form",
            children=[
                label_type,
                label_equipment,
                label_physics,
                dbc.Row(
                    [
                        label_confidence,
                        label_feedback,
                    ],
                    justify="start",
                    className="d-flex my-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            label_cancel, className="text-start"
                        ),
                        dbc.Col(
                            label_save, className="text-end"
                        ),
                    ],
                    justify="between",
                    className="my-3",
                ),
            ],
        )

        label_modal = dbc.Modal(
            id=f"{self.id}_label-modal",
            children=[
                dbc.ModalHeader(
                    children="Label event",
                    close_button=False,
                ),
                dbc.ModalBody(children=label_form),
                # dbc.ModalFooter(children=),
            ],
            is_open=False,
            size="xl",
        )

        @callback(
            Output(f"{self.id}_label-modal", "is_open"),
            Input(f"{self.id}_label-button", "n_clicks"),
            prevent_initial_call=True,
        )
        def toggle_modal(n_clicks):
            return True

        body = html.Div(
            children=[
                html.Div(
                    id=f"{self.id}_device-{i_device}-checklist",
                    children=[
                        dbc.Checklist(
                            options=[f"Device {i_device + 1}"],
                            value=[f"Device {i_device + 1}"],
                            style={"margin-bottom": "5px", 'margin-left': '32px'},
                        ),
                        html.Div(
                            [
                                dbc.Checklist(
                                    id=f"{self.id}_device-{i_device}-channel-checklist",
                                    options=["I1", "I2", "I3"],
                                    value=[],
                                    inline=True,
                                    style={'margin-left': '58px'}
                                ),
                                dbc.Checklist(
                                    options=[label for label in ["A", "B", "C"]],
                                    value=[],
                                    inline=True,
                                    style={'margin-left': '58px'}
                                )
                            ]
                        )
                    ],
                    style={
                        "display": "none",
                        "margin-bottom": "10px"
                    },
                )
            for i_device in range(MAX_N_TABS)
            ]
        )

        content = [
            body,
            label_modal,
            dbc.Row(
                [
                    dbc.Col(
                        delete_button, className="text-start"
                    ),
                    dbc.Col(
                        label_button, className="text-end"
                    ),
                ],
                justify="between",
                className="my-3",
            ),
        ]

        title = self.title
        if self.color is not None:
            status = "invalid"
            icon_class = 'bi-check-circle-fill' if status == 'valid' else 'bi-x-circle-fill'
            icon_color = 'green' if status == 'valid' else 'red'

            title = html.Div(
                [
                    html.Span(
                        className=f'bi {icon_class}',
                        id=f"{self.id}_status-icon",
                        style={
                            'color': icon_color,
                            "marginLeft": "10px",
                        }
                    ),
                    html.Span(
                        style={
                            'backgroundColor': self.color,
                            "width": "40px",
                            "height": "14px",
                            "marginLeft": "10px",
                            "marginRight": "12px",
                            'display': 'inline-block'
                        }
                    ),
                    html.Span(title, style={'flex': '1'}),
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'width': '100%'
                }
            )

        defaults = {
            "id": self.id,
            "children": content,
            "title": title,
            "item_id": self.item_id,
        }

        return dbc.AccordionItem(**(defaults | self.extra))


class EventAccordion(vm.VizroBaseModel):
    type: Literal["event_accordion"] = "event_accordion"

    items: conlist(EventAccordionItem, min_length=1) = Field(
        default_factory=list,
        description="List of items to be displayed in the accordion. Each item is an instance of `EventAccordionItem`.",
    )
    title: str = Field(default="", description="Title to be displayed")
    description: Annotated[
        Optional[vm.Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    always_open: bool = Field(
        default=True,
        description="""If `True`, the accordion will always be open. Defaults to `True`.""",
    )
    start_collapsed: bool = Field(
        default=False,
        description="""If `True`, the accordion will start collapsed. Defaults to `False`.""",
    )
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Card` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/card/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        description = self.description.build().children if self.description else [None]

        items = [
            dbc.Label(
                children=[html.Span(id=f"{self.id}_title", children=self.title), *description], html_for=self.id
            )
        ]
        for item in self.items:
            items.append(item.build())

        defaults = {
            "id": self.id,
            "children": items,
            "always_open": self.always_open,
            "start_collapsed": self.start_collapsed,
            "active_item": [item.item_id for item in self.items if item.item_id],
            "persistence": True,
            "persistence_type": "session",
        }

        return dbc.Accordion(**(defaults | self.extra))
