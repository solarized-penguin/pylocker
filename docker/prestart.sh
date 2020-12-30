#! /usr/bin/env bash

printf "CURRENT ENVIRONMENT: %s
CALCULATING PYTHONPATH...", "${app_env}"

calculated_path=$(find ./app -name 'database_schema.py' -exec readlink -f {} \;)

printf "CALCULATED PYTHONPATH: %s", "${calculated_path}"

printf "WAITING 10 SECONDS..."

sleep 10

printf "MIGRATING..."

alembic upgrade head

printf "ALL FINISHED SUCCESSFULLY!"
