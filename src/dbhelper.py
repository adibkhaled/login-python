import os
import logging
import psycopg2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "appdb"),
    "user": os.environ.get("DB_USER", "appuser"),
    "password": os.environ.get("DB_PASSWORD", "apppassword"),
}


def get_connection():
    """Return a new psycopg2 connection using env config."""
    return psycopg2.connect(**DB_CONFIG)


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Execute SQL and optionally return results.
    - fetchone: return single row
    - fetchall: return list of rows
    - commit: commit transaction for insert/update/delete
    """
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if commit:
                    return True
                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()
                return None
    except Exception:
        logger.exception("Database error")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass