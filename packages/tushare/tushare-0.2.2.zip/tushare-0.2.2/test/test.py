# -*- coding:utf-8 -*- 

import tushare.stock.cons as ct
import tushare.stock.trading as td
import tushare.stock.fundamental as fd


if __name__ == '__main__':
#     df = td.get_hist_data('cyb')
#     print df#.ix['2015-01-26 10:30:00']
#     print td.get_realtime_quotes(['600848','sh','sz','000981','zxb','cyb'])
#     print fd.get_stock_basics()
#     df.to_csv('c:\\allstocks.csv')
    
    print td.get_tick_data('600848',date='2015-02-04')
#     print fd.get_report_data(2013,4)
#     print fd.get_profit_data(1999,2)
#     print fd.get_operation_data(1999,2)
#     print fd.get_growth_data(2014,3)
#     print fd.get_debtpaying_data(2014,2)    
#     print fd.get_cashflow_data(2014,2)
#     print fd.get_stock_basics()