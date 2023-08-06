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
]


def is_holiday(date):
    date_string = date
    if type(date) is type(''):
        pass
    else:
        # datetime.date is assumed
        date_string = date_to_str(date)
    return date_string in krx_holidays


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
