# Author: Gustav Lundborg
# Date: 25-03-2024
# Revision date: 18-04-2024

import datetime
import holidays


# Dictionary of the financial holidays in the New York Stock Exchange
nyse_holidays = holidays.financial_holidays('NYSE')


def is_business_day(date):  
    """
    Check if the given date is a business day (i.e., not a weekend or holiday)
    takes in a datetime.date as parameter
    """
    return date.weekday() < 5 and date not in nyse_holidays


def last_business_day():  
    """Get the last business day of the current month"""
    today = datetime.date.today()

    while not is_business_day(today):  # Move backward from today's date until finding a business day
        today -= datetime.timedelta(days=1)
    return today


def business_day_one_month_ago():  
    """Get the business day one month ago"""
    today = datetime.date.today()
    # Calculate the date one month ago
    one_month_ago = today - datetime.timedelta(days=30)
    # Move backward from one month ago until finding a business day
    while not is_business_day(one_month_ago):
        one_month_ago -= datetime.timedelta(days=1)
    return one_month_ago
