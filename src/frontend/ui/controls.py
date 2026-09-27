from typing import Dict, Any, List

AVAILABLE_COLORSCALES: List[str] = [
    "Viridis",
    "Plasma",
    "Cividis",
    "Magma",
    "Inferno",
    "RdBu_r",
    "Greys",
    "Earth"
]

DOWNSAMPLE_PRESETS: Dict[str, int] = {
    "High Detail (1:5)": 5,
    "Standard (1:10)": 10,
    "Fast Overview (1:20)": 20,
    "Ultra Fast (1:40)": 40,
}


def format_metadata_summary(data: Dict[str, Any]) -> str:
    """
    Returns a human-readable text summary of the visualization data metadata.
    """
    source = data.get("source", "Unknown")
    label = data.get("label", "Relative NISAR Measurement")
    units = data.get("units", "dB")
    has_dem = data.get("has_dem", False)
    meta = data.get("metadata", {})

    downsampled_shape = meta.get("downsampled_shape", "N/A")
    downsample_step = meta.get("downsample_step", 1)

    summary = (
        f"<b>Dataset Source:</b> {source}<br>"
        f"<b>Data Label:</b> {label}<br>"
        f"<b>Units:</b> {units}<br>"
        f"<b>DEM Elevation Status:</b> {'Available' if has_dem else 'Not Present (Using Flat Geometry)'}<br>"
        f"<b>Visualization Matrix Dimensions:</b> {downsampled_shape}<br>"
        f"<b>Downsampling Step Factor:</b> {downsample_step}x"
    )
    return summary
