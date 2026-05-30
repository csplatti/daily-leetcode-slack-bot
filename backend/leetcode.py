import requests
from datetime import datetime, timezone, timedelta

LC_USER_BASE_URL = "https://leetcode.com/graphql"
TEST_USER = "csplatti"

def getACRequest(username: str):
    return {
        "query": "\n    query recentAcSubmissions($username: String!, $limit: Int!) {\n  recentAcSubmissionList(username: $username, limit: $limit) {\n    id\n    title\n    titleSlug\n    timestamp\n  }\n}\n    ",
        "variables": {
            "username": username,
            "limit": 15
        },
        "operationName": "recentAcSubmissions"
    }


def getUserData(username: str):
    URL = LC_USER_BASE_URL # + "/" + TEST_USER
    JSON = getACRequest(username)
    HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Referer": "https://leetcode.com",
    }

    data = requests.post(URL, json=JSON, headers=HEADERS).json()
    return data['data']['recentAcSubmissionList']

def getProblemsSolvedOnDate(username: str, date: datetime):
    WANTED_KEYS = ["title", "titleSlug", "timestamp"]
    data = getUserData(username)
    for row in data:
        row["timestamp"] = datetime.fromtimestamp(int(row["timestamp"]), tz=timezone.utc).date()
    data = filter(lambda row: row["timestamp"] == date, data)
    return [{key: row[key] for key in WANTED_KEYS} for row in data]

print(getProblemsSolvedOnDate("csplatti", datetime.today().date() - timedelta(days=2)))
