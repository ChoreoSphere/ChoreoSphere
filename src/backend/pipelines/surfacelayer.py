import h5py
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

h5_file = os.getenv("granule_path") 
print(h5_file)
def get_heatmap_matrix():
    with h5py.File(h5_file, "r") as f:
        matrix = np.array(f["science/LSAR/GCOV/grids/frequencyB/VVVV"])
        matrix =  10*np.log(matrix)
        # plt.figure(figsize = (10,16))
        # plt.imshow(matrix, cmap='gray')
        # plt.show()
        return matrix

