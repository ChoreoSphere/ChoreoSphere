import os
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any

try:
    import rasterio
    from rasterio.enums import Resampling
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False


def _find_file(filename: str) -> str:
    """Locates input raster files in local workspace or downloads directory."""
    candidates = [
        os.path.join("data", filename),
        os.path.join(r"C:\Users\Admin\Downloads\Dancing-with-SARs\data", filename),
        os.path.join(r"C:\Users\Admin\Desktop\ChoreoSphere\data", filename),
        os.path.join(r"C:\Users\Admin\Desktop\render_dem\render_dem - Copy\source\data", filename),
    ]
    return next((p for p in candidates if os.path.exists(p)), None)


def build_3d_surface(
    data: Dict[str, Any],
    colorscale: str = "Viridis",
    title_suffix: str = ""
) -> go.Figure:
    """
    Creates a 3D Plotly Surface visualization matching Shawal's exact render_dem implementation.

    Direct Comparison & Processing Pipeline from Shawal's mainvisualization.py:
    -----------------------------------------------------------------------------
    1. Bilinear Resampling: Reads raster with Resampling.bilinear (step factor 15).
    2. Outlier Capping & Nodata Clean:
       - Replaces nodata/negative values with 0.0.
       - Clips extreme 99th percentile sensor spikes (max_cap = np.percentile(dem_grid, 99)).
    3. Surface Color Normalization:
       - Normalizes surfacecolor to 0.0 - 1.0 range for full Viridis color contrast.
    4. Plotly Scene & Camera Parameters:
       - aspectratio = dict(x=1, y=1, z=0.25)
       - lighting = dict(ambient=0.6, diffuse=0.8, roughness=0.3)
       - margin = dict(l=10, r=10, b=10, t=50)
       - colorbar = dict(title='Radar Backscatter (dB)', len=0.75)
    """
    input_values = data["values"]
    has_dem_flag = data.get("has_dem", False)
    label = data.get("label", "Relative NISAR Measurement (dB)")
    units = data.get("units", "dB")
    source = data.get("source", "NISAR Granule")

    sar_path = _find_file("output_hh.tif")
    dem_path = _find_file("dem.tif")

    z_grid = None
    color_grid = None
    z_title = "Elevation (m)"
    z_desc = "3D Terrain & NISAR Overlay"

    # Match Shawal's exact processing pipeline from mainvisualization.py
    if sar_path and RASTERIO_AVAILABLE:
        try:
            with rasterio.open(sar_path) as src:
                step = 15
                out_height = max(1, int(src.height / step))
                out_width = max(1, int(src.width / step))

                # Read band 1 with bilinear resampling
                raw_grid = src.read(
                    1,
                    out_shape=(out_height, out_width),
                    resampling=Resampling.bilinear
                ).astype(np.float32)

                # Clean nodata values below -100
                raw_grid[raw_grid < -100] = 0.0
                raw_grid = np.nan_to_num(raw_grid, nan=0.0)

                # Clip extreme 99th percentile sensor spikes (Shawal line 28-30)
                max_cap = np.percentile(raw_grid, 99)
                if max_cap > 0:
                    dem_grid = np.clip(raw_grid, 0, max_cap)
                else:
                    dem_grid = raw_grid

                z_grid = dem_grid

                # Normalize surfacecolor to 0.0 - 1.0 range (Shawal surfacecolor overlay)
                valid_vals = dem_grid[dem_grid > 0]
                if len(valid_vals) > 0:
                    c_min, c_max = np.percentile(valid_vals, 2), np.percentile(valid_vals, 98)
                    if c_max > c_min:
                        color_grid = np.clip((dem_grid - c_min) / (c_max - c_min), 0.0, 1.0)
                    else:
                        color_grid = dem_grid
                else:
                    color_grid = dem_grid

                color_label = "Radar Backscatter (dB)"
                z_desc = "output_hh.tif Bilinear Resampled (Step 15)"

        except Exception as err:
            print(f"[visualizer_3d] Error loading output_hh.tif: {err}")

    # Fallback to physical DEM if dem.tif is present
    if z_grid is None and dem_path and RASTERIO_AVAILABLE:
        try:
            with rasterio.open(dem_path) as src:
                step = 15
                out_height = max(1, int(src.height / step))
                out_width = max(1, int(src.width / step))

                dem_grid = src.read(
                    1,
                    out_shape=(out_height, out_width),
                    resampling=Resampling.bilinear
                ).astype(np.float32)

                dem_grid[dem_grid < -100] = 0.0
                dem_grid = np.nan_to_num(dem_grid, nan=0.0)

                max_cap = np.percentile(dem_grid, 99)
                if max_cap > 0:
                    dem_grid = np.clip(dem_grid, 0, max_cap)

                z_grid = dem_grid
                color_grid = input_values[:out_height, :out_width] if input_values.shape[0] >= out_height else dem_grid
                color_label = f"{label} ({units})"
                z_desc = "dem.tif Bilinear Resampled"
        except Exception as err:
            print(f"[visualizer_3d] Error loading dem.tif: {err}")

    # Final fallback if files are unavailable
    if z_grid is None:
        if has_dem_flag:
            z_grid = data["z_elevation"]
            color_grid = input_values
            z_desc = "Physical DEM Terrain"
        else:
            z_grid = np.nan_to_num(input_values, nan=0.0)
            color_grid = z_grid
            z_desc = "Relative Measurement Terrain"
        color_label = f"{label} ({units})"

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
