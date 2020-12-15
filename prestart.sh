#! /usr/bin/env bash

echo "CURRENT ENVIRONMENT: $(printenv APP_ENV)"

# Let the DB start
sleep 10

# Run migrations
alembic upgrade head
