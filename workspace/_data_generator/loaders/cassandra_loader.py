from cassandra.cluster import Cluster
from cassandra.query import PreparedStatement


def cassandra_connect(hosts=None, keyspace="lab_keyspace"):
    cluster = Cluster(hosts or ["cassandra_nosql_lab"])
    session = cluster.connect(keyspace)
    return session


def build_insert_query(table: str, columns: list[str]) -> str:
    """
    Builds INSERT query dynamically based on schema
    """
    cols = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))

    return f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"


def load_to_cassandra(
    session,
    table: str,
    records,
    batch_size: int = 100,
):
    """
    Async loader (recommended pattern for Cassandra)
    """

    records = list(records)
    if not records:
        return

    columns = list(records[0].keys())

    query = build_insert_query(table, columns)
    prepared: PreparedStatement = session.prepare(query)

    futures = []

    for record in records:
        values = tuple(record[c] for c in columns)

        future = session.execute_async(prepared, values)
        futures.append(future)

        # simple backpressure
        if len(futures) >= batch_size:
            for f in futures:
                f.result()
            futures.clear()

    # flush remaining
    for f in futures:
        f.result()
