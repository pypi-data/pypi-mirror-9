from dateutil import parser
import datetime


def str_to_date(s):
    try:
        return parser.parse(s).date()
    except Exception, ex:
        pass
    return s


def date_to_str(d):
    if type(d) is str:
        return d
    return d.strftime('%Y-%m-%d')


krx_holidays = [
    '2008-01-01', '2008-02-06', '2008-02-07', '2008-02-08', '2008-04-09',
    '2008-05-01', '2008-05-05', '2008-05-12', '2008-06-06', '2008-08-15',
    '2008-09-15', '2008-10-03', '2008-12-25', '2008-12-31',

    '2009-01-01', '2009-01-26', '2009-01-27', '2009-05-01', '2009-05-05',
    '2009-10-02', '2009-12-25', '2009-12-31',

    '2010-01-01', '2010-02-15', '2010-03-01', '2010-05-05', '2010-05-21',
    '2010-06-02', '2010-09-21', '2010-09-22', '2010-09-23', '2010-12-31',

    '2011-02-02', '2011-02-03', '2011-02-04', '2011-03-01', '2011-05-05',
    '2011-05-10', '2011-06-06', '2011-08-15', '2011-09-12', '2011-09-13',
    '2011-10-03', '2011-12-30',

    '2012-01-23', '2012-01-24', '2012-03-01', '2012-04-11', '2012-05-01',
    '2012-05-28', '2012-06-06', '2012-08-15', '2012-10-01', '2012-10-03',
    '2012-12-19', '2012-12-25', '2012-12-31',

    '2013-01-01', '2013-02-11', '2013-03-01', '2013-05-01', '2013-05-17',
    '2013-06-06', '2013-08-15', '2013-09-18', '2013-09-19', '2013-09-20',
    '2013-10-03', '2013-10-09', '2013-12-25', '2013-12-31',

    '2014-01-01', '2014-01-30', '2014-01-31', '2014-05-01', '2014-05-05',
    '2014-05-06', '2014-06-04', '2014-06-06', '2014-08-15', '2014-09-08',
    '2014-09-09', '2014-09-10', '2014-10-03', '2014-10-09', '2014-12-25',
    '2014-12-31',

    '2015-01-01', '2015-02-18', '2015-02-19', '2015-02-20', '2015-05-01',
    '2015-05-05', '2015-05-25', '2015-09-28', '2015-09-29', '2015-10-09',
    '2015-12-25', '2015-12-31',

    '2016-01-01', '2016-02-08', '2016-02-09', '2016-02-10', '2016-03-01',
    '2016-04-13', '2016-05-05', '2016-06-06', '2016-08-15', '2016-09-14',
    '2016-09-15', '2016-09-16', '2016-10-03', '2016-12-30',
]


def is_holiday(date):
    date_string = date
    if type(date) is type(''):
        pass
    else:
        # datetime.date is assumed
        date_string = date_to_str(date)

    if date_string in krx_holidays:
        return True

    date = str_to_date(date_string)
    weekday = date.weekday()
    if weekday == 5 or weekday == 6:
        return True
    return False


def _get_neighbor_trading_date(cur_date, direction):
    is_string = False
    if type(cur_date) is type(''):
        is_string = True
        cur_date = str_to_date(cur_date)
    while True:
        cur_date += datetime.timedelta(days=direction)
        if is_holiday(cur_date):
            continue
        weekday = cur_date.weekday()
        if weekday == 5 or weekday == 6:
            continue

        if is_string:
            return date_to_str(cur_date)
        return cur_date


def get_next_trading_date(cur_date):
    return _get_neighbor_trading_date(cur_date, 1)


def get_prev_trading_date(cur_date):
    return _get_neighbor_trading_date(cur_date, -1)
