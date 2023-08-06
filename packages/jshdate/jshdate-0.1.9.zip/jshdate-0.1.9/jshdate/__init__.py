#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import datetime, timedelta
from dateutil.parser import parse

ONE_DAY = timedelta(days=1)
ONE_HOUR = timedelta(hours=1)
SHIFT_MINUTE = '30'
MONTH_FMT = '{}-{:02}-01 06:%s:00'
DAY_FMT = '%Y-%m-%d 06:{}:00'
HOUR_FMT = '%Y-%m-%d %H:{}:00'

# folder name format for day
FOLDER_DAY_FMT = '%Y%m%d'

# folder name format for hour
FOLDER_HOUR_FMT = '%Y%m%d%H'
QUARTERS = ['Q1 (Nov ~ Jan)', 'Q2 (Feb ~ Apr)', 'Q3 (May ~ Jul)',
            'Q4 (Aug ~ Oct)']
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
               'Oct', 'Nov', 'Dec']
WEEK_LIST = [('{}'.format(i), 'WWK{}'.format(i)) for i in range(1, 53)]


class JshDate(object):
    def __init__(self, **kwargs):
        self.shift_minute = kwargs.get('shift_minute', SHIFT_MINUTE)

        month_fmt = kwargs.get('month_fmt', MONTH_FMT)
        self.month_fmt = month_fmt % self.shift_minute

        day_fmt = kwargs.get('day_fmt', DAY_FMT)
        self.day_fmt = day_fmt.format(self.shift_minute)

        hour_fmt = kwargs.get('hour_fmt', HOUR_FMT)
        self.hour_fmt = hour_fmt.format(self.shift_minute)

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

    def get_year_chart_ticks(self, seqs=[], kind='quarter'):
        if kind == 'quarter':
            return [QUARTERS[i] for i, _ in enumerate(seqs)]

        ticks = []
        for d in seqs:
            dt = parse(d[0])
            if dt.month == 1:
                ticks.append(dt.strftime('%Y-%b'))
            else:
                ticks.append(dt.strftime('%b'))

        return ticks

    def get_year_ticks(self, year, month=0, quarter=0):
        # Month view and Quarter View
        # Nov, Dec, Jan, ..., Oct
        # Q1: Nov ~ Jan, Q2: Feb ~ Apr
        # Q3: May ~ Jul, Q4: Aug ~ Oct
        year = int(year)
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
            now_str = now.strftime('%Y%m')
            last_year = year - 1
            month_ticks = [(self.month_fmt.format(last_year, 11),
                           self.month_fmt.format(last_year, 12),
                           11),
                           (self.month_fmt.format(last_year, 12),
                           self.month_fmt.format(year, 1),
                           12),
                           ]

            for i in range(1, 11):
                if now_str < '{}{:02}'.format(year, i):
                    break

                month_ticks.append((self.month_fmt.format(year, i),
                                   self.month_fmt.format(year, i + 1),
                                   i))

            qt_ticks = [(self.month_fmt.format(last_year, 11),
                         self.month_fmt.format(year, 2),
                         1)]
            for i, q in enumerate((2, 5, 8)):
                if now_str < '{}{:02}'.format(year, q):
                    break

                qt_ticks.append((self.month_fmt.format(year, q),
                                 self.month_fmt.format(year, q + 3),
                                 i + 2))

        return month_ticks, qt_ticks

    def get_quarter_chart_ticks(self, seqs):
        return [MONTH_NAMES[qt[-1] - 1] for qt in seqs]

    def get_quarter_ticks(self, year, quarter):
        # Q1: Nov ~ Jan, Q2: Feb ~ Apr
        # Q3: May ~ Jul, Q4: Aug ~ Oct
        year = int(year)
        quarter = int(quarter)
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
                          self.month_fmt.format(year, 2),
                          1))
        elif quarter == 2 and now_str >= (year_str + '02'):
            for m in (2, 3, 4):
                if now_str < (year_str + '0{}'.format(m)):
                    break

                ticks.append((self.month_fmt.format(year, m),
                              self.month_fmt.format(year, m + 1),
                              m))

        elif quarter == 3 and now_str >= (year_str + '05'):
            for m in (5, 6, 7):
                if now_str < (year_str + '0{}'.format(m)):
                    break

                ticks.append((self.month_fmt.format(year, m),
                              self.month_fmt.format(year, m + 1),
                              m))
        elif quarter == 4 and now_str >= (year_str + '08'):
            for m in (8, 9, 10):
                if now_str < (year_str + '0{}'.format(m)):
                    break

                ticks.append((self.month_fmt.format(year, m),
                              self.month_fmt.format(year, m + 1),
                              m))

        return ticks

    def get_month_day_chart_ticks(self, seqs):
        return [parse(d[0]).strftime('%b-%d') for d in seqs]

    def get_month_day_ticks(self, year, month):
        ticks = []
        dt = datetime(int(year), int(month), 1)
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
        return [parse(d[0]).strftime('%b-%d') for d in days]

    def get_week_ticks(self, year, week):
        ticks = []
        dt = datetime(int(year), 1, 1) + timedelta(weeks=int(week)) - ONE_DAY
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

    def get_day_chart_ticks(self, seqs=[]):
        ticks = []
        for seq in seqs:
            dt = parse(seq[0])
            if dt.hour == 0:
                fmt = '%b-%d 00:{}'.format(self.shift_minute)
                ticks.append(dt.strftime(fmt))
            else:
                ticks.append(dt.strftime('%H:{}'.format(self.shift_minute)))

        return ticks

    def get_day_ticks(self, day):
        ticks = []
        if isinstance(day, basestring):
            day = parse(day)

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

    def get_quarter_choices(self, year=None):
        now = datetime.now()
        if not year or int(year) >= now.year:
            qt = self.get_current_quarter()
        else:
            qt = 4

        return [('{}'.format(i + 1), QUARTERS[i]) for i in range(qt)]

    def get_month_choices(self, year=None):
        now = datetime.now()
        if not year or int(year) >= now.year:
            months = MONTH_NAMES[:now.month]
        else:
            months = MONTH_NAMES[:]

        return [('{}'.format(i + 1), m) for i, m in enumerate(months)]

    def get_week_choices(self, year=None):
        now = datetime.now()
        if not year or int(year) >= now.year:
            week = int(now.strftime('%W'))
            if week == 53:
                week = 52

            if week == 0:
                week = 1

            seqs = self.get_week_ticks(year or now.year, week)
            if not seqs:
                week -= 1

            return WEEK_LIST[:week]

        return WEEK_LIST[:]
