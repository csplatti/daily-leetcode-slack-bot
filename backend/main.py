# REST API endpoints
from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import requests
import db
import leetcode as lc

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        run_daily_update,
        CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="daily_update",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI()

@app.get("/test-update")
def run_daily_update():
    for user_row in db.get_all_users():
        workspace_id = user_row["workspace_id"]
        slack_id = user_row["slack_id"]
        # db.add_daily(workspace_id, slack_id)
        # db.reset_user(workspace_id, slack_id)
        if lc.num_solved_yesterday(user_row["lc_username"]) > 0:
            db.add_daily(workspace_id, slack_id)
        else:
            db.reset_user(workspace_id, slack_id)

    return {"hello": "there"}

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

@app.get("/leaderboard/{workspace_id}")
def get_leaderboard(workspace_id: str):
    res = db.getWorkspaceUsers(workspace_id)
    print(res)
    return {"added": "success", "res": res}

@app.post("/remove/{workspace_id}/{user_id}")
def remove_user(workspace_id: str, user_id: str):
    res = db.remove_user(workspace_id, user_id)
    print(res)
    return {"removed": "success", "res": res}
