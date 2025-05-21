import os

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash_auth.oidc_auth import OIDCAuth
from flask_caching import Cache
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture

from kedro_vizro_labeling.dashboards.components import (
    DropdownMenu,
    DropdownMenuItem,
    Modal,
)
from kedro_vizro_labeling.dashboards.protected import (
    ProtectedAction,
    ProtectedDashboard,
    ProtectedGraph,
    ProtectedPage,
    forbidden_figure,
)
from kedro_vizro_labeling.dashboards.protected_iris.data import load_kedro_datasets


def get_openid_config_url() -> str:
    # Swagger configuration (via openapi spec)
    url = os.environ.get(
        "OIDC_URL",
        "http://localhost:8080/realms/test-realm/.well-known/openid-configuration",
    )
    if ".well-known/openid-configuration" not in url:
        url = url.rstrip("/") + "/.well-known/openid-configuration"
    return url


openid_connect_url = get_openid_config_url()
client_id = os.environ.get("OIDC_CLIENT_ID", "vizro-app")
scope = os.environ.get("OIDC_SCOPES", "openid email profile")
secret_key = os.environ.get("SECRET_KEY", "vizro-dashboard-secret-key")

data_manager.cache = Cache(
    config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT": 600}
)


load_kedro_datasets(env="base", dataset_names=["iris"])

@capture("action")
def show_plot():
    df = data_manager["iris"].load()
    return px.histogram(df, x="sepal_width", color="species")


@capture("graph")
def forbidden_graph(data_frame):
    return forbidden_figure

vm.Page.add_type("controls", vm.Button)
vm.Page.add_type("components", Modal)


page_1 = vm.Page(
    title="User page",
    components=[
        vm.Graph(id="scatter-chart", figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),
        ProtectedGraph(
            id="protected-admin-hist-chart",
            figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species"),
            groups=["Admin"],
            groups_key="roles",
        ),
        vm.Graph(
            id="admin-hist-chart",
            figure=forbidden_graph(pd.DataFrame()),
        ),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
        vm.Button(
            id="admin-button",
            text="Show admin histogram",
            actions=[
                ProtectedAction(
                    function=show_plot(),
                    outputs=[
                        "admin-hist-chart.figure",
                    ],
                    groups=["Admin"],
                    groups_key="roles",
                ),
            ],
        ),
    ],
)

page_2 = ProtectedPage(
    title="Admin page",
    components=[
        vm.Graph(id="hist-chart", figure=px.histogram("iris", x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
    groups=["Admin"],
    groups_key="roles",
)

dashboard = ProtectedDashboard(
    pages=[page_1, page_2],
    title="Iris Dashboard",
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


# We could use BasicAuth for demonstrating the auth setup
# However, it is not optimal as it does not support things like logout
# https://stackoverflow.com/questions/233507/how-to-log-out-user-from-web-site-using-basic-authentication
#
# USER_PWD = {
#     "user1": "user1",
#     "admin1": "admin1",
# }
# BasicAuth(
#     dash_app,
#     USER_PWD,
#     user_groups={"user1": ["Viewer"], "admin1": ["Admin"]},
#     secret_key="Test!",
# )

# In practice, we would most use something like OIDCAuth
auth = OIDCAuth(
    dash_app,
    secret_key=secret_key,
    login_route="/oidc/<idp>/login",
    logout_route="/oidc/logout",
    callback_route="/oidc/<idp>/callback",
    idp_selection_route=None,
)

auth.register_provider(
    "idp",
    client_id=client_id,
    server_metadata_url=openid_connect_url,
    client_kwargs={
        "scope": scope,
        "code_challenge_method": "S256",
        "token_endpoint_auth_method": "client_secret_post",
    },
)

if __name__ == "__main__":
    vizro_app.run(debug=False)
