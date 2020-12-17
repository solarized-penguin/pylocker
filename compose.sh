#!/usr/bin/env zsh
# shellcheck shell=bash

compose() {
  docker-compose --env-file ../../Documents/env_vars/"$1"/"${env}".env \
    -f ./docker-composes/"$1"-compose.yml up -d --build
}

export env=dev
CHOICE=$1

case $CHOICE in
"AUTH")
  echo "CHOICE: ${CHOICE}"
  compose auth
  ;;

"PYLOCKER")
  echo "CHOICE: ${CHOICE}"
  compose pylocker
  ;;

"ALL")
  echo "CHOICE: ${CHOICE}"

  compose auth
  compose pylocker
  ;;

*)
  printf "Wrong input parameters!\n
    Legal input: AUTH, PYLOCKER or ALL"

  exit 1
  ;;
esac

echo "Script has concluded"
