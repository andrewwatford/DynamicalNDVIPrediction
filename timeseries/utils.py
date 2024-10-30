# imports
from __future__ import annotations
from timeseries.TimeSeries import TimeSeries
from typing import List
from dateutil.relativedelta import relativedelta
import datetime

DAYS_IN_YEAR = 365.256 # sidereal year
DAYS_IN_MONTH = DAYS_IN_YEAR / 12

def daterange(start: datetime.datetime, stop: datetime.datetime, step: relativedelta) -> List[datetime.datetime]:
    '''
    Creates a list of datetimes in [start, stop) separated by step.

    Arguments:
        start: datetime.datetime. The initial datetime.
        stop: datetime.datetime. The final datetime.
        step: relativedelta. The time step between points.
    '''
    lst = []
    cur = start
    while cur < stop:
        lst.append(cur)
        cur = cur + step
    return lst

def flag(ts: TimeSeries, threshold: float, min_length: relativedelta, upper_threshold: bool = False) -> List[bool]:
    '''
    Returns a list of bools, the same length as ts.dates, with entry True if
        the value of ts.x exceeds (or is lower than, if upper_threshold = True)
        threshold for a period of at least min_length. 

    Arguments:
        ts: The TimeSeries to produce the flags for.
        threshold: A threshold to use.
        min_length: The minimum length for the threshold
        upper_threshold: whether the threshold is an upper or lower threshold.

    Returns:
        flags: The list of flags.
        periods: A list of tuples representing the start and end of the flagged periods.
    '''
    flags = [False] * len(ts.data_lst)

    start_date = None
    start_date_idx = None

    for i, (date, value) in enumerate(ts.data_lst):
        if ((value <= threshold) and (upper_threshold)) or ((not upper_threshold) and (value >= threshold)):
            if start_date is None:
                start_date = date
                start_date_idx = i
        else:
            start_date = None
            start_date_idx = None

        if (start_date is not None) and (start_date + min_length <= ts.dates[i+1]):
            for cur_idx in range(start_date_idx, i + 1):
                flags[cur_idx] = True

    periods = []
    start_date = None
    end_date = None

    for i in range(len(flags)):
        if flags[i]:
            end_date =  ts.dates[i]
            if start_date is None:
                start_date = ts.dates[i]
        elif start_date is not None:
            periods.append((start_date, end_date))
            start_date = None
            end_date = None

    return flags, periods