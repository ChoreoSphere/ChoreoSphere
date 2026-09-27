import os
import requests
import numpy as np
import h5py
from typing import Dict, Any, Optional
from src.frontend.config import DEFAULT_API_URL, DEFAULT_GRANULE_PATH, DEFAULT_DOWNSAMPLE_STEP, NEUTRAL_DATA_LABEL


def process_matrix_to_db(matrix: np.ndarray) -> np.ndarray:
    """
    Converts linear SAR backscatter covariance/intensity matrix to decibel (dB) scale.
    Replaces non-positive or missing values with NaN.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        db_matrix = 10.0 * np.log10(np.where(matrix > 0, matrix, np.nan))
    return db_matrix


def load_from_hdf5(
    file_path: Optional[str] = None,
    downsample_step: int = DEFAULT_DOWNSAMPLE_STEP
) -> Dict[str, Any]:
    """
    Loads NISAR HDF5 data locally from the given file path (or granule_path env var).
    Applies downsampling to optimize performance and browser memory.
    """
    h5_path = file_path or DEFAULT_GRANULE_PATH or os.getenv("granule_path", "")
    if not h5_path or not os.path.exists(h5_path):
        raise FileNotFoundError(f"HDF5 file path not found: '{h5_path}'. Check your .env granule_path setting.")

    with h5py.File(h5_path, "r") as f:
        # Check standard NISAR GCOV datasets
        grid_key = "science/LSAR/GCOV/grids/frequencyB/VVVV"
        if grid_key not in f:
            # Fallback search for any frequency grid
            grid_keys = [k for k in f if "grids" in k]
            raise KeyError(f"Dataset '{grid_key}' not found in HDF5 file.")

        raw_grid = f[grid_key]
        step = max(1, downsample_step)

        # Slice / downsample raster
        ds_matrix = np.array(raw_grid[::step, ::step], dtype=np.float32)

        # Load coordinates if available
        x_key = "science/LSAR/GCOV/grids/frequencyB/xCoordinates"
        y_key = "science/LSAR/GCOV/grids/frequencyB/yCoordinates"

        if x_key in f and y_key in f:
            x_coords = np.array(f[x_key][::step], dtype=np.float64)
            y_coords = np.array(f[y_key][::step], dtype=np.float64)
        else:
            y_len, x_len = ds_matrix.shape
            x_coords = np.arange(x_len, dtype=np.float64)
            y_coords = np.arange(y_len, dtype=np.float64)

        # Process linear values into dB scale
        values_db = process_matrix_to_db(ds_matrix)

        # Check for DEM / terrain elevation grid
        has_dem = False
        z_elevation = np.zeros_like(values_db)
        if "science/LSAR/GCOV/grids/frequencyB/height" in f:
            z_elevation = np.array(f["science/LSAR/GCOV/grids/frequencyB/height"][::step, ::step], dtype=np.float32)
            has_dem = True

        return {
            "x": x_coords,
            "y": y_coords,
            "z_elevation": z_elevation,
            "values": values_db,
            "has_dem": has_dem,
            "units": "dB",
            "label": NEUTRAL_DATA_LABEL,
            "source": f"Local HDF5 ({os.path.basename(h5_path)})",
            "metadata": {
                "original_shape": raw_grid.shape,
                "downsampled_shape": values_db.shape,
                "downsample_step": step,
            }
        }


def fetch_from_api(
    api_url: str = DEFAULT_API_URL,
    downsample_step: int = DEFAULT_DOWNSAMPLE_STEP
) -> Dict[str, Any]:
    """
    Attempts to fetch visualization data from the FastAPI backend endpoint.
    If the endpoint returns raw or un-downsampled data, formats and downsamples it.
    """
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    payload = response.json()

    # If backend returns heatmap_matrix
    if "heatmap_matrix" in payload:
        raw_matrix = np.array(payload["heatmap_matrix"], dtype=np.float32)
        step = max(1, downsample_step)
        ds_matrix = raw_matrix[::step, ::step]
        values_db = process_matrix_to_db(ds_matrix)

        y_len, x_len = values_db.shape
        return {
            "x": np.arange(x_len, dtype=np.float64),
            "y": np.arange(y_len, dtype=np.float64),
            "z_elevation": np.zeros_like(values_db),
            "values": values_db,
            "has_dem": False,
            "units": "dB",
            "label": NEUTRAL_DATA_LABEL,
            "source": f"FastAPI Endpoint ({api_url})",
            "metadata": {
                "downsampled_shape": values_db.shape,
                "downsample_step": step,
            }
        }

    # Standardized API response format
    values_matrix = np.array(payload.get("values", []), dtype=np.float32)
    x_coords = np.array(payload.get("x", np.arange(values_matrix.shape[1] if values_matrix.ndim > 1 else 0)))
    y_coords = np.array(payload.get("y", np.arange(values_matrix.shape[0] if values_matrix.ndim > 1 else 0)))
    z_elevation = np.array(payload.get("z_elevation", np.zeros_like(values_matrix)))

    return {
        "x": x_coords,
        "y": y_coords,
        "z_elevation": z_elevation,
        "values": values_matrix,
        "has_dem": payload.get("has_dem", False),
        "units": payload.get("units", "dB"),
        "label": payload.get("label", NEUTRAL_DATA_LABEL),
        "source": f"FastAPI Endpoint ({api_url})",
        "metadata": payload.get("metadata", {})
    }


def get_visualization_data(
    use_api: bool = True,
    api_url: str = DEFAULT_API_URL,
    h5_path: Optional[str] = None,
    downsample_step: int = DEFAULT_DOWNSAMPLE_STEP
) -> Dict[str, Any]:
    """
    Main data retrieval interface for the Visualization Team frontend.
    Tries API first if requested; falls back to local HDF5 file if API is unavailable or fails.
    """
    if use_api:
        try:
            return fetch_from_api(api_url=api_url, downsample_step=downsample_step)
        except Exception as err:
            print(f"[Visualization DataProvider] FastAPI endpoint fetch failed ({err}). Falling back to local HDF5.")

    return load_from_hdf5(file_path=h5_path, downsample_step=downsample_step)
