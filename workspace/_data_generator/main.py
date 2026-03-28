import argparse
import random
from datetime import datetime, timedelta

from schema import Schema, Field
from generator import generate_records

# loaders
from loaders.cassandra_loader import cassandra_connect, load_to_cassandra
from loaders.postgres_loader import pg_connect, load_to_postgres


# ---------- generators ----------

def gen_device():
    return f"device_{random.randint(1, 10)}"


def gen_timestamp():
    return datetime.now() - timedelta(minutes=random.randint(0, 1440))


def gen_day():
    return datetime.now().strftime("%Y-%m-%d")


def gen_temperature():
    return round(random.uniform(20, 35), 2)

def gen_humidity():
    return round(random.uniform(30, 70), 2)


# ---------- schema ----------

iot_schema = Schema(
    name="iot_events",
    fields=[
        Field("device_id", gen_device),
        Field("day", gen_day),
        Field("event_time", gen_timestamp),
        Field("temperature", gen_temperature),
        Field("humidity", gen_humidity),
    ],
)


# ---------- loader dispatcher ----------

def run_loader(loader_type: str, records, args):
    """
    Dispatch execution based on selected loader
    """

    if loader_type == "cassandra":
        session = cassandra_connect(hosts=[args.host])
        load_to_cassandra(
            session=session,
            table=args.table,
            records=records,
            batch_size=args.batch_size
        )

    elif loader_type == "postgres":
        conn = pg_connect(args.pg_conn)
        load_to_postgres(
            conn=conn,
            table=args.table,
            records=records,
            batch_size=args.batch_size
        )

    else:
        raise ValueError(f"Unsupported loader: {loader_type}")


# ---------- CLI ----------

def parse_args():
    parser = argparse.ArgumentParser(description="Universal Data Generator")

    parser.add_argument("--loader", required=True, choices=["cassandra", "postgres"])
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--table", required=True)

    # cassandra
    parser.add_argument("--host", default="127.0.0.1")

    # postgres
    parser.add_argument("--pg-conn", default="dbname=test user=postgres password=postgres host=localhost")

    parser.add_argument("--batch-size", type=int, default=100)

    return parser.parse_args()


# ---------- main ----------

def main():
    args = parse_args()

    # generate data
    records = generate_records(iot_schema, n=args.records)

    # run selected loader
    run_loader(args.loader, records, args)

    print(f"Done. Loader={args.loader}, Records={args.records}")


if __name__ == "__main__":
    main()
