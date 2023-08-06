from __future__ import division
import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import seaborn
import pandas as pd
import os
import os.path
import hedgeye_analysis.hedgeye_pandas_patch
from hedgeye_analysis.introspection import print_source

from IPython.display import display
from IPython.display import HTML

def file_exists(filename):
    return os.path.isfile(filename)

def root_dir():
    curdir = os.getcwd()
    import re
    curdir = re.sub('/copied.*', '', curdir)
    return re.sub('/shared.*', '', curdir)

def shared_dir():
    return root_dir() + '/shared'

def copied_dir():
    return root_dir() + '/copied'

def today_string(today = None):
    """Returns a string representing today

    >>> today_string('2014-03-11')
    '2014-03-11'
    >>> today_string('2014-09-30')
    '2014-09-30'
    >>> today_string('2014-12-31')
    '2014-12-31'
    """
    if today is None:
        today = datetime.date.today()
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return today.strftime("%Y-%m-%d")

def year_dash_month_string(today = None):
    """Returns a string representing current month

    >>> year_dash_month_string('2014-03-11')
    '2014-03'
    >>> year_dash_month_string('2014-09-30')
    '2014-09'
    >>> year_dash_month_string('2014-12-31')
    '2014-12'
    """
    if today is None:
        today = datetime.date.today()
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return today.strftime("%Y-%m")

def prev_month_year_dash_month_string(today = None):
    """Returns a string representing current month

    >>> prev_month_year_dash_month_string('2014-03-11')
    '2014-02'
    >>> prev_month_year_dash_month_string('2014-09-30')
    '2014-08'
    >>> prev_month_year_dash_month_string('2014-12-31')
    '2014-11'
    >>> prev_month_year_dash_month_string('2015-01-27')
    '2014-12'
    """
    if today is None:
        today = datetime.date.today()
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return (today + relativedelta(months = -1)).strftime("%Y-%m")

def next_month_year_dash_month_string(today = None):
    """Returns a string representing the next month

    >>> next_month_year_dash_month_string('2014-03-11')
    '2014-04'
    >>> next_month_year_dash_month_string('2014-09-30')
    '2014-10'
    >>> next_month_year_dash_month_string('2014-12-31')
    '2015-01'
    >>> next_month_year_dash_month_string('2015-01-27')
    '2015-02'
    """
    if today is None:
        today = datetime.date.today()
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return (today + relativedelta(months = +1)).strftime("%Y-%m")

