#! /usr/bin/env bash

echo "CURRENT ENVIRONMENT:${app_env}"

PYTHONPATH="${PYTHONPATH}:$(find ./app -name 'database_schema.py' -exec readlink -f {} \;)"
export PYTHONPATH

printf "CURRENT PYTHONPATH:\n%s", "${PYTHONPATH}"
ZZZZZZZZ

echo "Waiting 10 seconds to let database start..."
# Let the DB start
sleep 10

echo "Running migrations..."
# Run migrations
alembic upgrade head

echo "Migrations concluded. All done!"
