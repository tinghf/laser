#!/bin/sh
optuna studies --storage "mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DB}" | grep laser_on_aks > /dev/null
echo $?
