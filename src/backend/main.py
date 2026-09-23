from fastapi import FastAPI
from src.backend.pipelines import get_heatmap_matrix

app = FastAPI()


@app.get("/api/dem/heatmap")
def get_heatmap():
    "Returns the NISAR radar displacement heatmap matrix,"
    matrix = get_heatmap_matrix()
    return {"heatmap_matrix": matrix}