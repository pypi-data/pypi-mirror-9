import krxholiday as kh


print kh.is_holiday('2013-01-01')
print kh.is_holiday('2013-01-02')

print kh.get_next_trading_date('2013-12-30')
print kh.get_next_trading_date('2013-12-31')
print kh.get_next_trading_date('2014-01-01')
print kh.get_next_trading_date('2014-01-02')
print kh.get_next_trading_date('2014-01-03')

print kh.get_prev_trading_date('2013-12-30')
print kh.get_prev_trading_date('2013-12-31')
print kh.get_prev_trading_date('2014-01-01')
print kh.get_prev_trading_date('2014-01-02')
print kh.get_prev_trading_date('2014-01-03')

