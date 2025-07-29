from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from flask_caching import Cache
from kedro.utils import _find_kedro_project
from vizro.integrations import kedro as kedro_integration
from vizro.managers import data_manager

from kedro_vizro_labeling.dashboards.labeling.pages.label.utils import (
    get_device_name_from_filename,
)


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

    data_manager.cache = Cache(
        config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": "localhost", "CACHE_REDIS_PORT": 6379}
    )


def group_files_from_event_list(time_threshold=2):
    measurement_list = data_manager["measurement_list"].load()

    # Ensure the dataframe is sorted by datetime index
    measurement_list = measurement_list.sort_index()

    # Group files based on the time threshold
    groups = defaultdict(list)
    group_id = 0
    prev_timestamp = None

    for timestamp, row in measurement_list.iterrows():
        file = row["filename"]
        if prev_timestamp is None:
            groups[group_id].append(file)
        elif (timestamp - prev_timestamp) <= timedelta(seconds=time_threshold):
            groups[group_id].append(file)
        else:
            group_id += 1
            groups[group_id].append(file)
        prev_timestamp = timestamp

    return dict(groups)


def load_measurement_group(group_id):
    event_groups = group_files_from_event_list(time_threshold=2)

    return event_groups[group_id]


data_manager["measurement_group"] = load_measurement_group


def load_measurement(name) -> pd.DataFrame:
    device, datetime_str = name.split("/")
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    measurement_list = data_manager["measurement_list"].load()
    filename = measurement_list.loc[(measurement_list.index == dt) & (measurement_list["device"] == device), "filename"].values[0]

    wf = pd.DataFrame()
    measurement_partition = data_manager["measurement_partition"].load()

    wf = measurement_partition[filename.split(".pq")[0]]()
    wf.index = wf.index.set_levels([get_device_name_from_filename(filename)], level="name")

    return wf


data_manager["measurement"] = load_measurement
