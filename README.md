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
