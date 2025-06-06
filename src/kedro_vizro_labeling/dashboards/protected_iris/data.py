from pathlib import Path

from kedro.utils import _find_kedro_project
from vizro.integrations import kedro as kedro_integration


def load_kedro_datasets(env, dataset_names=None):
    from vizro.managers import data_manager

    project_path = _find_kedro_project(current_dir=Path(__file__).parent)
    catalog = kedro_integration.catalog_from_project(project_path, env=env)
    pipelines = kedro_integration.pipelines_from_project(project_path)

    if dataset_names is not None:
        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(
            catalog, pipeline=pipelines["__default__"]
        ).items():
            if dataset_name in dataset_names:
                data_manager[dataset_name] = dataset_loader
