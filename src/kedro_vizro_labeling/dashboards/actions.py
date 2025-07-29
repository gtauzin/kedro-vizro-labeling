from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from typing import Any

from dash import no_update
from vizro.managers import data_manager
from vizro.models.types import capture

from kedro_vizro_labeling.dashboards.labeling.pages.label.utils import (
    get_device_name_from_filename,
)

from .labeling.pages.label.graphs import plot_event
from .labeling.pages.label.utils import (
    CHECKLIST_GROUP_NAMES,
    CHECKLIST_OPTION_VALUES,
    MAX_N_TABS,
    compute_yaxis_ranges,
    filter_traces,
    get_checklist_options,
    get_datetime_ranges,
    get_group_checklist_value,
)


def get_legend(df: Any) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Generate legend options and values for a given DataFrame.

    Args:
        df (Any): DataFrame containing time series data.

    Returns:
        tuple[list[dict[str, Any]], list[str]]: Tuple of (legend_options, legend_value):
            legend_options: List of dicts for checklist options.
            legend_value: List of selected legend values.
    """
    legend_groups = ["ALL", "A"]
    legend_value = [val for group_name in legend_groups for val in get_group_checklist_value(group_name)]

    legend_options = get_checklist_options(legend_groups)

    return legend_options, legend_value


def update_fig_selection(fig, selection_range_list):
    """
    Update the figure with selection ranges and shapes based on the provided selection range list.
    Args:
        fig (dict[str, Any]): The plotly figure to update.
        selection_range_list (list[tuple[str, str]]): List of tuples containing x-range and color for selection.
    Returns:
        dict[str, Any]: Updated figure with selections and shapes.
    """
    if "layout" in fig:
        last_xref_number = sum(1 for key in fig["layout"] if key.startswith('xaxis'))
    else:
        last_xref_number = sum(1 for key in fig.layout if key.startswith('xaxis'))
    last_xref = f"x{last_xref_number}"

    y_ranges = compute_yaxis_ranges(fig)
    selections, shapes = [], []
    for x_range, color in selection_range_list:
        x_start, x_end = x_range

        for yref in range(1, 9):
            y_axis_name = f"yaxis{yref}" if yref > 1 else "yaxis"
            y_range = y_ranges.get(y_axis_name, None)

            if y_range is not None:
                selections.append({
                    "x0": x_start,
                    "y0": y_range[0] + (y_range[0] - y_range[1]) * 0.01,
                    "x1": x_end,
                    "y1": y_range[1] - (y_range[0] - y_range[1]) * 0.01,
                    "xref": last_xref,
                    "yref": f"y{yref}",
                    # "line": {"width": 0},
                })

                # Adding shapes
                shapes.append({
                    "type": "rect",
                    "xref": last_xref,
                    "yref": f"y{yref}",
                    "x0": x_start,
                    "y0": y_range[0] + (y_range[0] - y_range[1]) * 0.01,
                    "x1": x_end,
                    "y1": y_range[1] - (y_range[0] - y_range[1]) * 0.01,
                    "fillcolor": color,
                    "opacity": 0.5,
                    "layer": "below",
                    "line_width": 0,
                })

    fig["layout"]["selections"] = selections
    fig["layout"]["shapes"] = shapes

    return fig


def get_plot(
    df: Any,
    name: str,
    selection_range_list: list[tuple[str, str]] | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    legend_value: list[str] | None = None,
) -> Any:
    """
    Generate a plotly figure for the given time series data, filtered by time and legend selection.

    Args:
        df (Any): DataFrame containing time series data.
        name (str): Name of the time series.
        selection_range_list (list[tuple[str, str]] | None): Optional list of selection ranges for labeling.
        start (datetime | None): Optional start datetime for filtering.
        end (datetime | None): Optional end datetime for filtering.
        legend_value (list[str] | None): Optional list of legend values to filter traces.

    Returns:
        Any: Plotly figure object.
    """
    if start is not None:
        time_index = df.index.get_level_values("time")
        df = df[(time_index >= start)]

    if end is not None:
        time_index = df.index.get_level_values("time")
        df = df[(time_index <= end)]

    fig = plot_event(df, name)

    if legend_value is not None:
        fig = filter_traces(fig, legend_value)

    if selection_range_list is not None:
        fig = update_fig_selection(fig, selection_range_list)

    return fig


@capture("action")
def create_tabs(
    names: list[str],
) -> list[Any]:
    """
    Create initial dashboard tabs and their associated states.

    Args:
        names (list[str]): List of time series names.

    Returns:
        list[Any]: List containing tab states and plot/legend data for the dashboard.
    """
    i_tab = 0
    active_tab = f"tab-{i_tab}"

    name = names[i_tab]
    df = data_manager["measurement"].load(name)
    fig = get_plot(df, name)
    legend_options, legend_value = get_legend(df)
    n_tabs = len(names)

    tab_relayout_datas = [None] * MAX_N_TABS

    plot_component_style = {} if n_tabs else {"display": "none"}
    legend_style = plot_component_style
    buttons_style = plot_component_style

    return sum(
        [
            [active_tab],
            [fig],
            [legend_value],
            [legend_value],
            [legend_options],
            [legend_style],
            [buttons_style],
            tab_relayout_datas,
        ],
        [],
    )


@capture("action")
def toggle_tabs(
    active_tab: int | str,
    names: list[str],
    tab_legend_0: list[str],
    tab_legend_1: list[str],
    tab_legend_2: list[str],
    tab_legend_3: list[str],
    tab_legend_4: list[str],
    tab_legend_5: list[str],
    tab_legend_6: list[str],
    tab_legend_7: list[str],
    tab_legend_8: list[str],
    tab_legend_9: list[str],
    tab_legend_10: list[str],
    tab_legend_11: list[str],
    tab_legend_12: list[str],
    tab_legend_13: list[str],
    tab_legend_14: list[str],
    tab_legend_15: list[str],
    tab_relayout_data_0: dict[str, Any] | None,
    tab_relayout_data_1: dict[str, Any] | None,
    tab_relayout_data_2: dict[str, Any] | None,
    tab_relayout_data_3: dict[str, Any] | None,
    tab_relayout_data_4: dict[str, Any] | None,
    tab_relayout_data_5: dict[str, Any] | None,
    tab_relayout_data_6: dict[str, Any] | None,
    tab_relayout_data_7: dict[str, Any] | None,
    tab_relayout_data_8: dict[str, Any] | None,
    tab_relayout_data_9: dict[str, Any] | None,
    tab_relayout_data_10: dict[str, Any] | None,
    tab_relayout_data_11: dict[str, Any] | None,
    tab_relayout_data_12: dict[str, Any] | None,
    tab_relayout_data_13: dict[str, Any] | None,
    tab_relayout_data_14: dict[str, Any] | None,
    tab_relayout_data_15: dict[str, Any] | None,
    selection_range_list: list[tuple[str, str]] | None = None,
) -> tuple[Any, list[str], list[dict[str, Any]], dict[str, bool]]:
    """
    Update the dashboard when switching between tabs.

    Args:
        active_tab (Union[int, str]): The active tab index or tab id string.
        names (list[str]): List of time series names.
        tab_legend_0..15 (list[str]): Legend values for each tab.
        tab_relayout_data_0..15 (Optional[dict[str, Any]]): Relayout data for each tab.
        selection_range_list (list[tuple[str, str]] | None): Optional list of selection ranges for labeling.

    Returns:
        tuple[Any, list[str], list[dict[str, Any]], dict[str, bool]]: Updated figure, legend values, legend options, and legend all-values dict.
    """
    local_args = locals()
    tab_legends = [local_args[f"tab_legend_{i_tab}"] for i_tab in range(MAX_N_TABS)]
    tab_relayout_datas = [local_args[f"tab_relayout_data_{i_tab}"] for i_tab in range(MAX_N_TABS)]

    i_tab = active_tab
    if isinstance(active_tab, str):
        i_tab = int(active_tab.split("-")[1])

    name = names[i_tab]
    legend_value = tab_legends[i_tab]
    relayout_data = tab_relayout_datas[i_tab]

    legend_all_values: dict[str, bool] = {}
    for group_name in CHECKLIST_GROUP_NAMES:
        legend_group_value = [val.split("__")[1] for val in legend_value if val.startswith(group_name)]
        if group_name == "ALL":
            for val in CHECKLIST_OPTION_VALUES:
                legend_all_values[val] = val in legend_group_value

        legend_all_values[group_name] = "ALL" in legend_group_value

    start, end = None, None
    if relayout_data is not None and "autosize" not in relayout_data:
        datetime_ranges = get_datetime_ranges(relayout_data)
        min_dt, max_dt = next(iter(datetime_ranges.values()))
        start = datetime.strptime(min_dt, "%Y-%m-%d %H:%M:%S.%f")
        end = datetime.strptime(max_dt, "%Y-%m-%d %H:%M:%S.%f")

    df = data_manager["measurement"].load(name)
    fig = get_plot(df, name, selection_range_list=selection_range_list, start=start, end=end, legend_value=legend_value)

    legend_options, _ = get_legend(df)

    return fig, legend_value, legend_options, legend_all_values


@capture("action")
def update_plot(
    active_tab: int | str,
    names: list[str],
    relayout_data: dict[str, Any],
    tab_relayout_data_0: dict[str, Any] | None,
    tab_relayout_data_1: dict[str, Any] | None,
    tab_relayout_data_2: dict[str, Any] | None,
    tab_relayout_data_3: dict[str, Any] | None,
    tab_relayout_data_4: dict[str, Any] | None,
    tab_relayout_data_5: dict[str, Any] | None,
    tab_relayout_data_6: dict[str, Any] | None,
    tab_relayout_data_7: dict[str, Any] | None,
    tab_relayout_data_8: dict[str, Any] | None,
    tab_relayout_data_9: dict[str, Any] | None,
    tab_relayout_data_10: dict[str, Any] | None,
    tab_relayout_data_11: dict[str, Any] | None,
    tab_relayout_data_12: dict[str, Any] | None,
    tab_relayout_data_13: dict[str, Any] | None,
    tab_relayout_data_14: dict[str, Any] | None,
    tab_relayout_data_15: dict[str, Any] | None,
    selection_range_list: list[tuple[str, str]] | None = None,
) -> list[Any]:
    """
    Update the plot for the active tab based on relayout data (e.g., zoom/pan).

    Args:
        active_tab (Union[int, str]): The active tab index or tab id string.
        names (list[str]): List of time series names.
        relayout_data (dict[str, Any]): Plotly relayout data.
        tab_relayout_data_0..15 (Optional[dict[str, Any]]): Relayout data for each tab.
        selection_range_list (list[tuple[str, str]] | None): Optional list of selection ranges for labeling.

    Returns:
        list[Any]: Updated figure and relayout data for all tabs.
    """
    if "autosize" in relayout_data:
        return [no_update] * (MAX_N_TABS + 1)

    local_args = locals()
    tab_relayout_datas = [local_args[f"tab_relayout_data_{i_tab}"] for i_tab in range(MAX_N_TABS)]

    i_tab = active_tab
    if isinstance(active_tab, str):
        i_tab = int(active_tab.split("-")[1])

    name = names[i_tab]
    df = data_manager["measurement"].load(name)
    fig = get_plot(df, name, selection_range_list=selection_range_list)
    fig = fig.construct_update_data_patch(relayout_data)
    tab_relayout_datas[i_tab] = relayout_data

    return sum(
        [
            [fig],
            tab_relayout_datas,
        ],
        [],
    )


@capture("action")
def replot(
    names: list[str],
    legend_value: list[str],
    active_tab: int | str,
    tab_legend_value_0: list[str],
    tab_legend_value_1: list[str],
    tab_legend_value_2: list[str],
    tab_legend_value_3: list[str],
    tab_legend_value_4: list[str],
    tab_legend_value_5: list[str],
    tab_legend_value_6: list[str],
    tab_legend_value_7: list[str],
    tab_legend_value_8: list[str],
    tab_legend_value_9: list[str],
    tab_legend_value_10: list[str],
    tab_legend_value_11: list[str],
    tab_legend_value_12: list[str],
    tab_legend_value_13: list[str],
    tab_legend_value_14: list[str],
    tab_legend_value_15: list[str],
    selection_range_list: list[tuple[str, str]] | None = None,
) -> tuple[Any, ...]:
    """
    Replot the figure for the active tab when legend values change.

    Args:
        names (list[str]): List of time series names.
        legend_value (list[str]): Current legend values for the active tab.
        active_tab (Union[int, str]): The active tab index or tab id string.
        tab_legend_value_0..15 (list[str]): Legend values for each tab.
        selection_range_list (list[tuple[str, str]] | None): Optional list of selection ranges for labeling.

    Returns:
        tuple[Any, ...]: Updated figure and legend values for all tabs.
    """
    local_args = locals()
    tab_legend_values = [local_args[f"tab_legend_value_{i_tab}"] for i_tab in range(MAX_N_TABS)]

    i_tab = active_tab
    if isinstance(active_tab, str):
        i_tab = int(active_tab.split("-")[1])

    name = names[i_tab]
    df = data_manager["measurement"].load(name)
    figure = get_plot(df, name, selection_range_list=selection_range_list,legend_value=legend_value)

    tab_legend_values[i_tab] = legend_value

    return tuple(sum([[figure], tab_legend_values], []))


@capture("action")
def update_dragmode(
    dragmode: str,
    figure: dict[str, Any],
) -> dict[str, Any]:
    """
    Update the dragmode of the plotly figure layout.

    Args:
        dragmode (str): The dragmode to set (e.g., 'zoom', 'pan').
        figure (dict[str, Any]): The plotly figure dict.

    Returns:
        dict[str, Any]: The updated figure dict.
    """
    figure["layout"]["dragmode"] = dragmode

    return figure


@capture("action")
def zoom_in(fig: dict[str, Any]) -> dict[str, Any]:
    """
    Zoom in on the x-axis of the plotly figure.

    Args:
        fig (dict[str, Any]): The plotly figure dict.

    Returns:
        dict[str, Any]: The updated figure dict with zoomed x-axis.
    """
    zoom_in_factor = 0.7

    x_range = fig["layout"]["xaxis"]["range"]
    x_start = datetime.fromisoformat(x_range[0])
    x_end = datetime.fromisoformat(x_range[1])

    x_center = x_start + (x_end - x_start) / 2
    x_span = (x_end - x_start) * zoom_in_factor

    new_x_range = [x_center - x_span / 2, x_center + x_span / 2]

    for key in fig["layout"]:
        if key.startswith("xaxis"):
            fig["layout"][key]["range"] = new_x_range

    return fig


@capture("action")
def zoom_out(fig: dict[str, Any]) -> dict[str, Any]:
    """
    Zoom out on the x-axis of the plotly figure.

    Args:
        fig (dict[str, Any]): The plotly figure dict.

    Returns:
        dict[str, Any]: The updated figure dict with zoomed out x-axis.
    """
    zoom_out_factor = 1.3

    x_range = fig["layout"]["xaxis"]["range"]
    x_start = datetime.fromisoformat(x_range[0])
    x_end = datetime.fromisoformat(x_range[1])

    x_center = x_start + (x_end - x_start) / 2
    x_span = (x_end - x_start) * zoom_out_factor

    new_x_range = [x_center - x_span / 2, x_center + x_span / 2]

    for key in fig["layout"]:
        if key.startswith("xaxis"):
            fig["layout"][key]["range"] = new_x_range

    return fig


@capture("action")
def update_legend_checklist_value(
    checklist_value: list[str],
    previous_all_value: dict[str, bool],
    checklist_options: list[dict[str, Any]],
    active_tab: int | str,
    tab_legend_value_0: list[str],
    tab_legend_value_1: list[str],
    tab_legend_value_2: list[str],
    tab_legend_value_3: list[str],
    tab_legend_value_4: list[str],
    tab_legend_value_5: list[str],
    tab_legend_value_6: list[str],
    tab_legend_value_7: list[str],
    tab_legend_value_8: list[str],
    tab_legend_value_9: list[str],
    tab_legend_value_10: list[str],
    tab_legend_value_11: list[str],
    tab_legend_value_12: list[str],
    tab_legend_value_13: list[str],
    tab_legend_value_14: list[str],
    tab_legend_value_15: list[str],
) -> list[Any]:
    """
    Update the legend checklist values for the active tab, handling group and all selection logic.

    Args:
        checklist_value (list[str]): The current checklist values.
        previous_all_value (dict[str, bool]): The previous all-values dict.
        checklist_options (list[dict[str, Any]]): The checklist options.
        active_tab (Union[int, str]): The active tab index or tab id string.
        tab_legend_value_0..15 (list[str]): Legend values for each tab.

    Returns:
        list[Any]: Updated legend values for all tabs, the updated checklist value, and all-values dict.
    """
    local_args = locals()

    i_tab = active_tab
    if isinstance(active_tab, str):
        i_tab = int(active_tab.split("-")[1])

    tab_legend_values = [local_args[f"tab_legend_value_{i_tab}"] for i_tab in range(MAX_N_TABS)]

    checklist_value_dict: dict[str, list[str]] = defaultdict(list)
    for val in checklist_value:
        group_name, value = val.split("__")
        checklist_value_dict[group_name].append(value)

    updated_checklist_value_dict = checklist_value_dict

    all_value = "ALL" in checklist_value_dict["ALL"]
    if all_value != previous_all_value["ALL"]:
        if all_value:
            for group_name in CHECKLIST_GROUP_NAMES:
                updated_checklist_value_dict[group_name] = [
                    option["value"].split("__")[1]
                    for option in checklist_options
                    if option["value"].startswith(group_name)
                ]
        else:
            for group_name in CHECKLIST_GROUP_NAMES:
                updated_checklist_value_dict[group_name] = []

    else:
        group_names = deepcopy(CHECKLIST_GROUP_NAMES)
        group_names.remove("ALL")

        for group_name in group_names:
            all_value = "ALL" in checklist_value_dict[group_name]
            if all_value != previous_all_value[group_name]:
                if all_value:
                    updated_checklist_value_dict[group_name] = [
                        option["value"].split("__")[1]
                        for option in checklist_options
                        if option["value"].startswith(group_name)
                    ]

                else:
                    updated_checklist_value_dict[group_name] = []

        values = deepcopy(CHECKLIST_OPTION_VALUES)
        for val in values:
            all_value = val in checklist_value_dict["ALL"]
            if all_value != previous_all_value[val]:
                if all_value:
                    for group_name in group_names:
                        if val not in updated_checklist_value_dict[group_name]:
                            updated_checklist_value_dict[group_name].append(val)

                else:
                    for group_name in group_names:
                        if val in updated_checklist_value_dict[group_name]:
                            updated_checklist_value_dict[group_name].remove(val)

    all_values = {group_name: "ALL" in checklist_value_dict[group_name] for group_name in CHECKLIST_GROUP_NAMES} | {
        val: val in checklist_value_dict["ALL"] for val in CHECKLIST_OPTION_VALUES
    }

    updated_checklist_value: list[str] = []
    for group_name, values in updated_checklist_value_dict.items():
        for value in values:
            updated_checklist_value.append(f"{group_name}__{value}")

    tab_legend_values[i_tab] = updated_checklist_value

    return tab_legend_values + [updated_checklist_value, all_values]


@capture("action")
def load_names_from_cross_page_store(selected_filenames: list[str]) -> list[str]:
    """
    Load time series names from selected filenames using a utility function.

    Args:
        selected_filenames (list[str]): List of selected filenames.

    Returns:
        list[str]: List of time series names.
    """
    if not selected_filenames:
        return []

    selected_names = [get_device_name_from_filename(filename) for filename in selected_filenames]

    return selected_names
