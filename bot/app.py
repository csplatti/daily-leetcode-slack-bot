import requests
from slack_sdk import WebClient
import os
from flask import Flask, request, make_response, jsonify
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter

env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'],'/slack/events',app)
client = WebClient(token=os.environ['SLACK_TOKEN'])

BOT_ID = client.api_call("auth.test")['user_id']
API_URL = "http://127.0.0.1:8000"

@slack_event_adapter.on('app_mention')
def message(payload):
    event = payload.get('event', {})

    channel_id = event.get('channel')
    user_id = event.get('user')

    text = event.get('text')

    if user_id != BOT_ID:
        client.chat_postMessage(channel=channel_id, text=text)

@app.route("/slack/commands", methods=["POST"])
def handle_commands():
    command = request.form.get("command")      # "/leetcode-link"
    text = request.form.get("text")            # "csplatti"
    user_id = request.form.get("user_id")
    team_id = request.form.get("team_id")      # your workspace scope

    if command == "/leetcode-link":
        # call your API to link user_id + team_id -> text
        return make_response(f"Linked {text}", 200)
    elif command == "/leaderboard":
        return get_leaderboard(team_id)
    elif command == "/join-tracker":
        lc_username = text
        result = client.users_info(user=user_id)
        username = result["user"]["name"]

        json = {
            "workspace_id": team_id,
            "slack_id": user_id,
            "leetcode_username": lc_username,
        }
        db_res = requests.post(API_URL + "/add-to-tracker", json=json).json()['res']
        print(db_res)
        return jsonify({
            "response_type": "ephemeral",
            # "db_response": db_response.json(),
            "text": (
            "Added!\n"
            f"Leetcode Username: {db_res["leetcode_username"]}\n"
            f"Current Streak: {db_res["current_streak"]}\n"
            f"Max Streak: {db_res["max_streak"]}"
            
            )
            # "text": db_response.text
        })
    elif command == "/quit":
        return remove_user(user_id, team_id)
    elif command == "/test":
        res = requests.get(API_URL + "/test-update")
        return jsonify({"response_type": "ephemeral", "text": res.status_code})
    return make_response("Command Not Recognized", 400)

def remove_user(user_id: str, team_id: str):
    res = requests.post(API_URL + "/remove/" + team_id + "/" + user_id).json()
    print(res)
    if res["removed"] == "success":
        return jsonify({"response_type": "ephemeral", "text": "Successful Removal. Come back soon!"})
    else:
        return jsonify({"response_type": "ephemeral", "text": "Removal Unsuccessful..."}) 

RANK_PREFIXES = {0: "🥇", 1: "🥈", 2: "🥉"}

def get_leaderboard(team_id: str):
    query_result = requests.get(API_URL + "/leaderboard/" + team_id).json()
    res = sorted(query_result['res'], key=lambda x: x['current_streak'], reverse=True)

    lines = []
    for i, row in enumerate(res):
        lines.append(get_leaderboard_line(i, row["current_streak"], row["max_streak"], row["slack_id"], row["workspace_id"], row["lc_username"]))

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🏆 Leaderboard", "emoji": True},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(lines) or "_No participants yet._"},
        },
    ]

    return jsonify({
        "response_type": "in_channel",
        "text": "Leaderboard 📊",
        "blocks": blocks,
    })

def get_leaderboard_line(rank: int, streak: int, max_streak: int, slack_id: str, workspace_id: str, lc_username: str):
    resp = client.users_info(user=slack_id)
    username = resp["user"]["profile"]["real_name"]
    num_solved_today = requests.get(f"{API_URL}/{workspace_id}/{slack_id}/num-solved-today").json()['res']

    if num_solved_today > 0:
        streak += 1

    prefix = RANK_PREFIXES.get(rank, f"`{rank + 1}.`")
    streak_emoji = "🔥" if streak > 0 else "🥀"
    today_badge = f"✅ +{num_solved_today} today" if num_solved_today > 0 else "⭕ today"
    parts = [f"{streak_emoji} {streak}", today_badge]
    if streak > 0 and streak == max_streak:
        parts.append("‼️ *PR*")

    return f"{prefix}  *{username}*  ·  " + "  ·  ".join(parts)
    # TODO: Implement better error handling


if __name__ == "__main__":
    app.run(debug=True, port=5001)