import requests
from datetime import datetime, timezone, timedelta

LC_USER_BASE_URL = "https://leetcode.com/graphql"
TEST_USER = "csplatti"

def get_ac_request(username: str):
    return {
        "query": "\n    query recentAcSubmissions($username: String!, $limit: Int!) {\n  recentAcSubmissionList(username: $username, limit: $limit) {\n    id\n    title\n    titleSlug\n    timestamp\n  }\n}\n    ",
        "variables": {
            "username": username,
            "limit": 15
        },
        "operationName": "recentAcSubmissions"
    }


def get_user_data(username: str):
    URL = LC_USER_BASE_URL # + "/" + TEST_USER
    JSON = get_ac_request(username)
    HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Referer": "https://leetcode.com",
    }

    data = requests.post(URL, json=JSON, headers=HEADERS).json()
    return data['data']['recentAcSubmissionList']

def user_num_solved_today(username: str):
    today = datetime.today().date()
    return len(get_solved_on_date(username, today))

def get_solved_on_date(username: str, date: datetime):
    WANTED_KEYS = ["title", "titleSlug", "timestamp"]
    data = get_user_data(username)
    for row in data:
        row["timestamp"] = datetime.fromtimestamp(int(row["timestamp"]), tz=timezone.utc).date()
    data = filter(lambda row: row["timestamp"] == date, data)
    return [{key: row[key] for key in WANTED_KEYS} for row in data]

def num_solved_yesterday(username: str):
    yestr_date = datetime.today().date() - timedelta(days=1)
    return len(get_solved_on_date(username, yestr_date))