#!/bin/sh
optuna studies --storage "mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DB}" | grep spatial_demo_calibration_on_aks2 > /dev/null
echo $?
