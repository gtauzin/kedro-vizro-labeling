import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash_auth import BasicAuth, protected
from vizro import Vizro
from vizro.models.types import capture

from kedro_vizro_labeling.dashboards.components import (
    CustomDashboard,
    DropdownMenu,
    DropdownMenuItem,
    Modal,
)
from kedro_vizro_labeling.dashboards.protected_action import ProtectedAction
from kedro_vizro_labeling.dashboards.iris.data_manager import load_kedro_datasets

data_manager = load_kedro_datasets(env="base", dataset_names=["iris"])


@capture("action")
def show_plot_protected():
    def func():
        df = data_manager["iris"].load()
        return px.histogram(df, x="sepal_width", color="species"), False, False

    unauthenticated_output = (
        px.histogram(pd.DataFrame(columns=["sepal_width", "species"]), x="sepal_width", color="species"),
        True,
        False,
    )
    missing_permission_output = (
        px.histogram(pd.DataFrame(columns=["sepal_width", "species"]), x="sepal_width", color="species"),
        False,
        True,
    )

    return protected(
        unauthenticated_output=unauthenticated_output,
        missing_permissions_output=missing_permission_output,
        groups=["Admin"],
    )(func)()


@capture("action")
def show_plot():
    df = data_manager["iris"].load()
    return px.histogram(df, x="sepal_width", color="species"), False


vm.Page.add_type("controls", vm.Button)
vm.Page.add_type("components", Modal)
# TODO: This does not work...
# vm.Button.add_type("actions", ProtectedAction)

page_1 = vm.Page(
    title="User page",
    components=[
        vm.Graph(id="scatter-chart", figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),
        vm.Graph(
            id="admin-hist-chart",
            figure=px.histogram(pd.DataFrame(columns=["sepal_width", "species"]), x="sepal_width", color="species"),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
        vm.Button(
            id="admin-button",
            text="Show histogram",
            actions=[
                vm.Action(
                    function=show_plot_protected(),
                    outputs=[
                        "admin-hist-chart.figure",
                        "unauthentificated-modal.is_open",
                        "missing-permission-modal.is_open",
                    ],
                ),
                # TODO: Eventually replace the above with this code
                # ProtectedAction(
                #     function=show_plot(),
                #     outputs=[
                #         "admin-hist-chart.figure",
                #         "unauthentificated-modal.is_open",
                #         "missing-permission-modal.is_open",
                #     ],
                #     groups=["Admin"],
                # ),
            ],
        ),
    ],
)

page_2 = vm.Page(
    title="Admin page",
    components=[
        vm.Graph(id="hist-chart", figure=px.histogram("iris", x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)

dashboard = CustomDashboard(
    pages=[page_1, page_2],
    title="Iris Dashboard",
    settings_menu=DropdownMenu(
        label="Settings",
        items=[
            DropdownMenuItem(
                text="Sign in with another account",
                # href="",
            ),
            DropdownMenuItem(
                text="Logout",
                # href="",
            ),
        ],
    ),
    missing_permission_modal=Modal(
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
    ),
    unauthentificated_modal=Modal(
        id="unauthentificated-modal",
        header=vm.Container(components=[vm.Text(text="unauthentificated.")]),
        body=vm.Container(components=[vm.Text(text="You are not authorized to perform this action. Please sign in.")]),
        footer=vm.Container(components=[vm.Button(text="Sign in")]),
    ),
)

app_name = "iris"

# Build the Vizro app as a Flask app
vizro_app = Vizro(
    # TODO: This breaks everything...
    # name=app_name,
    # assets_folder=f"src/kedro_vizro_labeling/dashboards/{app_name}/assets",
    # requests_pathname_prefix=f"/{app_name}/",
).build(dashboard)
dash_app = vizro_app.dash


# Here we use BasicAuth for demonstrating the auth setup
# However, it is not optimal as it does not support things like logout
# https://stackoverflow.com/questions/233507/how-to-log-out-user-from-web-site-using-basic-authentication


USER_PWD = {
    "user1": "user1",
    "admin1": "admin1",
}
BasicAuth(
    dash_app,
    USER_PWD,
    user_groups={"user1": ["Viewer"], "admin_1": ["Viewer", "Admin"]},
    secret_key="Test!",
)

# In practice, we would most use something like OIDCAuth
# from dash_auth import OIDCAuth
# auth = OIDCAuth(
#     dash_app,
#     secret_key=secret_key,
#     ...
# )

# auth.register_provider(
#     ...
# )

flask_app = dash_app.server

if __name__ == "__main__":
    vizro_app.run(debug=False)
