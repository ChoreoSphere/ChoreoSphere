import os
from dotenv import load_dotenv

load_dotenv()

# API and File Path Configurations
DEFAULT_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/dem/heatmap")
DEFAULT_GRANULE_PATH = os.getenv("granule_path", "")

# Default visualization settings
DEFAULT_DOWNSAMPLE_STEP = int(os.getenv("VIS_DOWNSAMPLE_STEP", "10"))
DEFAULT_COLORSCALE = "Viridis"
NEUTRAL_DATA_LABEL = "Relative NISAR Measurement (dB)"
