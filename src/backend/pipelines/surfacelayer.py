import h5py
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

h5_file = os.getenv("granule_path")

def get_heatmap_matrix():
    if not h5_file or not os.path.exists(h5_file):
        print("ERROR: HDF5 File path nahi mila ya file exist nahi karti!")
        return np.random.rand(10, 10).tolist()

    with h5py.File(h5_file, "r") as f:
        matrix = np.array(f["science/LSAR/GCOV/grids/frequencyB/VVVV"])
        matrix = np.nan_to_num(matrix)
        matrix = 10 * np.log10(np.maximum(matrix, 1e-10))
        
        return matrix

