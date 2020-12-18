#! /usr/bin/env bash

printf "CURRENT ENVIRONMENT: %s \n
CALCULATING PYTHONPATH...", "${app_env}"

calculated_path=$(find ./app -name 'database_schema.py' -exec readlink -f {} \;)

printf "CALCULATED PATH: %s", "${calculated_path} \n
EXPORTING TO PYTHONPATH..."

export PYTHONPATH="${PYTHONPATH}:${calculated_path}"

printf "CURRENT PYTHONPATH:\n%s", "${PYTHONPATH}"

printf  "WAITING 10 SECONDS..."

sleep 10

printf  "MIGRATING..."

alembic upgrade head

printf "ALL FINISHED SUCCESSFULLY!"
