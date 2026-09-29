import h5py
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

h5_file = os.getenv("granule_path")


def get_heatmap_matrix():
    if not h5_file or not os.path.exists(h5_file):
        print("ERROR: HDF5 file path not found or does not exist!")
        return np.random.rand(10, 10)

    with h5py.File(h5_file, "r") as f:
        matrix = np.array(f["science/LSAR/GCOV/grids/frequencyB/VVVV"])
        matrix = 10 * np.log10(matrix)
        return matrix