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
    return [{
        "slack_id": row[0], 
        "lc_username": row[1],
        "current_streak": row[2],
        "max_streak": row[3]} for row in rows]

def add_user(workspace_id: str, slack_id: str, lc_username: str):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute(
        """
        INSERT INTO users (workspace_id, slack_user_id, leetcode_username)
        VALUES (%s, %s, %s);
        """, 
        (workspace_id, slack_id, lc_username))
    
    conn.commit()
    conn.close()

def remove_user(workspace_id: str, slack_id: str):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE workspace_id = %s AND slack_user_id = %s",
                (workspace_id, slack_id),
            )
            deleted = cur.rowcount
            conn.commit()
    finally:
        conn.close()
    return deleted
    


def fetch_user(workspace_id: str, slack_id: str):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute(
        """
            SELECT slack_user_id, leetcode_username, current_streak, max_streak
            FROM users
            WHERE workspace_id = %s AND slack_user_id = %s;
        """,
        (workspace_id, slack_id))
        res = cur.fetchall()[0]
        print(res)

    conn.close()
    return {
        "leetcode_username": res[1],
        "current_streak": res[2],
        "max_streak": res[3]
    }
