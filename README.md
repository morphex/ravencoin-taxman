ravencoin-taxman is a tool to generate CSV files suitable for
accounting purposes.

Unlike ethereum-classic-taxman, this tool creates the CSV file based
on an existing service to get CSV transaction data from the
blockchain, and that service is

  https://rvn.cryptoscope.io/

It can be run using for example

  ./run.py INDATA.csv 2022 

Just to get the balance and transactions for 2022.

To get the USD rate of each transaction as well, use the script like
this:

  ./run.py INDATA.csv 2022 RVN-USD.csv,0,3,2

where the CSV file format is the same as what you can download from
Yahoo, IIRC.

As it is, it appears to be working correctly.
