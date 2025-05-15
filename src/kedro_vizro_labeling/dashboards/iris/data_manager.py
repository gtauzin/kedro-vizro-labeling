import subprocess

from flask_caching import Cache
from vizro.integrations import kedro as kedro_integration


def load_kedro_datasets(env, dataset_names=None):
    from vizro.managers import data_manager

    # AM question: is there a reason you find project_path like this rather than just use Pathlib and specify
    # Path.parent or similar?
    project_path = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], universal_newlines=True).strip()
    catalog = kedro_integration.catalog_from_project(project_path, env=env)
    pipelines = kedro_integration.pipelines_from_project(project_path)

    if dataset_names is not None:
        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(
            catalog, pipeline=pipelines["__default__"]
        ).items():
            # AM comment: `if not dataset_names` is maybe redundant given L16
            if not dataset_names or dataset_name in dataset_names:
                data_manager[dataset_name] = dataset_loader

    data_manager.cache = Cache(
        config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT": 600}
    )

    # AM comment: you shouldn't need to return this. You're populating a global object data_manager.
    # return data_manager
