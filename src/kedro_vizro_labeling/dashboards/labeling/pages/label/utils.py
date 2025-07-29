import re
from collections import defaultdict
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
from dash import html
from vizro.managers import data_manager

MAX_N_TABS, MAX_N_EVENTS = 16, 8

CHECKLIST_GROUP_NAMES = (
    ["ALL"]
)

CHECKLIST_OPTION_VALUES = ["X", "Y", "Z"]

INVISIBLE_FIGURE_ATTRIBUTES = {
    "layout": go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
}

QUANTITY_GROUP_MAP = {
    "acceleration": ["A"],
}

LEGEND_GROUP_MAP = {
    "acceleration": ["A"],

}

COLORS = [
    "#0000ff",  # Blue
    "#228b22",  # ForestGreen
    "#dc143c",  # Crimson
    "#00ffff",  # Cyan
    "#7cfc00",  # LawnGreen
    "#ff00ff",  # Magenta
    "#808080",  # Gray
    "#9acd32",  # YellowGreen
    "#8b4513",  # SaddleBrown
    "#00ff7f",  # SpringGreen
    "#00bfff",  # DeepSkyBlue
    "#808000",  # Olive
    "#ff4500",  # OrangeRed
    "#8a2be2",  # BlueViolet
    "#008b8b",  # DarkCyan
    "#ffff00",  # Yellow
    "#00008b",  # DarkBlue
    "#ffa500",  # Orange
    "#483d8b",  # DarkSlateBlue
    "#7b68ee",  # MediumSlateBlue
    "#800080",  # Purple
    "#da70d6",  # Orchid
    "#8fbc8f",  # DarkSeaGreen
]


def get_checklist_options(group_names=None):
    if group_names is None:
        group_names = CHECKLIST_GROUP_NAMES

    checklist_options = []
    for group_name in group_names:
        checklist_options.extend(get_group_checklist_options(group_name))

    n_group_names = len(group_names)
    n_group_values = len(CHECKLIST_OPTION_VALUES) + 1
    checklist_options = [
        checklist_options[j * n_group_values + i] for i in range(n_group_values) for j in range(n_group_names)
    ]

    return checklist_options


def get_group_checklist_options(group_name, len_group=3):
    legend_config = {"ALL": {group_name: None for group_name in CHECKLIST_OPTION_VALUES}}

    quantity = "A"
    legend_config[quantity] = {}
    for i_option, option_name in enumerate(["X", "Y", "Z"]):
        legend_config[quantity][option_name] = COLORS[i_option]

    all_option = {"label": group_name, "value": f"{group_name}__ALL"}
    if group_name == "ALL":
        all_option["label"] = html.Span(
            "",
            style={
                "marginLeft": "1px",
            },
        )

    return [all_option] + [
        {
            "label": html.Span(
                children=[
                    html.Span(
                        option,
                        style={
                            "marginLeft": "3px",
                        },
                    )
                    if color is None
                    else html.Span(
                        style={
                            "display": "inline-block",
                            "width": "10px",
                            "height": "10px",
                            "backgroundColor": color,
                            "marginLeft": "2px",
                        }
                    ),
                ],
                style={
                    "display": "inline-block",
                    "alignItems": "left",
                },
            ),
            "value": f"{group_name}__{option}",
        }
        for option, color in legend_config[group_name].items()
    ]


def get_checklist_value():
    checlist_values = []
    for group_name in CHECKLIST_GROUP_NAMES:
        checlist_values.extend(get_group_checklist_value(group_name))

    return checlist_values


def get_group_checklist_value(group_name):
    return [opt["value"] for opt in get_group_checklist_options(group_name)]


