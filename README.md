# NISAR Temporal Change & 3D Visualization Platform

An open-source platform to process, analyze, and visualize Earth surface changes over time using NASA-ISRO Synthetic Aperture Radar (NISAR) data. The project provides an end-to-end pipeline and an interactive 3D web visualizer for temporal SAR time-series and surface displacement products.

## Table of contents

- Project overview
- Quickstart (backend)
- Project layout
- Development notes
- Contributing
- License & contact

## Project overview

NISAR produces repeat-pass SAR observations suited for monitoring land deformation, glaciers, forest dynamics, and other surface changes. This repository contains tools to ingest NISAR granules, run SAR/InSAR processing steps, serve geospatial tiles and time-series via a FastAPI backend, and visualize results in a 3D web UI.

## Quickstart (backend)

Follow these minimal steps to run the backend locally and verify the core API.

1) Place a NISAR granule (.h5) on your machine. Example filename:

```
NISAR_L2_PR_GCOV_030_165_A_043_0005_NASV_A_20260917T152657_20260917T152728_P05023_N_F_J_001.h5
```

Download the exact granule used in this README from NASA Earthdata Search:

[Download granule on NASA Earthdata Search](https://search.earthdata.nasa.gov/search/granules?p=C2854338529-ASF&pg[0][v]=f&pg[0][id]=NISAR_L2_PR_GCOV_030_165_A_043_0005_NASV_A_20260917T152657_20260917T152728_P05023_N_F_J_001&pg[0][gsk]=-start_date&g=G4316546578-ASF&q=nisar&lat=63.00126139171006&long=145.4354896411795&zoom=4.701546331828165)

Note: an Earthdata login is required to download.

2) Create and activate a Python virtual environment

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Ubuntu (if `python` maps to Python 2, install `python3-venv` first):

```bash
sudo apt update && sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
```

Windows Command Prompt:

```cmd
python -m venv venv
venv\Scripts\activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3) Install dependencies

Linux / macOS / Ubuntu (inside the activated virtualenv):

```bash
pip install -r requirements.txt
```

Windows (Command Prompt / PowerShell, inside the activated virtualenv):

```powershell
pip install -r requirements.txt
```

4) Create a `.env` file in the repository root and set the absolute path to your granule. Example (Linux/macOS):

```
granule_path="/home/yourusername/Downloads/your_nisar_file.h5"
```

On Windows use a Windows-style absolute path, e.g. `C:/Users/you/Downloads/your_nisar_file.h5`.

5) Start the FastAPI development server from the project root

Linux / macOS / Ubuntu:

```bash
uvicorn src.backend.main:app --reload
```

Windows (Command Prompt / PowerShell):

```powershell
python -m uvicorn src.backend.main:app --reload
```

The API will be available at http://127.0.0.1:8000.

6) Verify a simple endpoint (example)

Linux / macOS / Ubuntu (curl):

```bash
curl "http://127.0.0.1:8000/api/dem/heatmap?utm_source=gemini"
```

Windows (PowerShell):

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/dem/heatmap?utm_source=gemini"
```

Windows (Command Prompt using curl if available):

```cmd
curl "http://127.0.0.1:8000/api/dem/heatmap?utm_source=gemini"
```

If configured correctly, the endpoint should return a JSON payload representing the DEM/heatmap matrix derived from the granule.

## Quickstart (3D visualization)

The steps above get the backend running. To generate the interactive 3D terrain + radar visualization, a few extra pieces are needed.

1) Get the elevation data (Copernicus GLO-30 DEM) and save it as `data/output_hh.tif` in the repository root. The file is ~256 MB, so it is not stored in git; every teammate downloads it once, the same way as the NISAR granule.

Area covered by the DEM we use (WGS 84 / EPSG:4326):

| West | East | South | North |
| --- | --- | --- | --- |
| 140.4 | 153.0 | 74.0 | 77.0 |

