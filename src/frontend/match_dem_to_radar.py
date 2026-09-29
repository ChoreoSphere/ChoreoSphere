import os
import h5py
import numpy as np
import rasterio
from dotenv import load_dotenv
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin

load_dotenv()

# Paths come from .env and the project's data folder, so this works on any computer.
# Run from the project root:  python src\frontend\match_dem_to_radar.py
h5_path = os.getenv("granule_path")
dem_path = os.path.join("data", "output_hh.tif")
output_path = os.path.join("data", "dem_matched.tif")

if not h5_path or not os.path.exists(h5_path):
    raise SystemExit("granule_path is missing or wrong in .env")
if not os.path.exists(dem_path):
    raise SystemExit(f"DEM not found at {dem_path}")

# Pull the exact target grid definition from the NISAR file
with h5py.File(h5_path, "r") as f:
    grp = f["science/LSAR/GCOV/grids/frequencyB"]
    x_coords = grp["xCoordinates"][:]
    y_coords = grp["yCoordinates"][:]
    epsg = int(grp["projection"][()])

dst_crs = f"EPSG:{epsg}"
dst_height = len(y_coords)
dst_width = len(x_coords)
x_res = x_coords[1] - x_coords[0]
y_res = y_coords[1] - y_coords[0]
dst_transform = from_origin(x_coords[0] - x_res / 2, y_coords[0] - y_res / 2, x_res, -y_res)

with rasterio.open(dem_path) as src:
    dst_array = np.empty((dst_height, dst_width), dtype=np.float32)
    reproject(
        source=rasterio.band(src, 1),
        destination=dst_array,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear,
    )
    kwargs = src.meta.copy()
    kwargs.update({
        "crs": dst_crs, "transform": dst_transform,
        "height": dst_height, "width": dst_width, "dtype": "float32",
    })
    with rasterio.open(output_path, "w", **kwargs) as dst:
        dst.write(dst_array, 1)

print(f"Done. Aligned DEM saved to {output_path}")
print(f"Shape: {dst_array.shape}")