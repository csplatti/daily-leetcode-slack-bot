import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def connect():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ.get("DB_PASSWORD"),
    )

def getWorkspaceUsers(workspace_id: str):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute(
        "SELECT slack_user_id, leetcode_username, current_streak, max_streak "
        "FROM users WHERE workspace_id = %s",
        (workspace_id,),
        )
        rows = cur.fetchall()
    conn.close()
    return rows