Download it from [OpenTopography](https://portal.opentopography.org/) (free account, then request an API key from your account page):

Linux / macOS / Ubuntu:

```bash
mkdir -p data
curl -o data/output_hh.tif "https://portal.opentopography.org/API/globaldem?demtype=COP30&south=74&north=77&west=140.4&east=153.0&outputFormat=GTiff&API_Key=YOUR_API_KEY"
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force data
Invoke-WebRequest -Uri "https://portal.opentopography.org/API/globaldem?demtype=COP30&south=74&north=77&west=140.4&east=153.0&outputFormat=GTiff&API_Key=YOUR_API_KEY" -OutFile data\output_hh.tif
```

Or use the website: Data > Global DEMs > Copernicus GLO-30, enter the bounds above, choose GeoTIFF, and save the result as `data/output_hh.tif`. Never commit your API key. If the download is only a few KB, open it in a text editor; it will contain an error message (bad key, area too large, etc.).

**Where the file goes (folder layout):**

```
ChoreoSphere/              <- repository root (the folder containing README.md)
├── data/                  <- create this folder if it doesn't exist
│   ├── output_hh.tif      <- the DEM you download or receive goes HERE (exact name)
│   └── dem_matched.tif    <- created automatically in step 2 below
├── src/
├── .env
└── README.md
```

Already have the DEM file from a teammate (shared link, USB, etc.) instead of downloading it? Skip the download commands: create the `data` folder, copy the file into it, and rename it to exactly `output_hh.tif`. Then continue with the check below.

Check that the file landed in the right part of the world :

```bash
python -c "import rasterio; s=rasterio.open('data/output_hh.tif'); print(s.crs, s.bounds, s.width, s.height)"
```

Expected: `EPSG:4326`, bounds of about left 140.4 / bottom 74.0 / right 153.0 / top 77.0, size 45360 x 10800. Anything else means the wrong file.

Known limitation: the public COP30 download stops at 77.00 degrees north, slightly short of the full study area, so pixels beyond that edge have no elevation data.

2) Align the DEM to the NISAR grid. The DEM and the radar file are usually stored in different map projections, so they need to be reprojected onto the same pixel grid before they can be combined. Run this once, from the repository root, after your `.env` and `data/output_hh.tif` are both in place:

```bash
python src/frontend/match_dem_to_radar.py
```

This reads the exact grid definition already stored inside your NISAR `.h5` file and produces a new file, `data/dem_matched.tif`, that lines up with it pixel-for-pixel. `src/frontend/map/visualizer_3d.py` looks for this file automatically.

3) Generate the interactive visualization:

```bash
python -m src.frontend.main_visualization
```

This produces `nisar_visualization.html` in the repository root, containing both the 2D heatmap and the 3D terrain + radar overlay. Open it directly in a browser.

Note: `data/`, `*.tif`, and `.env` are all gitignored on purpose, since they're either large binary files or contain machine-specific paths. Nothing under `data/` is shared through git — each teammate sources their own DEM and points `.env` at their own local granule.
## Project layout

- `src/backend/` — FastAPI backend, processing pipelines, and geospatial API endpoints
- `src/backend/pipelines/` — SAR/InSAR and surface-layer processing scripts
- `src/frontend/` — 3D visualizer, UI components and map client
- `requirements.txt` — Python dependencies

## Development notes

- Use Python 3.10+ and Node.js v18+ for local development.
- Processing large `.h5` granules can be memory- and CPU-intensive. For production-scale processing consider chunking, tiled workflows, or cloud VMs with larger RAM.
- Environment variables and absolute paths should be used for any local data files to avoid accidental commits of large binaries.

## Contributing

- Branching: create a feature branch off `main` (e.g. `feature/ingest-stream`).
- Pull Requests: open PRs targeting `main`; a sub-team lead should review before merging.
- Issues: file bug reports or feature requests with reproducible steps and small sample data when possible.

If you'd like help writing a contribution guide, CI checks, or sample notebooks to reproduce results, open an issue or request a PR.

## License & contact

This project is provided under the terms of the repository license (see `LICENSE`). For questions, open an issue or contact the maintainers via the repository discussion board.

---

If you want, I can also add a short `CONTRIBUTING.md`, API examples, or update `requirements.txt` to pin tested versions.
