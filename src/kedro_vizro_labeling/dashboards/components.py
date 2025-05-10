import logging
from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import get_relative_path, html
from flask import session
from pydantic import Field, conlist
from pydantic.json_schema import SkipJsonSchema
from vizro.models._components import Container
from vizro.models._models_utils import _log_call

logger = logging.getLogger(__name__)


class Modal(vm.VizroBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["modal"]): Defaults to `"modal"`.
        header (Optional[Container]): Container to be displayed on the modal's header. Defaults to `None`.
        body (Optional[Container]): Container to be displayed on the modal's body. Defaults to `None`.
        footer (Optional[Container]): Container to be displayed on the modal's footer. Defaults to `None`.
        is_open (bool): Whether modal is currently open. Default to ``False``.
        header_close_button (bool): Add a close button to the header that can be used to close the modal. Defaults to
            ``True``.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Modal` and overwrite
            any defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the
            [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/modal/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["modal"] = "modal"
    header: Container | None = Field(default=None, description="Container to be displayed on the modal's header.")
    body: Container | None = Field(default=None, description="Container to be displayed on the modal's body.")
    footer: Container | None = Field(default=None, description="Container to be displayed on the modal's footer.")
    is_open: bool = Field(default=False, description="Whether modal is currently open.")
    header_close_button: bool = Field(
        default=True, description="Add a close button to the header that can be used to close the modal."
    )
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Modal` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/modal/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        defaults = {
            "id": self.id,
            "children": [
                dbc.ModalHeader(
                    children=self.header.build() if self.header is not None else None,
                    close_button=self.header_close_button,
                ),
                dbc.ModalBody(children=self.body.build() if self.body is not None else None),
                dbc.ModalFooter(children=self.footer.build() if self.footer is not None else None),
            ],
            "is_open": self.is_open,
        }

        return dbc.Modal(**(defaults | self.extra))


class DropdownMenuItem(vm.VizroBaseModel):
    """Dropdown menu item made to be collected into a `DropdownMenu`.

    Args:
        type (Literal["dropdown_menu_item"]): Defaults to `"dropdown_menu_item"`.
        text (str): Text to be displayed on item. Defaults to `"Click me!"`.
        href (str): URL (relative or absolute) to navigate to. Defaults to `""`.
        actions (list[ActionType]): See [`ActionType`][vizro.models.types.ActionType]. Defaults to `[]`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.DropdownMenuItem` and overwrite
            any defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the
            [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/dropdown_menu/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["dropdown_menu_item"] = "dropdown_menu_item"
    text: str = Field(default="Click me!", description="Text to be displayed on button.")
    href: str = Field(default="", description="URL (relative or absolute) to navigate to.")
    # actions: Annotated[
    #     list[ActionType],
    #     AfterValidator(_action_validator_factory("n_clicks")),
    #     PlainSerializer(lambda x: x[0].actions),
    #     Field(default=[]),
    # ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.DropdownMenuItem` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/dropdown_menu/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        defaults = {
            "id": self.id,
            "children": self.text,
            "href": get_relative_path(self.href) if self.href.startswith("/") else self.href,
            "target": "_top",
        }

        return dbc.DropdownMenuItem(**(defaults | self.extra))


class DropdownMenu(vm.VizroBaseModel):
    """Dropdown menu to organise lists of links and buttons into a toggleable overlay.

    Args:
        type (Literal["dropdown_menu"]): Defaults to `"dropdown_menu"`.
        tabs (list[Container]): See [`Container`][vizro.models.Container].
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.DropdownMenu` and overwrite
            any defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the
            [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/dropdown_menu/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
    """

    type: Literal["dropdown_menu"] = "dropdown_menu"
    label: str = "Menu"
    items: conlist(DropdownMenuItem, min_length=1)  # type: ignore[valid-type]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.DropdownMenu` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/dropdown_menu/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        defaults = {
            "id": self.id,
            "label": self.label,
            "children": [item.build() for item in self.items],
        }
        return dbc.DropdownMenu(**(defaults | self.extra))


class CustomDashboard(vm.Dashboard):
    """Custom Vizro Dashboard that enables cross-page stores.

    Args:
        pages (list[Page]): See [`Page`][vizro.models.Page].
        theme (Literal["vizro_dark", "vizro_light"]): Layout theme to be applied across dashboard.
            Defaults to `vizro_dark`.
        navigation (Navigation): See [`Navigation`][vizro.models.Navigation]. Defaults to `None`.
        title (str): Dashboard title to appear on every page on top left-side. Defaults to `""`.

    """

    type: Literal["custom_dashboard"] = "custom_dashboard"
    settings_menu: DropdownMenu | None = None
    unauthentificated_modal: Modal | None = None
    missing_permission_modal: Modal | None = None

    def _make_page_layout(self, *args, **kwargs):
        super_build_obj = super()._make_page_layout(*args, **kwargs)
        # We access the container with id="settings", where the theme switch is placed and add the H4.
        theme_switch = super_build_obj["settings"]

        if "user" in session:
            additional_build_obj = [
                html.H4(f"Hello, {session['user']['email']}!", style={"margin-bottom": "0"}),
            ]
        else:
            additional_build_obj = [
                html.H4("Hello!", style={"margin-bottom": "0"}),
            ]

        if self.settings_menu is not None:
            additional_build_obj.append(self.settings_menu.build())
        if self.unauthentificated_modal is not None:
            additional_build_obj.append(self.unauthentificated_modal.build())
        if self.missing_permission_modal is not None:
            additional_build_obj.append(self.missing_permission_modal.build())

        super_build_obj["settings"].children = [
            theme_switch.children,
            *additional_build_obj,
        ]
        return super_build_obj
