# REST API endpoints
from fastapi import FastAPI
import db
import leetcode as lc

app = FastAPI()

@app.get("/test")
def test():
    return {"test": "successful"}

@app.get("/workspace-participants/{workspace_id}")
def get_workspace_participants(workspace_id: str):
    return db.getWorkspaceUsers(workspace_id)

@app.get("/workspace-streaks/{workspace_id}")
def get_workspace_streaks(workspace_id: str):
    return db.getWorkspaceUsers(workspace_id)
