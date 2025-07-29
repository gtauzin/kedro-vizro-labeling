import os

import vizro.models as vm
from kedro_vizro_labeling.dashboards.components import CustomDashboard
from kedro_vizro_labeling.dashboards.labeling.data import load_kedro_datasets
from kedro_vizro_labeling.dashboards.labeling.pages.home.page import get_home_page
from kedro_vizro_labeling.dashboards.labeling.pages.label.page import get_label_page
from vizro import Vizro


KEDRO_ENV = os.getenv("KEDRO_ENV", "base")

load_kedro_datasets(dataset_names=["measurement_list", "measurement_partition"], env=KEDRO_ENV)

vizro_instance = Vizro(
    external_scripts=[
        "https://cdn.jsdelivr.net/npm/lodash/lodash.min.js",
        "https://unpkg.com/virtual-webgl@1.0.6/src/virtual-webgl.js",
        "https://raw.githubusercontent.com/predict-idlab/plotly-resampler/refs/heads/main/plotly_resampler/figure_resampler/assets/coarse_fine.js",
    ],
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
    ],
)

dash_app = vizro_instance.dash

home_page = get_home_page()
label_page = get_label_page()

vm.Page.add_type("controls", vm.Button)


dashboard = CustomDashboard(
    title="Anomalous event labeling dashboard",
    pages=[
        home_page,
        label_page,
    ],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Home", pages=[home_page.id], icon="home"),
                vm.NavLink(label="Label events", pages=[label_page.id], icon="shoppingmode"),
            ],
        ),
    ),
)

if __name__ == "__main__":
    PROFILE_DIR = os.getenv("PROFILE", None)
    if PROFILE_DIR is not None:
        from werkzeug.middleware.profiler import ProfilerMiddleware

        dash_app.server.config["PROFILE"] = True
        dash_app.server.wsgi_app = ProfilerMiddleware(
            dash_app.server.wsgi_app,
            sort_by=("cumtime", "tottime"),
            restrictions=[50],
            stream=None,
            profile_dir=PROFILE_DIR,
        )

    app = vizro_instance.build(dashboard)
    app.run(debug=False)
