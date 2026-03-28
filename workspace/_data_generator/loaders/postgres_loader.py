import psycopg2
from psycopg2.extras import execute_batch


def pg_connect(conn_string: str):
    return psycopg2.connect(conn_string)


def build_insert_query(table: str, columns: list[str]) -> str:
    cols = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    return f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"


def load_to_postgres(conn, table: str, records, batch_size=1000):
    """
    Uses batch insert (Postgres optimized)
    """

    records = list(records)
    if not records:
        return

    columns = list(records[0].keys())
    query = build_insert_query(table, columns)

    values = [tuple(r[c] for c in columns) for r in records]

    with conn.cursor() as cur:
        execute_batch(cur, query, values, page_size=batch_size)

    conn.commit()
