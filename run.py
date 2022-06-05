#!/usr/bin/python3

import csv, sys

from decimal import Decimal
from collections import OrderedDict
from datetime import date as Date
from datetime import timedelta

DATA_FILE = ""
ZERO = Decimal(0)
DEBUG = True

DATA_FILE = sys.argv[1]

year = None
usd_rate_config = ""
usd_exchange_config = ""

try:
    year = int(sys.argv[2])
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

def guess_date_format(dates):
    """Guess the date format given a set of dates."""
    year_index = month_index = day_index = None
    for date in dates:
        if date.startswith('"') and date.endswith('"'):
            date = date[1:-1]
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
    return year_index, month_index, day_index

def parse_date(date, format):
    """Returns year, month, day of a parsed date. Format is year_index, month_index, day_index."""
    if date.startswith('"') and date.endswith('"'):
        date = date[1:-1]
    date = date.split(" ")[0]
    date_ = date.split("-")
    year, month, day = date_[format[0]], date_[format[1]], date_[format[2]]
    return int(year), int(month), int(day)

def parse_rate_file(filename, date, low, high, skip_header=True):
    rates = OrderedDict()
    lines = open(filename).readlines()[1:]
    date_index = int(date)
    low_index = int(low)
    high_index = int(high)
    date_format = ""
    dates = []
    for line in lines:
        dates.append(line.split(",")[date_index])
    date_format = guess_date_format(dates)
    year_index, month_index, day_index = date_format
    if DEBUG:
        print("Date format", year_index, month_index, day_index, file=sys.stderr)
        print("First date", parse_date(lines[0].split(",")[date_index], date_format), file=sys.stderr)
    for line in lines:
        line_ = line.split(",")
        date = parse_date(line_[date_index], date_format)
        low_ = Decimal(line_[low_index])
        high_ = Decimal(line_[high_index])
        rates[date] = ((low_ + high_) / 2)
    return rates

usd_rates = {}

if usd_rate_config:
    try:
        usd_rate_file, date, low, high = usd_rate_config.split(",")
    except ValueError:
        print("Rate config: file name,date index,low rate index,high rate index")
        sys.exit(1)
    usd_rates = parse_rate_file(usd_rate_file, date, low, high)
    if DEBUG:
        print(list(usd_rates.items())[0], file=sys.stderr)

def lookup_rate(rate_database, date):
    """Looks up a rate for a given date.  If one doesn't exist for that day,
    return the rate of the first date before the given date."""
    try:
        return rate_database[date]
    except KeyError:
        date_ = Date(*date)
        date_ = date_ - timedelta(days=1)
        if DEBUG:
            print("Date", date, "not found, looking at", date_, file=sys.stderr)
        return lookup_rate(rate_database, (date_.year, date_.month, date_.day))

balance = Decimal(0.0)

data = csv.reader(open(DATA_FILE, "r"))
data = list(data)
data, header = data[1:], data[0]
data.reverse()
additional_headers = ["Balance"]
if usd_rate_config:
    additional_headers.extend(["USD rate", "USD converted"])
if usd_exchange_config:
    additiona._headers.append("Local currency")
print(",".join(header),"," + ",".join(additional_headers),sep="")
dates = []
for line in data:
    dates.append(line[0])
date_format = guess_date_format(dates)
print("RVN Data date format:", date_format, file=sys.stderr)
for line in data:
    date = parse_date(line[0], date_format)
    balance += Decimal(line[-1])
    additional_data = [str(balance)]
    printable = None
    if year:
        if year == date[0]:
            printable = line
    else:
        printable = line
    if printable:
        if usd_rates:
            try:
                total = Decimal(line[-1]) * lookup_rate(usd_rates, date)
                if DEBUG:
                    print((total, str(total)), file=sys.stderr)
                additional_data.extend([str(lookup_rate(usd_rates, date)), str(total)])
            except KeyError:
                additional_data.extend(["", ""])
    if printable:
        print(','.join(line),",",",".join(additional_data),sep="")
