# imports
from __future__ import annotations
from scipy.interpolate import CubicSpline, interp1d
from scipy.integrate import quad
import scipy.signal as signal
from typing import Union, Iterable, List
from dateutil.relativedelta import relativedelta
import numpy as np
import datetime
import csv
import os

class TimeSeries():
    '''
    Class to create time series of quantities from Google Earth Engine.
    '''

    def __init__(self, data_dir: str, t_format_str: str, spline_interpolate: bool = True, warn: bool = True):
        '''
        Constructor.

        Arguments:
            data_dir: string pointing to the (relative) folder where .csv files of data are stored.
            t_format_str: string for formatting dates into datetime objects.
            spline_interpolate: a bool, deciding whether to use a cubic spline interpolation or not.
            warn: a bool whether or not to print warning messages.
        '''
        self.data_dir = data_dir
        self.t_format_str = t_format_str
        self.spline_interpolate = spline_interpolate
        self.warn = warn
        data_lst = []
        # import the data
        if data_dir:
            for file in os.listdir(self.data_dir):
                filepath = os.path.join(self.data_dir, file)
                if file.endswith(".csv"):
                    with open(filepath, newline='') as f:
                        reader = csv.reader(f)
                        for row_num, row in enumerate(reader):
                            if (row_num > 0) and (row[0] != '') and (row[1] != ''):
                                date = datetime.datetime.strptime(row[0], self.t_format_str)
                                value = float(row[1])
                                data_lst.append((date, value))
            # sort the data
            data_lst.sort(key = lambda d: d[0])
            self.dates, self.x = zip(*data_lst)
            self.set_up_interpolant()

    def __call__(self, datetime: Union[datetime.datetime, Iterable[datetime.datetime]]) -> Union[float, List[float]]:
        '''
        Calls the interpolant of the time series on a datetime (or array of datetimes).

        Arguments:
            datetime: the points at which to evaluate the interpolant.

        Returns:
            val: the values of the interpolant.
        '''
        if hasattr(datetime, "__iter__"):
            return [self.interpolant(d.timestamp()) for d in datetime]
        else:
            return self.interpolant(datetime.timestamp())
        
    def set_up_interpolant(self):
        '''
        Sets up the interpolant function.
        '''
        self.t = [d.timestamp() for d in self.dates]
        if self.spline_interpolate:
            self.interpolant = CubicSpline(self.t, self.x, extrapolate=False)
        else:
            self.interpolant = interp1d(self.t, self.x, bounds_error = True)

    def get_average(self, start: datetime.datetime, stop: datetime.datetime) -> float:
        '''
        Returns the average value of the timeseries across two dates.

        Arguments:
            start: datetime.datetime. Specifies the start of the interval over which to average.
            stop: datetime.datetime. Specifies the end of the interval over which to average.

        Returns:
            avg: float
        '''
        if (stop < self.dates[0]) or (start > self.dates[-1]):
            if self.warn:
                print('The range is entirely outside of the available dates. Returning zero.')
            return 0
        if (start < self.dates[0]):
            if self.warn:
                print('Extrapolation is not possible, adjusting start of range.')
            start = self.dates[0]
        elif (stop > self.dates[-1]):
            if self.warn:
                print('Extrapolation is not possible, adjusting end of range.')
            stop = self.dates[-1]
        a = start.timestamp()
        b = stop.timestamp()
        if not self.spline_interpolate:
            points = list(filter(lambda t: (a <= t) and (t <= b), self.t))
            int_val, abserr = quad(self.interpolant, a, b, points = points, limit = max(len(points), 50))
            out = int_val / (b - a)
            return out
        else:
            out = self.interpolant.integrate(a, b) / (b - a)
            return out

    def export(self, data_dir: str, t_format_str: str) -> None:
        '''Exports the timeseries to a csv file in the same manner as it was imported'''
        with open(data_dir, 'w', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(['date','x'])
            for date, x in zip(self.dates, self.x):
                date_str = date.strftime(t_format_str)
                wr.writerow([date_str, x])

    def resample(self, start: datetime.datetime, stop: datetime.datetime, step: Union[relativedelta, datetime.timedelta]) -> TimeSeries:
        '''
        Returns a resampled TimeSeries of self.
        '''
        new_ts = TimeSeries(None, None, self.spline_interpolate, self.warn)
        if start < self.dates[0]:
            if self.warn:
                print('Extrapolation is not possible, adjusting start of range.')
            start = self.dates[0]
        if stop > self.dates[-1]:
            if self.warn:
                print('Extrapolation is not possible, adjusting end of range.')
            stop = self.dates[-1]
        new_ts.dates = []
        new_ts.x = []
        cur_date = start
        while cur_date < stop:
            cur_x = self(cur_date)
            new_ts.dates.append(cur_date)
            new_ts.x.append(cur_x)
            cur_date = cur_date + step
        new_ts.set_up_interpolant()
        return new_ts
    
    def smooth(self, window: np.ndarray) -> TimeSeries:
        '''
        Returns a smoothed TimeSeries of self.
        '''
        new_ts = TimeSeries(None, None, self.spline_interpolate, self.warn)
        new_ts.dates = self.dates
        new_ts.x = signal.convolve(self.x, window, 'same') / sum(window)
        new_ts.set_up_interpolant()
        return new_ts
