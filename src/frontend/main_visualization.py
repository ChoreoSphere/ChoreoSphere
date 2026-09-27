import os
import argparse
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, Optional

from src.frontend.config import (
    DEFAULT_API_URL,
    DEFAULT_GRANULE_PATH,
    DEFAULT_DOWNSAMPLE_STEP,
    DEFAULT_COLORSCALE
)
from src.frontend.data_provider import get_visualization_data, load_from_hdf5, fetch_from_api
from src.frontend.map.visualizer_2d import build_2d_heatmap
from src.frontend.map.visualizer_3d import build_3d_surface
from src.frontend.ui.controls import format_metadata_summary, AVAILABLE_COLORSCALES, DOWNSAMPLE_PRESETS


def create_visualization_figures(
    data: Dict[str, Any],
    colorscale: str = DEFAULT_COLORSCALE
) -> Tuple[go.Figure, go.Figure]:
    """
    Creates both 2D Heatmap and 3D Surface Plotly figures for the given visualization data.

    Returns:
    --------
    Tuple[go.Figure, go.Figure]
        (fig_2d, fig_3d)
    """
    fig_2d = build_2d_heatmap(data, colorscale=colorscale)
    fig_3d = build_3d_surface(data, colorscale=colorscale)
    return fig_2d, fig_3d


def generate_interactive_html(
    fig_2d: go.Figure,
    fig_3d: go.Figure,
    data_summary: str,
    output_filename: str = "nisar_visualization.html"
) -> str:
    """
    Combines 2D and 3D Plotly visualizations into a single self-contained interactive HTML file.
    """
    html_2d = fig_2d.to_html(full_html=False, include_plotlyjs="cdn")
    html_3d = fig_3d.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChoreoSphere - NISAR 2D/3D Visualization</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .header {{
            text-align: center;
            padding: 15px;
            background: #1e293b;
            color: #fff;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 0;
            font-size: 14px;
            color: #94a3b8;
        }}
        .summary-card {{
            background: #ffffff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-size: 14px;
            line-height: 1.6;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }}
        .tab-btn {{
            padding: 10px 24px;
            background: #e2e8f0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s ease;
        }}
        .tab-btn.active {{
            background: #2563eb;
            color: #ffffff;
        }}
        .vis-container {{
            background: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            min-height: 650px;
        }}
        .vis-panel {{
            display: none;
        }}
        .vis-panel.active {{
            display: block;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>ChoreoSphere - NISAR Earth Surface Visualization</h1>
        <p>Visualization Team Frontend Component | Plotly 2D & 3D Interactive Views</p>
    </div>

    <div class="summary-card">
        {data_summary}
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('view-2d', this)">2D Heatmap View</button>
        <button class="tab-btn" onclick="switchTab('view-3d', this)">3D Surface View</button>
    </div>

    <div class="vis-container">
        <div id="view-2d" class="vis-panel active">
            {html_2d}
        </div>
        <div id="view-3d" class="vis-panel">
            {html_3d}
        </div>
    </div>

    <script>
        function switchTab(panelId, btnElement) {{
            document.querySelectorAll('.vis-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
            btnElement.classList.add('active');
            
            // Trigger Plotly resize when tab switches
            window.dispatchEvent(new Event('resize'));
        }}
    </script>
</body>
</html>
"""
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_filename)


def run_cli():
    """
    CLI runner to execute data loading and produce interactive Plotly visualizations.
    """
    parser = argparse.ArgumentParser(description="ChoreoSphere NISAR Frontend Visualizer")
    parser.add_argument("--step", type=int, default=DEFAULT_DOWNSAMPLE_STEP, help="Downsampling step factor (default: 10)")
    parser.add_argument("--colorscale", type=str, default=DEFAULT_COLORSCALE, help="Plotly colorscale (default: Viridis)")
    parser.add_argument("--use-api", action="store_true", help="Attempt to fetch data from FastAPI endpoint first")
    parser.add_argument("--h5-path", type=str, default="", help="Path to local HDF5 file (overrides .env)")
    parser.add_argument("--output", type=str, default="nisar_visualization.html", help="Output HTML filename")

    args = parser.parse_args()

    print("\n==================================================")
    print("CHOREOSPHERE VISUALIZATION TEAM - FRONTEND")
    print("==================================================")

    data = get_visualization_data(
        use_api=args.use_api,
        api_url=DEFAULT_API_URL,
        h5_path=args.h5_path or None,
        downsample_step=args.step
    )

    print(f"Loaded data source: {data['source']}")
    print(f"Data dimensions: {data['values'].shape}")
    print(f"Units: {data['units']} | Label: {data['label']}")
    print(f"DEM Available: {data['has_dem']}")

    print("\nGenerating 2D and 3D Plotly visualizations...")
    fig_2d, fig_3d = create_visualization_figures(data, colorscale=args.colorscale)

    summary_text = format_metadata_summary(data)
    abs_output = generate_interactive_html(fig_2d, fig_3d, summary_text, output_filename=args.output)

    print(f"[OK] Interactive HTML visualization saved to:\n  {abs_output}")
    print("==================================================\n")


if __name__ == "__main__":
    run_cli()
