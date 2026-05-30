import requests
import slack
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

client.chat_postMessage(channel='#daily-leetcoders', text="Hello!")


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