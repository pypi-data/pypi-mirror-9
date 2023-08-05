# -*- coding:utf-8 -*- 

import tushare.stock.cons as ct
import tushare.stock.trading as td
import tushare.stock.fundamental as fd


import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


if __name__ == '__main__':
    df = fd.get_stock_basics()
    df.to_csv('c:\\allstocks.csv')
    
    
#     print get_report_data(2013,4)
#     print get_profit_data(1999,2)
#     print get_operation_data(1999,2)
#     print get_growth_data(2014,3)
#     print get_debtpaying_data(2014,2)    
#     print get_cashflow_data(2014,2)
#     print get_stock_basics()