def tomorrow_string(today = None):
    """Returns a string representing tomorrow or the day after the day passed in

    >>> tomorrow_string('2014-03-11')
    '2014-03-12'
    >>> tomorrow_string('2014-09-30')
    '2014-10-01'
    >>> tomorrow_string('2014-12-31')
    '2015-01-01'
    """
    if today is None:
        today = datetime.date.today()
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return (today + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")

def tomorrow(today = None):
    """ Returns date object representing tomorrow or the day after the day passed in

    >>> tomorrow('2015-06-15')
    datetime.date(2015, 6, 16)
    """
    if today is None:
        today = datetime.date.today()
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return (today + datetime.timedelta(days = 1))

def next_date(date):
    """ deprecated """
    return tomorrow_string(date)
    #return (datetime.datetime.strptime(date,"%Y-%m-%d") + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")

def today():
    return datetime.date.today()

def yesterday(today = today()):
    """Returns date object representing yesterday or the day before the day passed in

    >>> yesterday(datetime.date(2014, 3, 11))
    datetime.date(2014, 3, 10)
    >>> yesterday(datetime.date(2014, 10, 1))
    datetime.date(2014, 9, 30)
    >>> yesterday(datetime.date(2015, 1, 1))
    datetime.date(2014, 12, 31)
    """
    return (today - datetime.timedelta(days = 1))

def yesterday_string(today = today()):
    """Returns a string representing yesterday or the day before the day passed in

    >>> yesterday_string('2014-03-11')
    '2014-03-10'
    >>> yesterday_string('2014-10-01')
    '2014-09-30'
    >>> yesterday_string('2015-01-01')
    '2014-12-31'
    """
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return yesterday(today).strftime("%Y-%m-%d")

def week_ago_string(today = datetime.date.today()):
    """deprecated"""
    #if isinstance(today, str):
    #  today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    #return (today - datetime.timedelta(days = 7)).strftime("%Y-%m-%d")
    return n_weeks_ago_date_string(1, today=today)

def month_ago_string(today = datetime.date.today()):
    """deprecated"""
    #if isinstance(today, str):
    #  today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    #return (today - datetime.timedelta(months = 1)).strftime("%Y-%m-%d")
    return n_months_ago_date_string(1, today=today)

def n_months_ago_date(n, today=datetime.date.today()):
    return (today - relativedelta(months=n))

def n_months_ago_date_string(n, today=datetime.date.today()):
    """Returns a string representing n (1, 2, 3, etc.) months ago

    >>> n_months_ago_date_string(12, '2016-02-29')
    '2015-02-28'

    >>> n_months_ago_date_string(12, '2015-08-31')
    '2014-08-31'

    >>> n_months_ago_date_string(2, '2015-08-31')
    '2015-06-30'

    >>> n_months_ago_date_string(3, '2014-03-11')
    '2013-12-11'

    >>> n_months_ago_date_string(5, '2014-03-11')
    '2013-10-11'
    """
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return n_months_ago_date(n, today=today).strftime('%Y-%m-%d')

def n_weeks_ago_date(n, today=datetime.date.today()):
    return (today - relativedelta(weeks=n))

def n_weeks_ago_date_string(n, today=datetime.date.today()):
    """Returns a string representing n (1, 2, 3, etc.) weeks ago

    >>> n_weeks_ago_date_string(1, '2016-02-29')
    '2016-02-22'

    >>> n_weeks_ago_date_string(2, '2015-08-31')
    '2015-08-17'

    >>> n_weeks_ago_date_string(3, '2015-08-31')
    '2015-08-10'

    >>> n_weeks_ago_date_string(4, '2014-03-11')
    '2014-02-11'

    >>> n_weeks_ago_date_string(5, '2014-03-11')
    '2014-02-04'
    """
    if isinstance(today, str):
        today = datetime.datetime.strptime(today,"%Y-%m-%d").date()
    return n_weeks_ago_date(n, today=today).strftime('%Y-%m-%d')

def remove_weekends(data):
    """ Return Series/DataFrame with weekend dates removed """
    # http://pandas.pydata.org/pandas-docs/stable/missing_data.html
    return data[data.index.weekday < 5]

def remove_empty_rows(data):
    """ Return Series/DataFrame with only rows containing valid data """
    # http://pandas.pydata.org/pandas-docs/stable/missing_data.html
    return data.dropna(axis=0)

def df_stale_days(dataframe):
    """ Return integer number of calendar days since last observation
        according to dataframe index """
    staleness = datetime.datetime.now() - dataframe.index.to_pydatetime()[-1]
    return staleness.days

def plot_many_against_one(one, many, dataframe, title=None):
    """
    Displays array of plots, each with y-axis dataframe[one] and x-axis dataframe[name]
    where "name" is a value in the list "many."
    
    If there are four or fewer values in "many," it will print four plots in a single row.
    If there are more than 16 values in "many," it will print in rows of four.
    If there are 5-15 values in "many," it will choose a nice number of rows/columns.     
    """

    fig = plt.figure()

    import math

    num_plots = len(many)

    
    if num_plots <= 4:
        per_row = num_plots
    elif math.ceil(math.sqrt(num_plots)) >= 4:
        per_row = 4
    else:
        per_row = math.ceil(math.sqrt(num_plots))
    rows = math.ceil(num_plots / per_row)

    #axes1 = fig.add_axes([0.1/num_plots * 1 + 0.3 * 0, 0.1, 0.9/num_plots, 0.9]) # main axes
    #axes2 = fig.add_axes([0.1/num_plots * 2 + 0.3 * 1, 0.1, 0.9/num_plots, 0.9]) # inset axes
    #axes3 = fig.add_axes([0.1/num_plots * 3 + 0.3 * 2, 0.1, 0.9/num_plots, 0.9]) # inset axes

    x_width = 0.9
    y_height = 1 - 0.1 * rows

    x_padding = 1 - x_width
    plot_width = x_width / per_row
    y_padding = 1 - y_height
    y_row_padding = y_padding / rows
    plot_height = (y_height - y_padding) / rows

    if title: fig.suptitle(title)
    for row in range(1, rows + 1):
        for col in range(1, per_row + 1):
            i = (row - 1) * per_row + col
            x_offset = x_padding/per_row * (col - 1) + plot_width * (col - 1)
            y_offset = y_padding/rows * (rows - row) + plot_height * (rows - row)
            globals()['axes' + str(i)] = fig.add_axes([x_offset, y_offset, plot_width, plot_height])
            globals()['axes' + str(i)].scatter(dataframe[many[i - 1]], dataframe[one], c='g', alpha=0.1)
            globals()['axes' + str(i)].set_xlabel(many[i - 1])
            globals()['axes' + str(i)].set_title(many[i - 1] + ' vs. ' + one)
            if col == 1: globals()['axes' + str(i)].set_ylabel(one)
            if i == num_plots: break

if __name__ == '__main__':
    import doctest
    doctest.testmod()
