#!/usr/bin/env bash

docker-compose --env-file ../env_vars/joined.env \
-f docker-compose.yml up -d --build pylocker_db pylocker
