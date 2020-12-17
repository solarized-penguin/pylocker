#!/usr/bin/env bash

cat ../../Documents/env_vars/pylocker/dev.env ../../Documents/env_vars/fusionauth/dev.env \
  >../../Documents/env_vars/joined.env

python ../../Documents/env_vars/env_to_dotenv.py ../../Documents/env_vars/joined.env \
  ../../Documents/env_vars/joined.env

B=FP

echo "option ${B} chosen"

if [[ $B == P ]]; then
  docker-compose --env-file ../../Documents/env_vars/joined.env \
    -f docker-compose.yml up -d --build pylocker_db pylocker
elif [[ $B == F ]]; then
  docker-compose --env-file ../../Documents/env_vars/joined.env \
    -f docker-compose.yml up -d --build fusion_db fusionauth
elif [[ $B == E ]]; then
  docker-compose --env-file ../../Documents/env_vars/joined.env \
    -f docker-compose.yml up -d --build elastic_search
elif [[ $B == A ]]; then
  docker-compose --env-file ../../Documents/env_vars/joined.env \
    -f docker-compose.yml up -d --build
elif [[ $B == FS ]]; then
  docker-compose --env-file ../../Documents/env_vars/joined.env \
    -f docker-compose.yml up -d --build fusion_search fusion_db fusionauth
elif [[ $B == FP ]]; then
  docker-compose --env-file ../../Documents/env_vars/joined.env \
    -f docker-compose.yml up -d --build fusion_db fusionauth pylocker_db pylocker
fi

echo "running compose concluded..."
