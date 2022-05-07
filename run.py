#!/usr/bin/python3

import csv, sys

from decimal import Decimal

DATA_FILE = ""
ZERO = Decimal(0)

DATA_FILE = sys.argv[1]

try:
    year = sys.argv[2]
except IndexError:
    year = None

balance = Decimal(0.0)

data = csv.reader(open(DATA_FILE, "r"))
data = list(data)
data, header = data[1:], data[0]
data.reverse()
print(",".join(header),",Balance",sep="")
for line in data:
    balance += Decimal(line[-1])
    printable = None
    if year:
        if line[0].startswith(str(year)):
            printable = line
    else:
        printable = line
    if printable:
        print(','.join(line),",",balance,sep="")
