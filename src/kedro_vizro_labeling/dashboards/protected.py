import logging
from typing import Optional

import plotly.graph_objs as go
import vizro.models as vm
from dash import html, no_update, set_props
from dash_auth.group_protection import CheckType, protected
from flask import session
from vizro.models._models_utils import _log_call

from kedro_vizro_labeling.dashboards.components import (
    DropdownMenu,
    DropdownMenuItem,
    Modal,
)

logger = logging.getLogger(__name__)


forbidden_figure = go.Figure(
    layout={
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [
            {
                "text": "You don't have permission to see this graph",
                "xref": "paper",
                "yref": "paper",
            }
        ],
    }
)

class ProtectedGraph(vm.Graph):
    """Custom Vizro Graph that enables authorization and group-based access control.

    Args:
        type (Literal["graph"]): Defaults to `"graph"`.
        figure (CapturedCallable): Function that returns a graph.
            See `CapturedCallable`][vizro.models.types.CapturedCallable].
        title (str): Title of the `Graph`. Defaults to `""`.
        header (str): Markdown text positioned below the `Graph.title`. Follows the CommonMark specification.
            Ideal for adding supplementary information such as subtitles, descriptions, or additional context.
            Defaults to `""`.
        footer (str): Markdown text positioned below the `Graph`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
        groups (Optional[list[str]]): List of authorized user groups. If no groups are passed, checks only whether the user is
            authenticated. Defaults to `None`.
        groups_key (str): Groups key in the user data saved in the Flask session e.g.
            ``session["user"] == {"email": "a.b@mail.com", "groups": ["admin"]}`` Defaults to `"roles"`.
        groups_str_split (Optional[str]): Used to split groups if provided as a string. Defaults to `None`.
        check_type (Literal["one_of", "all_of", "none_of"]): Type of check to perform. Either "one_of", "all_of" or
            "none_of". Defaults to `"one_of"`.
    """

    groups: Optional[list[str]] = None
    groups_key: str = "roles"
    groups_str_split: Optional[str] = None
    check_type: CheckType = "one_of"

    def __call__(self, **kwargs):
        return protected(
            unauthenticated_output=forbidden_figure,
            missing_permissions_output=forbidden_figure,
            groups=self.groups,
            groups_key=self.groups_key,
            groups_str_split=self.groups_str_split,
            check_type=self.check_type,
        )(super().__call__)()


class ProtectedAction(vm.Action):
    """Custom Vizro Action that enables authorization and group-based access control.

    Args:
        function (CapturedCallable): Action function.
        inputs (list[_DotSeparatedStr]): List of inputs provided to the action function, each specified as
            `<component_id>.<property>`. Defaults to `[]`.
        outputs (Union[list[_DotSeparatedStr], dict[str, _DotSeparatedStr]]): List or dictionary of outputs modified by
            the action function, where each output needs to be specified as `<component_id>.<property>`.
            Defaults to `[]`.
        groups (Optional[list[str]]): List of authorized user groups. If no groups are passed, checks only whether the user is
            authenticated. Defaults to `None`.
        groups_key (str): Groups key in the user data saved in the Flask session e.g.
            ``session["user"] == {"email": "a.b@mail.com", "groups": ["admin"]}`` Defaults to `"roles"`.
        groups_str_split (Optional[str]): Used to split groups if provided as a string. Defaults to `None`.
        check_type (Literal["one_of", "all_of", "none_of"]): Type of check to perform. Either "one_of", "all_of" or
            "none_of". Defaults to `"one_of"`.
    """

    groups: Optional[list[str]] = None
    groups_key: str = "roles"
    groups_str_split: Optional[str] = None
    check_type: CheckType = "one_of"

    def _action_callback_function(self, *args, **kwargs):
        n_outputs = len(self.outputs)

        def unauthenticated_output():
            set_props("unauthenticated-modal", {"is_open": True})
            return (no_update, ) * n_outputs

        def missing_permissions_output():
            set_props("missing-permission-modal", {"is_open": True})
            return (no_update, ) * n_outputs

        return protected(
            unauthenticated_output=unauthenticated_output,
            missing_permissions_output=missing_permissions_output,
            groups=self.groups,
            groups_key=self.groups_key,
            groups_str_split=self.groups_str_split,
            check_type=self.check_type,
        )(super()._action_callback_function)(*args, **kwargs)


