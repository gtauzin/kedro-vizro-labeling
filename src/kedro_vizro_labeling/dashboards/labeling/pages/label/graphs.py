import plotly.graph_objects as go
from vizro.models.types import capture

from kedro_vizro_labeling.dashboards.labeling.pages.label.plotting import (
    plot_time_series,
)
from kedro_vizro_labeling.dashboards.labeling.pages.label.utils import (
    COLORS,
    INVISIBLE_FIGURE_ATTRIBUTES,
    LEGEND_GROUP_MAP,
    QUANTITY_GROUP_MAP,
)


def get_event_labels():
    labels = {}
    for legend_group in ["A"]:
        labels[legend_group] = r"\\\vec{A} \\\quad [m / s^2]$"

    return labels


@capture("graph")
def plot_empty(data_frame):
    return go.Figure(INVISIBLE_FIGURE_ATTRIBUTES)


def plot_event(data_frame, name, quantity_groups=None):
    if quantity_groups is None:
        quantity_groups = QUANTITY_GROUP_MAP.keys()

    colors = COLORS()
    labels = get_event_labels()

    reordered_columns = []
    quantities = data_frame.columns.get_level_values("quantity").unique()

    legend_groups = []
    for quantity_group in quantity_groups:
        legend_groups.extend(LEGEND_GROUP_MAP[quantity_group])

    for legend_group in legend_groups:
        for q in sorted(quantities):
            if q[:-1] == legend_group:
                for g in sorted(data_frame[q].columns.get_level_values("group")):
                    reordered_columns.append((q, g))

    df = data_frame[reordered_columns].copy()

    quantities = df.columns.get_level_values("quantity").unique()
    n_plots = len(set([quantity[:-1] for quantity in quantities]))
    fig = plot_time_series(
        df=df,
        freq=None,
        labels=labels,
        colors=colors,
        title=None,
        height=n_plots * 300,
        width=None,
        web_gl=True,
        resampling=True,
    )

    fig.update_xaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikecolor="grey",
        spikedash="dashdot",
        spikethickness=2,
    )
    fig.update_yaxes(fixedrange=False, title_font=dict(size=30))
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig
