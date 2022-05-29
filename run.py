#!/usr/bin/python3

import csv, sys

from decimal import Decimal

DATA_FILE = ""
ZERO = Decimal(0)

DATA_FILE = sys.argv[1]

year = None
usd_rate_config = ""
usd_exchange_config = ""

try:
    year = sys.argv[2]
except IndexError:
    pass

try:
    usd_rate_config = sys.argv[3]
except IndexError:
    pass

try:
    usd_exchange_config = sys.argv[4]
except IndexError:
    pass

def parse_rate_file(filename, date, low, high, skip_header=True):
    lines = open(filename).readlines()[1:]
    date_index = int(date)
    low_index = int(date)
    high_index = int(date)
    date_format = ""
    year_index = month_index = day_index = None
    for line in lines:
        date = line.split(",")[date_index]
        date = date.split(" ")[0]
        date = list(map(int, date.split("-")))
        if not year_index:
            if int(date[0]) > 1000:
                year_index = 0
            else:
                year_index = 2
        if year_index == 0:
            if date[1] > 12:
                day_index = 1
                month_index = 2
                break
            elif date[2] > 12:
                day_index = 2
                month_index = 1
                break
        elif year_index == 2:
            if date[1] > 12:
                day_index = 1
                month_index = 0
                break
            elif date[0] > 12:
                day_index = 0
                month_index = 1
                break
    else:
        raise ValueError("Unable to determine date format")
    print("Date format", year_index, month_index, day_index, file=sys.stderr)
    return {}

usd_rates = {}

if usd_rate_config:
    try:
        usd_rate_file, date, low, high = usd_rate_config.split(",")
    except ValueError:
        print("Rate config: file name,date index,low rate index,high rate index")
        sys.exit(1)
    usd_rates = parse_rate_file(usd_rate_file, date, low, high)

balance = Decimal(0.0)

data = csv.reader(open(DATA_FILE, "r"))
data = list(data)
data, header = data[1:], data[0]
data.reverse()
additional_headers = ["Balance"]
if usd_rate_config:
    additional_headers.append("USD rate")
if usd_exchange_config:
    additiona._headers.append("Local currency")
print(",".join(header),"," + ",".join(additional_headers),sep="")
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
