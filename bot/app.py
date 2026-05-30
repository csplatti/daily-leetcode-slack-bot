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

# client.chat_postMessage(channel='#daily-leetcoders', text="Hello!")

if __name__ == "__main__":
    app.run(debug=True)

# @slack_event_adapter.on('message')
# def message(payload):
#     event = payload.get('event', {})
#     channel_id = event.get('channel')
#     user_id = event.get('user')
#     text = event.get('text')
#     if user_id != BOT_ID:
#         client.chat_postMessage(channel=channel_id, text=text)

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
        return jsonify({
            "response_type": "in_channel",   # only the sender sees this
            "text": f"Linked hello",
        })

    return make_response("", 200)



# TEST_URL = "http://127.0.0.1:8000/test"
# r = requests.get(TEST_URL)
# print(r)
# print(r.json())
TEST_WORKSPACE_ID = "000000"

# print("Workspace Participants:")
# GET_WS_URL = "http://127.0.0.1:8000/workspace-participants/" + TEST_WORKSPACE_ID
# r = requests.get(GET_WS_URL)
# print(r)
# print(r.json())

print("Workspace Streaks")
GET_WS_USR_INF_URL = "http://127.0.0.1:8000/workspace-streaks/" + TEST_WORKSPACE_ID
r = requests.get(GET_WS_USR_INF_URL)
print(r)
print(r.json())

# pull