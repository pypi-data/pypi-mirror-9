#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import datetime, timedelta
from dateutil.parser import parse

ONE_DAY = timedelta(days=1)
ONE_HOUR = timedelta(hours=1)
MONTH_FMT = '{}-{:02}-01 06:00:00'
DAY_FMT = '%Y-%m-%d 06:00:00'
HOUR_FMT = '%Y-%m-%d %H:00:00'

# folder name format for day
FOLDER_DAY_FMT = '%Y%m%d'

# folder name format for hour
FOLDER_HOUR_FMT = '%Y%m%d%H'
QUARTERS = ['Q1 (Nov ~ Jan)', 'Q2 (Feb ~ Apr)', 'Q3 (May ~ Jul)',
            'Q4 (Aug ~ Oct)']
MONTHS = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
          'Sep', 'Oct']
MONTH_DAYS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
              'Oct', 'Nov', 'Dec']
QUARTER_MONTHS = [['Nov', 'Dec', 'Jan'],
                  ['Feb', 'Mar', 'Apr'],
                  ['May', 'Jun', 'Jul'],
                  ['Aug', 'Sep', 'Oct'],
                  ]


class JshDate(object):
    def __init__(self, **kwargs):
        self.month_fmt = kwargs.get('month_fmt', MONTH_FMT)
        self.day_fmt = kwargs.get('day_fmt', DAY_FMT)
        self.hour_fmt = kwargs.get('hour_fmt', HOUR_FMT)
        self.folder_day_fmt = kwargs.get('folder_day_fmt', FOLDER_DAY_FMT)
        self.folder_hour_fmt = kwargs.get('folder_hour_fmt', FOLDER_HOUR_FMT)

    def get_quarter_by_month(self, month):
        if month in (11, 12, 1):
            return 1

        if month in (2, 3, 4):
            return 2

        if month in (5, 6, 7):
            return 3

        return 4

    def get_current_quarter(self):
        return self.get_quarter_by_month(datetime.now().month)

    def get_year_chart_ticks(self, seqs=[], kind='quarter', **kwargs):
        if kind == 'quarter':
            return [QUARTERS[i] for i, _ in enumerate(seqs)]

        year = kwargs['year']
        ticks = []
        for i, _ in enumerate(seqs):
            if i == 2:
                ticks.append('{}-Jan'.format(year))
            else:
                ticks.append(MONTHS[i])

        return ticks

    def get_year_ticks(self, year, month=0, quarter=0):
        # Month view and Quarter View
        # Nov, Dec, Jan, ..., Oct
        # Q1: Nov ~ Jan, Q2: Feb ~ Apr
        # Q3: May ~ Jul, Q4: Aug ~ Oct
        now = datetime.now()
        now_str = now.strftime('%Y%m')
        y_str = '{}'.format(year)
        month_ticks = []
        qt_ticks = []
        if month:
            if '{}{:02}'.format(year, month) > now_str:
                return [], []

            if month == 11:
                ts1 = self.month_fmt.format(year - 1, 11)
                ts2 = self.month_fmt.format(year - 1, 12)
            elif month == 12:
                ts1 = self.month_fmt.format(year - 1, 12)
                ts2 = self.month_fmt.format(year, 1)
            elif 1 <= month <= 10:
                ts1 = self.month_fmt.format(year, month)
                ts2 = self.month_fmt.format(year, month + 1)
            else:
                return [], []

            month_ticks.append((ts1, ts2, month))

        if quarter:
            if quarter == 1 and year <= now.year:
                ts1 = self.month_fmt.format(year - 1, 11)
                ts2 = self.month_fmt.format(year, 2)
            elif quarter == 2 and now_str >= (y_str + '02'):
                ts1 = self.month_fmt.format(year, 2)
                ts2 = self.month_fmt.format(year, 5)
            elif quarter == 3 and now_str >= (y_str + '05'):
                ts1 = self.month_fmt.format(year, 5)
                ts2 = self.month_fmt.format(year, 8)
            elif quarter == 4 and now_str >= (y_str + '08'):
                ts1 = self.month_fmt.format(year, 8)
                ts2 = self.month_fmt.format(year, 10)
            else:
                return [], []

            qt_ticks.append((ts1, ts2, quarter))

        if not (month or quarter):
            now_str = now.strftime('%Y-%m-%d 06:00:00')
            last_year = year - 1
            month_ticks = [(self.month_fmt.format(last_year, 11),
                           self.month_fmt.format(last_year, 12),
                           11),
                           (self.month_fmt.format(last_year, 12),
                           self.month_fmt.format(year, 1),
                           12),
                           ]

            for i in range(1, 11):
                if now_str < self.month_fmt.format(year, i):
                    break

                month_ticks.append((self.month_fmt.format(year, i),
                                   self.month_fmt.format(year, i + 1),
                                   i))

            qt_ticks = [(self.month_fmt.format(last_year, 11),
                         self.month_fmt.format(year, 2),
                         1)]
            for i, q in enumerate((2, 5, 8)):
                if now_str < self.month_fmt.format(year, q):
                    break

                qt_ticks.append((self.month_fmt.format(year, q),
                                 self.month_fmt.format(year, q + 3),
                                 i + 2))

        return month_ticks, qt_ticks

    def get_quarter_chart_ticks(self, quarter):
        return QUARTER_MONTHS[int(quarter) - 1]

    def get_quarter_ticks(self, year, quarter):
        # Q1: Nov ~ Jan, Q2: Feb ~ Apr
        # Q3: May ~ Jul, Q4: Aug ~ Oct
        ticks = []
        now = datetime.now()
        now_str = now.strftime('%Y%m')
        year_str = '{}'.format(year)
        if quarter == 1 and year <= now.year:
            ticks.append((self.month_fmt.format(year - 1, 11),
                          self.month_fmt.format(year - 1, 12),
                          11))
            ticks.append((self.month_fmt.format(year - 1, 12),
                          self.month_fmt.format(year, 1),
                          12))
            ticks.append((self.month_fmt.format(year, 1),
                          self.month_fmt.format(year, 2), 1))
        elif quarter == 2 and now_str >= (year_str + '02'):
            for m in (2, 3, 4):
                ticks.append((self.month_fmt.format(year, m),
                              self.month_fmt.format(year, m + 1),
                              m))

        elif quarter == 3 and now_str >= (year_str + '05'):
            for m in (5, 6, 7):
                ticks.append((self.month_fmt.format(year, m),
                              self.month_fmt.format(year, m + 1),
                              m))
        elif quarter == 4 and now_str >= (year_str + '08'):
            for m in (8, 9, 10):
                ticks.append((self.month_fmt.format(year, m),
                              self.month_fmt.format(year, m + 1),
                              m))

        return ticks

    def get_month_day_chart_ticks(self, month, days=0):
        prefix = '{}-'.format(MONTH_DAYS[int(month) - 1])
        return ['{}{:02}'.format(prefix, i) for i in range(1, days + 1)]

    def get_month_day_ticks(self, year, month):
        ticks = []
        dt = datetime(year, month, 1)
        day_str = datetime.now().strftime(self.folder_day_fmt)
        i = 1
        while i <= 31:
            i += 1
            if dt.strftime(self.folder_day_fmt) > day_str:
                break

            ticks.append((dt.strftime(self.day_fmt),
                          (dt + ONE_DAY).strftime(self.day_fmt),
                          dt.strftime(self.folder_day_fmt),
                          ))
            dt += ONE_DAY
            if dt.month != month:
                break

        return ticks

    def get_week_chart_ticks(self, days=[]):
        return [parse(d).strftime('%b-%d') for d in days]

    def get_week_ticks(self, year, week):
        ticks = []
        dt = datetime(year, 1, 1) + timedelta(weeks=week) - ONE_DAY
        # we use Tuesday as the first day of one week for the statistic
        dt = dt - ONE_DAY * (dt.weekday() - 1)
        day_str = datetime.now().strftime(self.folder_day_fmt)
        for i in range(7):
            if dt.strftime(self.folder_day_fmt) > day_str:
                break

            ticks.append((dt.strftime(self.day_fmt),
                          (dt + ONE_DAY).strftime(self.day_fmt),
                          dt.strftime(self.folder_day_fmt)))
            dt += ONE_DAY

        return ticks

    def get_day_chart_ticks(self, hours=[]):
        ticks = []
        for hour in hours:
            dt = parse(hour)
            if dt.hour == 0:
                ticks.append(dt.strftime('%b-%m 00:00'))
            else:
                ticks.append(dt.strftime('%H:00'))

        return ticks

    def get_day_ticks(self, day):
        ticks = []
        day = day.replace(hour=6)
        hour_str = datetime.now().strftime(self.folder_hour_fmt)
        for h in range(24):
            if day.strftime(self.folder_hour_fmt) > hour_str:
                break

            ticks.append((day.strftime(self.hour_fmt),
                          (day + ONE_HOUR).strftime(self.hour_fmt),
                          day.hour))
            day += ONE_HOUR

        return ticks
