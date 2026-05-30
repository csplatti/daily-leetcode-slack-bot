import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("DB_PORT", 5432)),
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ.get("DB_PASSWORD"),
)


with conn.cursor() as cur:
    cur.execute("SELECT * FROM users;")
    print(cur.fetchone())

conn.close()
