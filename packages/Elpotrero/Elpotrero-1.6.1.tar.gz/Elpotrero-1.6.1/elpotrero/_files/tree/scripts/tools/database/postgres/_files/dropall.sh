#!/bin/bash

export PGPASSWORD="{{db_pg_password}}"
psql -d template1 -U {{db_pg_user}} -h {{db_host}} -f dropall.sql 
echo "done"
