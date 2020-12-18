#! /usr/bin/env bash

echo "CURRENT ENVIRONMENT:${APP_ENV}"
echo "CURRENT PYTHONPATH:${PYTHONPATH}"

# Let the DB start
sleep 10

# Run migrations
alembic upgrade head