def get_datetime_ranges(relayout_data):
    """Extract datetime ranges for every x-axis found in Plotly relayoutData.

    Scans both formats that Plotly emits on zoom/pan:
      - Separate entries: 'xaxisN.range[0]' and 'xaxisN.range[1]'
      - Single-list entry:    'xaxisN.range': [start, end]

    Args:
        relayout_data: The `relayoutData` dict from a Dash `dcc.Graph` event.

    Returns:
        A dict mapping each axis key (e.g. 'xaxis', 'xaxis2', 'xaxis8', …)
        to a (min_datetime, max_datetime) tuple of ISO-formatted strings.
        Axes with incomplete or missing ranges are omitted.
    """
    ranges: dict[str, tuple[str, str]] = {}

    # 1) Handle any single-list entries: 'xaxisN.range': [start, end]
    for key, val in relayout_data.items():
        m = re.match(r"^(xaxis\d*)\.range$", key)
        if m and isinstance(val, list | tuple):
            axis = m.group(1)
            ranges[axis] = (val[0], val[1])

    # 2) Handle separate-index entries: 'xaxisN.range[0]' / 'xaxisN.range[1]'
    temp: dict[str, list] = {}
    for key, val in relayout_data.items():
        m = re.match(r"^(xaxis\d*)\.range\[(0|1)\]$", key)
        if m:
            axis, idx = m.group(1), int(m.group(2))
            temp.setdefault(axis, [None, None])[idx] = val

    # Transfer complete pairs into the final dict
    for axis, pair in temp.items():
        if pair[0] is not None and pair[1] is not None:
            ranges[axis] = (pair[0], pair[1])

    return ranges


def filter_traces(figure, legend_value):
    legend_value_dict = defaultdict(list)
    for val in legend_value:
        group_name, value = val.split("__")
        legend_value_dict[group_name].append(value)

    # Update the 'visible' property for each trace
    for i, trace in enumerate(figure["data"]):
        group_name = trace["legendgroup"]
        val = trace["name"].split("-")[1]
        visible = val in legend_value_dict[group_name]
        figure["data"][i]["visible"] = visible

    return figure


def get_filenames():
    filenames = data_manager["measurement_list"].load()["filename"].values
    filenames = sorted(filenames)
    return filenames


def get_max_datetime():
    filenames = get_filenames()
    return get_datetime_from_filename(filenames[-1])


def get_min_datetime():
    filenames = get_filenames()
    return get_datetime_from_filename(filenames[0])


def get_min_date():
    return get_min_datetime().date()


def get_device_names():
    ["device_1", "device_2", "device_3"]


def get_device_name_from_filename(filename):
    device_name = filename.split("/")[0]
    return device_name


def get_datetime_from_filename(filename):
    datetime_str = filename.split("/")[1].split(".pq")[0]
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H-%M-%S")


def get_tab_label_from_name(name):
    device_name, datetime_name = name.split("/")
    device_id = device_name.split("-")[0].upper()
    return f"{device_id} {datetime_name}"


def compute_yaxis_ranges(fig):
    """
    Compute the min and max y-values for each y-axis in a Plotly figure.

    Args:
        fig (go.Figure): The Plotly figure object.

    Returns:
        dict: A dictionary mapping each y-axis to its min and max y-values.
    """

    yaxis_ranges = {}
    for trace in fig["data"]:
        if trace["visible"]:
            # Determine the axis this trace is associated with
            yaxis_ref = trace["yaxis"] if "yaxis" in trace else 'y'
            axis_name = 'yaxis' if yaxis_ref == 'y' else f'yaxis{yaxis_ref[1:]}'

            if axis_name not in yaxis_ranges:
                yaxis_ranges[axis_name] = None

            # Append y-values to the list
            y_values = trace["y"]
            if "_inputArray" in y_values:
                y_values = np.array(
                    [
                        val for key, val in y_values["_inputArray"].items()
                        if key not in ["bdata", "dtype", "shape"] and val is not None
                    ]
                )

            # Drop all nan values in y_values
            y_values = y_values[~np.isnan(y_values)]

            if y_values is not None:
                if yaxis_ranges[axis_name] is not None:
                    y_values = np.concatenate([yaxis_ranges[axis_name], y_values])

                yaxis_ranges[axis_name] = [min(y_values), max(y_values)]

    # Compute min and max for each axis
    for axis_name, y_values in yaxis_ranges.items():
        if y_values is None:
            yaxis_ranges[axis_name] = [None, None]

    return yaxis_ranges
    format = "%Y-%m-%dT%H-%M-%S"
