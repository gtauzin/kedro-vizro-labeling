import os

import flask
import vizro.models as vm
from kedro_vizro_labeling.dashboards.components import Markdown
from kedro_vizro_labeling.dashboards.utils import load_markdown_file


def get_home_page():
    home_filename = os.path.join(
        flask.helpers.get_root_path("kedro_vizro_labeling"),
        "dashboards/labeling/pages/home/home.md",
    )
    _, home_text = load_markdown_file(home_filename)

    page = vm.Page(
        title="Home",
        components=[
            vm.Container(
                components=[
                    Markdown(text=home_text, classname="intro-text")
                ],
            )
        ],
    )

    return page
