# Standard Library Imports
import datetime


def valid_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

