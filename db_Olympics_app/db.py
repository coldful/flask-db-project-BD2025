import logging
import sqlite3
import re
import os

DB = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Use the Olympics database that ships with the APP folder
DB_FILE = os.path.join(BASE_DIR, "Olympics.db")

def connect():
    global DB
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    DB['conn'] = conn
    DB['cursor'] = conn.cursor()
    logging.info(f"Connected to database: {DB_FILE}")

def execute(sql, args=None):
    sql = re.sub(r'\s+', ' ', sql).strip()
    logging.info(f"SQL: {sql} | Args: {args}")
    if args:
        return DB['cursor'].execute(sql, args)
    return DB['cursor'].execute(sql)

def close():
    DB['conn'].close()