class ProtectedPage(vm.Page):
    """Custom Vizro Page that enables authorization and group-based access control.

    Args:
        components (List[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        description (str): Description for meta tags.
        layout (Layout): Layout to place components in. Defaults to `None`.
        controls (List[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        path (str): Path to navigate to page. Defaults to `""`.
        groups (Optional[list[str]]): List of authorized user groups. If no groups are passed, checks only whether the user is
            authenticated. Defaults to `None`.
        groups_key (str): Groups key in the user data saved in the Flask session e.g.
            ``session["user"] == {"email": "a.b@mail.com", "groups": ["admin"]}`` Defaults to `"roles"`.
        groups_str_split (Optional[str]): Used to split groups if provided as a string. Defaults to `None`.
        check_type (Literal["one_of", "all_of", "none_of"]): Type of check to perform. Either "one_of", "all_of" or
            "none_of". Defaults to `"one_of"`.
    """

    groups: Optional[list[str]] = None
    groups_key: str = "roles"
    groups_str_split: Optional[str] = None
    check_type: CheckType = "one_of"


class ProtectedDashboard(vm.Dashboard):
    """Custom Vizro Dashboard that enables authorization and group-based access control.

    Args:
        pages (list[Page]): See [`Page`][vizro.models.Page].
        theme (Literal["vizro_dark", "vizro_light"]): Layout theme to be applied across dashboard.
            Defaults to `vizro_dark`.
        navigation (Navigation): See [`Navigation`][vizro.models.Navigation]. Defaults to `None`.
        title (str): Dashboard title to appear on every page on top left-side. Defaults to `""`.

    """

    @staticmethod
    def _make_user_menu():
        return DropdownMenu(
            label="Settings",
            items=[
                DropdownMenuItem(
                    text="Sign in with another account",
                    # href="",
                ),
                DropdownMenuItem(
                    text="Logout",
                    href="/logout",
                ),
            ],
        )

    @_log_call
    def build(self):
        super_build_obj = super().build()

        unauthenticated_modal = Modal(
            id="unauthenticated-modal",
            header=vm.Container(components=[vm.Text(text="Unauthenticated.")]),
            body=vm.Container(components=[vm.Text(text="You are not authorized to perform this action. Please sign in.")]),
            footer=vm.Container(components=[vm.Button(text="Sign in")]),
        )

        missing_permission_modal = Modal(
            id="missing-permission-modal",
            header=vm.Container(components=[vm.Text(text="Missing permissions.")]),
            body=vm.Container(
                components=[
                    vm.Text(
                        text="You do not have the required permissions to perform this action. Sign in with another account."
                    )
                ]
            ),
            footer=vm.Container(components=[vm.Button(text="Sign in")]),
        )

        super_build_obj.children.extend(
            [
                unauthenticated_modal.build(),
                missing_permission_modal.build(),
            ]
        )

        return super_build_obj

    def _make_page_layout(self, page: vm.Page, **kwargs):
        if isinstance(page, ProtectedPage):
            return protected(
                unauthenticated_output=self._make_page_404_layout,
                missing_permissions_output=self._make_page_404_layout,
                groups=page.groups,
                groups_key=page.groups_key,
                groups_str_split=page.groups_str_split,
                check_type=page.check_type,
            )(self._make_protected_page_layout)(page, **kwargs)

        return self._make_protected_page_layout(page, **kwargs)

    def _make_protected_page_layout(self, *args, **kwargs):
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

        additional_build_obj.extend(
            [
                self._make_user_menu().build(),
            ]
        )

        super_build_obj["settings"].children = [
            theme_switch.children,
            *additional_build_obj,
        ]
        return super_build_obj
