#! /usr/bin/env bash

echo "CURRENT ENVIRONMENT:${app_env}"
echo "CURRENT PYTHONPATH:${pythonpath}"

# Let the DB start
sleep 10

# Run migrations
alembic upgrade head
