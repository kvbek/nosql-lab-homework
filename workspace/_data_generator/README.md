# How to run"

## Cassandra
python main.py \
  --loader cassandra \
  --table events_by_device_day \
  --records 10000 \
  --batch-size 200


## PostgreSQL
python main.py \
  --loader postgres \
  --table events \
  --records 10000 \
  --pg-conn "dbname=test user=postgres password=postgres host=localhost"
