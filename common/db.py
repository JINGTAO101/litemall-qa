import pymysql

from common.config import load_config

def query_one(sql,args=None):
    cfg = load_config()["db"]
    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql,args)
            return cur.fetchone()
    finally:
        conn.close()