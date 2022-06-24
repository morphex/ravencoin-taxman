#!/usr/bin/python3

import csv, sys

from decimal import Decimal
from collections import OrderedDict
from datetime import date as Date
from datetime import timedelta

DATA_FILE = ""
ZERO = Decimal(0)
DEBUG = True

def DEBUG_PRINT(*arguments):
    if DEBUG:
        print(*arguments, file=sys.stderr)


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

def guess_separator(csv_data_lines, default=","):
    """Returns a guess at what the column separator is in the CSV data."""
    semicolon_count_header = csv_data_lines[0].count(";")
    semicolon_count_data = semicolon_count_header
    comma_count_header = csv_data_lines[0].count(",")
    comma_count_data = comma_count_header
    for line in csv_data_lines[1:]:
        semicolon_count_data += line.count(";")
        comma_count_data += line.count(",")
    if comma_count_data > semicolon_count_data:
        return ","
    if comma_count_data < semicolon_count_data:
        return ";"
    else:
        DEBUG_PRINT("Unable to determine column separator")
        DEBUG_PRINT("Choosing ,")
        return ","

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

def parse_float(value):
    """Parses a float, using either a . or , as the denominator."""
    try:
        return float(value)
    except ValueError:
        return float(value.replace(",", "."))

def parse_rate_file(filename, date, low, high, skip_header=True):
    rates = OrderedDict()
    lines = open(filename).readlines()[1:]
    date_index = int(date)
    low_index = int(low)
    high_index = int(high)
    date_format = ""
    dates = []
    separator = guess_separator(lines)
    for line in lines:
        dates.append(line.split(separator)[date_index])
    date_format = guess_date_format(dates)
    year_index, month_index, day_index = date_format
    DEBUG_PRINT("Date format", year_index, month_index, day_index)
    DEBUG_PRINT("First date", parse_date(lines[0].split(separator)[date_index], date_format))
    for line in lines:
        line_ = line.split(separator)
        date = parse_date(line_[date_index], date_format)
        low_ = Decimal(parse_float(line_[low_index]))
        high_ = Decimal(parse_float(line_[high_index]))
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
    DEBUG_PRINT(list(usd_rates.items())[0])

def parse_exchange_file(filename, date, low, high, skip_header=True):
    rates = OrderedDict()
    lines = open(filename).readlines()[1:]
    date_index = int(date)
    low_index = int(low)
    high_index = int(high)
    date_format = ""
    dates = []
    separator = guess_separator(lines)
    for line in lines:
        dates.append(line.split(separator)[date_index])
    date_format = guess_date_format(dates)
    year_index, month_index, day_index = date_format
    DEBUG_PRINT("Exchange rate date format", year_index, month_index, day_index)
    DEBUG_PRINT("Exchange rate first date", parse_date(lines[0].split(separator)[date_index], date_format))
    for line in lines:
        line_ = line.split(separator)
        DEBUG_PRINT("line, date_index:", line_, date_index)
        date = parse_date(line_[date_index], date_format)
        low_ = Decimal(parse_float(line_[low_index]))
        high_ = Decimal(parse_float(line_[high_index]))
        rates[date] = ((low_ + high_) / 2)
    return rates

exchange_rates = {}

if usd_exchange_config:
    try:
        usd_exchange_file, date, low, high = usd_exchange_config.split(",")
    except ValueError:
        try:
            usd_exchange_file, date, rate = usd_exchange_config.split(",")
            low = high = rate
        except ValueError:
            print("USD Exchange rate config: file name,date index,low rate index,high rate index")
            print("Or: file name,date index,exchange rate index")
            sys.exit(1)
    exchange_rates = parse_exchange_file(usd_exchange_file, date, low, high)
    DEBUG_PRINT(list(exchange_rates.items())[0])

def lookup_rate(rate_database, date):
    """Looks up a rate for a given date.  If one doesn't exist for that day,
    return the rate of the first date before the given date."""
    try:
        return Decimal(rate_database[date])
    except KeyError:
        date_ = Date(*date)
        date_ = date_ - timedelta(days=1)
        DEBUG_PRINT("Date", date, "not found, looking at", date_)
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
    additional_headers.append("Exchange rate for LC")
    additional_headers.append("Local currency")
print(",".join(header),"," + ",".join(additional_headers),sep="")
dates = []
for line in data:
    dates.append(line[0])
date_format = guess_date_format(dates)
DEBUG_PRINT("RVN Data date format:", date_format)
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
                exchange_rate =  lookup_rate(usd_rates, date)
                total = Decimal(line[-1]) * exchange_rate
                DEBUG_PRINT((total, str(total)))
                additional_data.extend([str(exchange_rate), str(total)])
            except KeyError:
                additional_data.extend(["", ""])
            if exchange_rates:
                try:
                    exchange_rate = lookup_rate(exchange_rates, date)
                    total2 = total * exchange_rate
                    DEBUG_PRINT((exchange_rate, total2, str(total2)))
                    additional_data.extend([str(exchange_rate), str(total2)])
                except KeyError:
                    additional_data.extend([""])
    if printable:
        print(','.join(line),",",",".join(additional_data),sep="")
