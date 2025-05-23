import subprocess

from flask_caching import Cache
from vizro.integrations import kedro as kedro_integration


def load_kedro_datasets(env, dataset_names=None):
    from vizro.managers import data_manager

    project_path = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], universal_newlines=True).strip()
    catalog = kedro_integration.catalog_from_project(project_path, env=env)
    pipelines = kedro_integration.pipelines_from_project(project_path)

    if dataset_names is not None:
        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(
            catalog, pipeline=pipelines["__default__"]
        ).items():
            if not dataset_names or dataset_name in dataset_names:
                data_manager[dataset_name] = dataset_loader

    data_manager.cache = Cache(
        config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT": 600}
    )

    return data_manager
