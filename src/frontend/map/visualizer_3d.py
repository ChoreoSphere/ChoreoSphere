import os
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any

try:
    import rasterio
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False


def _find_file(filename: str) -> str:
    """Locates input raster files in local workspace."""
    candidates = [
        filename,
        os.path.join("data", filename),
    ]
    return next((p for p in candidates if os.path.exists(p)), None)


def build_3d_surface(
    data: Dict[str, Any],
    colorscale: str = "Viridis",
    title_suffix: str = ""
) -> go.Figure:
    """
    Creates a 3D Plotly Surface visualization.

    Z-height (terrain shape) comes from dem_matched.tif — real elevation,
    reprojected and pixel-aligned to the NISAR grid.

    Surface color comes from the REAL NISAR radar values already loaded
    into data["values"] (not re-derived from any .tif file).
    """
    input_values = data["values"]
    label = data.get("label", "Relative NISAR Measurement (dB)")
    units = data.get("units", "dB")
    source = data.get("source", "NISAR Granule")
    step = data.get("metadata", {}).get("downsample_step", 10)

    z_grid = None
    color_grid = input_values
    color_label = f"{label} ({units})"
    z_title = "Elevation (m)"
    z_desc = "Relative Measurement Terrain"

    dem_path = _find_file("dem_matched.tif")

    if dem_path and RASTERIO_AVAILABLE:
        try:
            with rasterio.open(dem_path) as src:
                full_dem = src.read(1).astype(np.float32)
                # Downsample with the SAME step used for the NISAR data,
                # since dem_matched.tif is already pixel-aligned to that grid.
                z_grid = full_dem[::step, ::step]
                z_desc = "dem_matched.tif (real elevation, aligned to NISAR grid)"
        except Exception as err:
            print(f"[visualizer_3d] Error loading dem_matched.tif: {err}")

    if z_grid is None:
        z_grid = np.nan_to_num(input_values, nan=0.0)
        z_desc = "Relative Measurement Terrain (no DEM found)"

    # Ensure z_grid and color_grid end up the same shape (trim to smallest)
    min_rows = min(z_grid.shape[0], color_grid.shape[0])
    min_cols = min(z_grid.shape[1], color_grid.shape[1])
    z_grid = z_grid[:min_rows, :min_cols]
    color_grid = color_grid[:min_rows, :min_cols]

    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            z=z_grid,
            surfacecolor=color_grid,
            colorscale=colorscale,
            colorbar=dict(
                title=dict(text=color_label, side="right"),
                len=0.75
            ),
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                roughness=0.3
            ),
            hovertemplate=(
                "<b>X Grid</b>: %{x}<br>"
                "<b>Y Grid</b>: %{y}<br>"
                "<b>Elevation</b>: %{z:,.1f} m<br>"
                f"<b>{color_label}</b>: %{{surfacecolor:.2f}}"
                "<extra></extra>"
            )
        )
    )

    full_title = "ChoreoSphere - 3D Terrain & NISAR Overlay"
    if title_suffix:
        full_title += f" ({title_suffix})"

    fig.update_layout(
        title=dict(
            text=full_title,
            x=0.5,
            xanchor="center",
            font=dict(size=18, color="#1e293b")
        ),
        scene=dict(
            xaxis=dict(title=dict(text="X Grid")),
            yaxis=dict(title=dict(text="Y Grid")),
            zaxis=dict(title=dict(text=z_title)),
            aspectratio=dict(x=1, y=1, z=0.25)
        ),
        template="plotly_white",
        margin=dict(l=10, r=10, b=10, t=50),
        annotations=[
            dict(
                text=f"Source: {source} | Layer: {z_desc}",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.0,
                y=-0.05,
                font=dict(size=10, color="gray")
            )
        ]
    )

    return fig