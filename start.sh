#!/bin/bash

# Massage dates into ISO format

sed -i '' 's/\([0-9]\{1,2\}\)\/\([0-9]\{1,2\}\)\/\([0-9]\{2\}\)/20\3-\2-\1/g' uc_results_gf.csv
sed -i '' 's/-\([0-9]\)-/-0\1-/g' uc_results_gf.csv
sed -i '' 's/-\([0-9]\),/-0\1,/g' uc_results_gf.csv

# Start SQLite3
sqlite3 transactions.db <<EOF

# Import the data from uc_results_gf.csv
drop table if exists transactions;
.mode csv
.import uc_results_gf.csv transactions

EOF

redis-cli ping
if [ $? -eq 1 ]; then
    redis-server &
fi

python3 server.py &
