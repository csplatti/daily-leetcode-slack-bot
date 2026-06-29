import requests
from slack_sdk import WebClient
import os
from datetime import datetime, timezone, timedelta
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
API_URL = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:8000")

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
    try:
        if command == "/leetcode-link":
            # call your API to link user_id + team_id -> text
            return make_response(f"Linked {text}", 200)
        elif command == "/leaderboard":
            return get_leaderboard(team_id)
        elif command == "/join-tracker":
            lc_username = (text or "").strip()
            if not lc_username:
                return jsonify({
                    "response_type": "ephemeral",
                    "text": "Usage: `/join-tracker <your-leetcode-username>`\nExample: `/join-tracker csplatti`",
                })

            result = client.users_info(user=user_id)
            real_name = result["user"]["profile"]["real_name"]

            payload = {
                "workspace_id": team_id,
                "slack_id": user_id,
                "leetcode_username": lc_username,
            }
            resp = requests.post(API_URL + "/add-to-tracker", json=payload)
            if resp.status_code == 409:
                return jsonify({
                    "response_type": "ephemeral",
                    "text": "You're already on the tracker! Try `/leaderboard` to see how you're doing.",
                })
            db_res = resp.json()['res']

            num_solved_today = requests.get(f"{API_URL}/{team_id}/{user_id}/num-solved-today").json()['res']
            current_streak = db_res['current_streak'] + (1 if num_solved_today > 0 else 0)
            today_badge = f"✅ +{num_solved_today} today" if num_solved_today > 0 else "⭕ today"

            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🎉 You're in!", "emoji": True},
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"Welcome, *{real_name}* — tracking `{db_res['leetcode_username']}` on LeetCode."}
                    ],
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔥 *Current Streak:* {current_streak}   |   🏆 *Max Streak:* {db_res['max_streak']}   |   {today_badge}",
                    },
                },
            ]

            return jsonify({
                "response_type": "ephemeral",
                "text": f"Welcome, {real_name}!",
                "blocks": blocks,
            })
        elif command == "/quit":
            return remove_user(user_id, team_id)
        elif command == "/test":
            res = requests.get(API_URL + "/test-update")
            return jsonify({"response_type": "ephemeral", "text": res.status_code})
        return make_response("Command Not Recognized", 400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return make_response(f"An Error Occured: {e}", 500)

def remove_user(user_id: str, team_id: str):
    res = requests.delete(f"{API_URL}/{team_id}/{user_id}").json()
    rows_deleted = res.get("res", 0)

    if rows_deleted == 0:
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤔 Not on the tracker", "emoji": True},
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "You're not currently tracked. Use `/join-tracker <leetcode-username>` to start your streak."}
                ],
            },
        ]
        return jsonify({
            "response_type": "ephemeral",
            "text": "You're not currently on the tracker.",
            "blocks": blocks,
        })

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "👋 You're out!", "emoji": True},
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "Your streak data has been cleared. Come back anytime with `/join-tracker`."}
            ],
        },
    ]
    return jsonify({
        "response_type": "ephemeral",
        "text": "Removed — come back soon!",
        "blocks": blocks,
    })

RANK_PREFIXES = {0: "🥇", 1: "🥈", 2: "🥉"}

def get_leaderboard(team_id: str):
    query_result = requests.get(f"{API_URL}/{team_id}/leaderboard/").json()
    res = sorted(query_result['res'], key=lambda x: x['current_streak'], reverse=True)

    lines = []
    for i, row in enumerate(res):
        lines.append(get_leaderboard_line(i, row["current_streak"], row["max_streak"], row["slack_id"], row["workspace_id"], row["lc_username"]))

    now = datetime.now(timezone.utc)
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = next_midnight - now
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🏆 Leaderboard!", "emoji": True},
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"⏰ *{hours}h {minutes}m left* to solve today's problem — streaks reset at midnight UTC"}
            ],
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
    app.run(debug=True, host="0.0.0.0", port=5001)