import plotly.graph_objects as go
from typing import Dict, Any, Optional


def build_2d_heatmap(
    data: Dict[str, Any],
    colorscale: str = "Viridis",
    title_suffix: str = ""
) -> go.Figure:
    """
    Creates a 2D Plotly heatmap visualization of NISAR spatial raster data.

    Parameters:
    -----------
    data: Dict[str, Any]
        Standardized data dictionary containing 'x', 'y', 'values', 'label', 'units', etc.
    colorscale: str
        Plotly colorscale name (e.g. 'Viridis', 'Plasma', 'Cividis', 'RdBu_r').
    title_suffix: str
        Optional suffix to append to figure title.

    Returns:
    --------
    go.Figure
        Configured 2D Plotly Heatmap figure object.
    """
    x = data["x"]
    y = data["y"]
    values = data["values"]
    label = data.get("label", "Relative NISAR Measurement (dB)")
    units = data.get("units", "dB")
    source = data.get("source", "NISAR Granule")

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            x=x,
            y=y,
            z=values,
            colorscale=colorscale,
            colorbar=dict(
                title=dict(text=f"{label} ({units})", side="right"),
                thickness=18,
                len=0.9
            ),
            hoverongaps=False,
            hovertemplate=(
                "<b>X Coordinate</b>: %{x:,.1f} m<br>"
                "<b>Y Coordinate</b>: %{y:,.1f} m<br>"
                f"<b>{label}</b>: %{{z:.2f}} {units}"
                "<extra></extra>"
            )
        )
    )

    full_title = f"NISAR 2D Spatial Heatmap - {label}"
    if title_suffix:
        full_title += f" ({title_suffix})"

    fig.update_layout(
        title=dict(
            text=full_title,
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        xaxis=dict(
            title="X Spatial Coordinate (meters)",
            showgrid=True,
            zeroline=False,
            scaleanchor="y",
            scaleratio=1.0
        ),
        yaxis=dict(
            title="Y Spatial Coordinate (meters)",
            showgrid=True,
            zeroline=False
        ),
        template="plotly_white",
        margin=dict(l=60, r=60, t=60, b=60),
        annotations=[
            dict(
                text=f"Source: {source}",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.0,
                y=-0.12,
                font=dict(size=10, color="gray")
            )
        ]
    )

    return fig
