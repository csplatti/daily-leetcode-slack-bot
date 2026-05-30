# REST API endpoints
from fastapi import FastAPI
from pydantic import BaseModel
import requests
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

class LinkRequest(BaseModel):
    workspace_id: str
    slack_id: str
    leetcode_username: str

@app.post("/add-to-tracker")
def add_to_tracker(payload: LinkRequest):
    print(payload)
    db.add_user(payload.workspace_id, payload.slack_id, payload.leetcode_username)
    res = db.fetch_user(payload.workspace_id, payload.slack_id)
    return {"added": "linked", "res": res, "leetcode_username": payload.leetcode_username}
