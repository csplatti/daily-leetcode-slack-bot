import requests

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