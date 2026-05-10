import pymysql
from config import Config


def conn():
    con = pymysql.connect(host=Config.DB_HOST, port=Config.DB_PORT,
                          user=Config.DB_USER, password=Config.DB_PASSWORD, db=Config.DB_NAME)
    cur = con.cursor()
    return con, cur


def query(sql):
    con, cur = conn()
    try:
        cur.execute(sql)
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


def insert(sql):
    con, cur = conn()
    try:
        cur.execute(sql)
        con.commit()
    finally:
        cur.close()
        con.close()
