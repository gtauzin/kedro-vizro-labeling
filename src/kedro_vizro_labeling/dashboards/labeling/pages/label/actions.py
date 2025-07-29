from datetime import datetime

from dash import no_update
from dash.exceptions import PreventUpdate
from pyparsing import Any
from vizro.managers import data_manager
from vizro.models.types import capture

from kedro_vizro_labeling.dashboards.actions import (
    get_legend,
    get_plot,
    update_fig_selection,
)
from kedro_vizro_labeling.dashboards.labeling.data import (
    group_files_from_event_list,
)
from kedro_vizro_labeling.dashboards.labeling.pages.label.utils import (
    COLORS,
    MAX_N_EVENTS,
    MAX_N_TABS,
    get_device_name_from_filename,
)


@capture("action")
def get_new_event_group(n_clicks):
    file_groups_dict = group_files_from_event_list()
    file_groups = list(file_groups_dict.values())[n_clicks - 1]
    group_files_values = [get_device_name_from_filename(filename) for filename in file_groups]
    group_files_options = [
        {
            "label": f"Device {val.split(':')[1].split('-')[0]}",
            "value": val,
        }
        for val in group_files_values
    ]

    return group_files_options, group_files_values


@capture("action")
def update_tab_titles(names):
    n_tabs = len(names)

    tab_titles = []
    for i_tab in range(MAX_N_TABS):
        if i_tab < n_tabs:
            name = names[i_tab]

            tab_title = f"Device {name.split(':')[1].split('-')[0]}"
            tab_title = f"Device {i_tab + 1}"

        else:
            tab_title = ""

        tab_titles.append(tab_title)

    return tab_titles



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

    n_devices = n_tabs

    # TODO: Replace with configuration
    n_I_channels_devices = []
    for i_device in range(MAX_N_TABS):
        try:
            df = data_manager["measurement"].load(names[i_device])
        except Exception:
            n_I_channels = 5
        n_I_channels_devices.append(n_I_channels)

    event_device_checklist_styles, event_device_channel_checklist_options = [], []
    for i_event in range(MAX_N_EVENTS):
        for i_device in range(MAX_N_TABS):
            if i_device < n_devices:
                event_device_channel_checklist_options.append([f"I{i_channel + 1}" for i_channel in range(n_I_channels_devices[i_device])])
                event_device_checklist_styles.append({})
            else:
                event_device_channel_checklist_options.append([])
                event_device_checklist_styles.append({"display": "none"})

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
            event_device_checklist_styles,
            event_device_channel_checklist_options,
        ],
        [],
    )


@capture("action")
def submit_label(selection_range_list, selection_popup_store):
    return no_update


@capture("action")
def process_selection(
    selected_data,
    fig,
    selection_range_list,
):
    if "range" not in selected_data:
        raise PreventUpdate()

    x_range = selected_data["range"]["x8"]

    replace = False
    for i, ((start, end), _) in enumerate(selection_range_list):
        start_test = datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
        end_test = datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")

        start_x_range = datetime.strptime(x_range[0], "%Y-%m-%d %H:%M:%S.%f")
        end_x_range = datetime.strptime(x_range[1], "%Y-%m-%d %H:%M:%S.%f")

        if (end_test - start_test) == (end_x_range - start_x_range):
            selection_range_list[i] = (x_range, selection_range_list[i][1])
            replace = True
            break

        if x_range[0] in (start, end) or x_range[1] in (start, end):
            selection_range_list[i] = (x_range, selection_range_list[i][1])
            replace = True
            break

    if not replace:
        for color in COLORS:
            if not any(c == color for _, c in selection_range_list):
                selection_range_list.append((x_range, color))
                break

    updated_fig = update_fig_selection(fig, selection_range_list)

    event_accordion_style = {} if len(selection_range_list) else {"display": "none"}
    event_accordion_item_styles = [{}] * len(selection_range_list) + [{"display": "none"}] * (MAX_N_EVENTS - len(selection_range_list))

    return sum(
        [
            [updated_fig],
            [selection_range_list],
            [event_accordion_style],
            event_accordion_item_styles,
        ],
        [],
    )
