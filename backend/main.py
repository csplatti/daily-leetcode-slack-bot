# REST API endpoints
from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import requests
import db
import leetcode as lc

app = FastAPI()

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

class LinkRequest(BaseModel):
    workspace_id: str
    slack_id: str
    leetcode_username: str

def run_daily_update():
    for user_row in db.get_all_users():
        workspace_id = user_row["workspace_id"]
        slack_id = user_row["slack_id"]

        if lc.num_solved_yesterday(user_row["lc_username"]) > 0:
            db.add_daily(workspace_id, slack_id)
        else:
            db.reset_user(workspace_id, slack_id)

# GET requests
@app.get("/{workspace_id}/leaderboard")
def get_leaderboard(workspace_id: str):
    res = db.get_workspace_users(workspace_id)
    return {"added": "success", "res": res}

@app.get("/{workspace_id}/{user_id}/num-solved-today")
def get_num_solved_today(workspace_id: str, user_id: str):
    user_obj = db.fetch_user(workspace_id, user_id)
    print(user_obj)
    return {"res": lc.user_num_solved_today(user_obj["leetcode_username"])}

# POST requests
@app.post("/add-to-tracker")
def add_to_tracker(payload: LinkRequest):
    db.add_user(payload.workspace_id, payload.slack_id, payload.leetcode_username)
    res = db.fetch_user(payload.workspace_id, payload.slack_id)
    return {
        "added": "linked",
        "res": res,
        "leetcode_username": payload.leetcode_username,
    }

# DELETE requests
@app.delete("/{workspace_id}/{user_id}")
def remove_user(workspace_id: str, user_id: str):
    res = db.remove_user(workspace_id, user_id)
    return {"removed": "success", "res": res}
