import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash_auth import BasicAuth
from vizro import Vizro
from vizro.models.types import capture

from kedro_vizro_labeling.dashboards.components import (
    CustomDashboard,
    DropdownMenu,
    DropdownMenuItem,
    Modal,
)
from kedro_vizro_labeling.dashboards.iris import data_manager
from kedro_vizro_labeling.dashboards.iris.data_manager import load_kedro_datasets
from kedro_vizro_labeling.dashboards.protected_action import ProtectedAction

# AM comment: no need to set to data_manager variable.
load_kedro_datasets(env="base", dataset_names=["iris"])



@capture("action")
def show_plot():
    df = data_manager["iris"].load()
    return px.histogram(df, x="sepal_width", color="species")


vm.Page.add_type("controls", vm.Button)
vm.Page.add_type("components", Modal)

# TODO: Remove once vizro actions are more stable
from pydantic import Tag
from typing import Annotated
# TODO: this should be "protected_action" but there was a problem with `add_type`
ProtectedAction = Annotated[ProtectedAction, Tag("action")]

vm.Button.add_type("actions", ProtectedAction)

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
                ProtectedAction(
                    # AM question: is this actually how you want the flow to work or is it just a workaround? Compared
                    # to my example where the plot is protected by the @capture("graph") and there's no button to
                    # enable it.
                    function=show_plot(),
                    # AM comment: FYI soon you'll be able to do just outputs=["admin-hist-chart"].
                    outputs=[
                        "admin-hist-chart.figure",
                    ],
                    groups=["Admin"],
                    # AM question: it feels like these fields would probably be the same for every single
                    # ProtectedAction instance in the app?
                    unauthenticated_modal_id="unauthenticated-modal",
                    missing_permission_modal_id="missing-permission-modal",
                ),
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
    user_menu=DropdownMenu(
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
    unauthenticated_modal=Modal(
        id="unauthenticated-modal",
        header=vm.Container(components=[vm.Text(text="Unauthenticated.")]),
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
    user_groups={"user1": ["Viewer"], "admin1": ["Admin"]},
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
