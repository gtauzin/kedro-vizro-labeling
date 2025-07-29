import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Scatter
from plotly.subplots import make_subplots
from plotly_resampler import FigureResampler
from vizro.models.types import capture

from pulsation.utils.time_split import split_time

from .utils import get_hover_template, get_theme


# TODO: Make channel_id and group_id range customizable
def _plot(df, quantity, colors, row, fig, web_gl, resampling):
    if web_gl:
        from plotly.graph_objects import Scattergl as ScatterClass
    else:
        from plotly.graph_objects import Scatter as ScatterClass

    df = df.sort_index(axis=1)
    quantities = df.columns.get_level_values("quantity").unique()
    groups = sorted(list(df.columns.get_level_values("group").unique()))

    n_channel_ids = max([int(q[-1]) for q in quantities])

    for channel_id in range(1, n_channel_ids + 1):
        for group_id, group in enumerate(groups):
            col = (f"{quantity}{channel_id}", group)
            visible = True

            if col in df.columns:
                df_col = df[col]
            else:
                df_col = pd.DataFrame({col: np.ones(len(df.index)) * np.nan}, index=df.index)[col]
                visible = False

            color = None
            if (channel_id-1, group_id) in colors:
                color = colors[(channel_id-1, group_id)]

            if resampling:
                n_hf_x = len(df_col.index)
                n_max_samples = None
                if len(df_col.dropna()) <= 0.5 * n_hf_x:
                    n_max_samples = n_hf_x
                scatter = ScatterClass(
                    mode="lines",
                    line=dict(color=color, width=2),
                    name=f"{quantity[0]}{channel_id}-{group}",
                    visible=visible,
                    connectgaps=True,
                )
                fig.add_trace(
                    scatter,
                    hf_x=df_col.index,
                    hf_y=df_col.values,
                    max_n_samples=n_max_samples,
                    row=row,
                    col=1,
                )

            else:
                scatter = ScatterClass(
                    x=df_col.index,
                    y=df_col.values,
                    mode="lines",
                    line=dict(color=color, width=2),
                    name=f"{quantity[0]}{channel_id}-{group}",
                    visible=visible,
                    connectgaps=True,
                )
                fig.add_trace(scatter, row=row, col=1)

    return fig


def plot_time_series(
    df,
    name=None,
    quantities=None,
    start=None,
    end=None,
    freq=None,
    labels=None,
    colors=None,
    title=None,
    height=800,
    width=1400,
    web_gl=False,
    resampling=True,
):
    """Return a time series figure.

    Parameters
    ----------
    df : pd.DataFrame, required
        Input time series dataframe.
    name : str or None, default=``None``
        Name of the time series to plot. If ``None``,
        the name is extracted from the index as the
        first one.
    quantities : list of str or None, default=``None``
        List of available quantities in `df` to plot.
    start : float or None, default=``None``
        Start delay of the time series in milliseconds. If ``None`,
        it is ignored.
    end : float or None, default=``None``
        End delay of the time series in milliseconds. If ``None`,
        it is ignored.
    freq : str or None, default=``None``
        Dataframe frequency to use to resample the input time series.
    labels : dict or None, default=``None``
        Dictionary mapping quantities to their corresponding label.
    colors : dict or None, default=``None``
        Dictionary mapping quantities to their corresponding colors.
    title : str or None, default=``None``
        The title label of the plot.
    height : int, default=``800``
        Sets the height of the chart.
    width : int, default=``1400``
        Sets the width of the chart.
    web_gl : bool, default=``True``
        Whether to use `go.Scattergl` in place of `go.Scatter`.
    resampling : bool, default=``True``
        Whether to use `plotly-resampler`'s `FigureResampler`.

    Returns
    -------
    fig : plotly.Figure

    """
    if name is None:
        name = df.index.get_level_values("name")[0]

    labels = labels or {}

    df_name = split_time(df.loc[[name]], start, end)
    df_name = df_name.loc[name]

    if freq is not None:
        df_name = df_name.asfreq(freq)

    if colors is None:
        colors = {}

    available_quantities = list(df_name.columns.unique("quantity"))

    if quantities is None:
        quantities = []
        for quantity in available_quantities:
            if quantity[:-1] not in quantities:
                quantities.append(quantity[:-1])

    quantity_channels_dict = {
        quantity: list(set([q for q in available_quantities if q[:-1] == quantity])) for quantity in quantities
    }

    n_rows = len(quantities)
    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06/len(quantities),
    )

    if resampling:
        fig = FigureResampler(
            fig,
            resampled_trace_prefix_suffix=("", ""),
            show_mean_aggregation_size=False,
        )

    for row, quantity in enumerate(quantities):
        quantity_channels = quantity_channels_dict[quantity]
        quantity_colors = {}
        if quantity in colors:
            quantity_colors = colors[quantity]

        fig = _plot(
            df=df_name[quantity_channels],
            quantity=quantity,
            colors=quantity_colors,
            row=row + 1,
            fig=fig,
            web_gl=web_gl,
            resampling=resampling,
        )

        yaxis_label = quantity
        if quantity in labels:
            yaxis_label = labels[quantity]

        fig["layout"][f"yaxis{row + 1}"]["title"] = yaxis_label

        fig.update_yaxes(title_standoff=7, row=row + 1, col=1)

    main_xaxis = ""
    if len(quantities) > 1:
        main_xaxis = fig["layout"]["xaxis"]["matches"][1:]

    fig.update_traces(xaxis=f"x{main_xaxis}")

    fig.update_layout(
        height=height,
        width=width,
        title_text=title,
    )

    return fig
