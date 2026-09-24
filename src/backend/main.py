from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipelines.surfacelayer import get_heatmap_matrix

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dem/heatmap")
def get_heatmap():
    """Returns the NISAR radar displacement heatmap matrix."""
    matrix = get_heatmap_matrix()
    if hasattr(matrix, "tolist"):
        matrix = matrix.tolist()
        
    return {"heatmap_matrix": matrix}