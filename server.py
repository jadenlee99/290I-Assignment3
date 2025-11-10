from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    global active_graph

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    filename = file.filename or ""
    if not filename.lower().endswith(".json"):
        return JSONResponse(status_code=400, content={"Upload Error": "Invalid file type"})

    try:
        file.file.seek(0)
        active_graph = create_graph_from_json(file)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid graph JSON: {exc}") from exc

    return {"Upload Success": filename}


@app.get("/solve_shortest__path/starting_node_id={starting_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(starting_node_id: str, end_node_id: str):
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    if (
        starting_node_id not in active_graph.nodes
        or end_node_id not in active_graph.nodes
    ):
        return {"Solver Error": "Invalid start or end node ID."}

    start_node = active_graph.nodes[starting_node_id]
    end_node = active_graph.nodes[end_node_id]

    dijkstra(active_graph, start_node)

    if np.isinf(end_node.dist):
        return {"shortest_path": None, "total_distance": None}

    path = []
    cursor = end_node
    while cursor:
        path.append(cursor.id)
        cursor = cursor.prev
    path.reverse()

    return {
        "shortest_path": path,
        "total_distance": float(end_node.dist),
    }

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
