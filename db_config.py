"""
Database connection manager — thread-safe MySQL connector pool.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import mysql.connector
from mysql.connector import pooling
from config.settings import DB_CONFIG

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="sas_pool",
            pool_size=5,
            **DB_CONFIG,
        )
    return _pool


def get_connection():
    """Return a pooled connection. Caller must close() when done."""
    return get_pool().get_connection()


def execute_query(sql: str, params: tuple = (), fetch: bool = False):
    """
    Run a single query.
    fetch=True  → return list of dicts
    fetch=False → return lastrowid
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def test_connection():
    try:
        conn = get_connection()
        conn.close()
        print("✅ Database connection successful.")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
