#!/bin/sh
./run.py tests/randomly_selected_transactions.csv 2021
# RVN-USD from Yahoo data service RVN->USD
# USD-NOK format from Norwegian central bank data service USD->NOK
./run.py tests/randomly_selected_transactions.csv 2021 ../RVN-USD.csv,0,3,2 ../USD-NOK.csv,14,15 1> processed_transactions_2021.csv
