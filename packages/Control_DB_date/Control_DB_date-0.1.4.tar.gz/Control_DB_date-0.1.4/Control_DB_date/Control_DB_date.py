#coding:utf-8
from datetime import datetime
from datetime import timedelta
import time

class Match_db_date(object):
    """
    Match = Match_db_date()
    import json
    print json.dumps(Match.to_match('2014-01-11','2014-08-22'))
    """
    def getMonthDays(self, year, month ):
        day = 31                #定义每月最多的天数
        while day:
            try:
                time.strptime( '%s-%s-%d'%( year, month, day ), '%Y-%m-%d' )      #尝试将这个月最大的天数的字符串进行转化
                return day      #成功时返回得就是这个月的天数
            except:
                day -= 1        #否则将天数减1继续尝试转化, 直到成功为止

    def fit_date_format(self,year,month):
        if month<10:
            str_db = "buzz_v1_%s0%s"%(year,month)
        else:
            str_db = "buzz_v1_%s%s"%(year,month)
        return str_db
    
    def to_match(self,start,end):
        dc = {}
        opt_start_time = datetime.strptime(start,"%Y-%m-%d")
        opt_end_time = datetime.strptime(end,"%Y-%m-%d")
        count_month = opt_end_time.month - opt_start_time.month
        if count_month == 0:
            """buzz_v1_201502"""
            str_db = "buzz_v1_%s"%opt_start_time.strftime('%Y%m')
            dc[str_db] = [start,end]
            return dc
    
        for i in range(0,count_month+1):
            if i == 0:
                year = opt_start_time.year
                month = opt_start_time.month
                dc[self.fit_date_format(year,month)] = [start,"%s-%s-%s"%(year,month,self.getMonthDays(year,month))]
    
            elif i == count_month:
                year = opt_end_time.year
                month = opt_end_time.month
                day = opt_end_time.month
                dc[self.fit_date_format(year,month)] = ["%s-%s-01"%(year,month),end]
    
            else:
                year = opt_start_time.year
                month = opt_start_time.month+i
                if month<=12:
                    dc[self.fit_date_format(year,month)] = ["%s-%s-01"%(year,month),"%s-%s-%s"%(year,month,self.getMonthDays(year,month) )]
                else:
                    year = month / 12 + year
                    month = month % 12
                    dc[self.fit_date_format(year,month)] = ["%s-%s-01"%(year,month),"%s-%s-%s"%(year,month,getMonthDays(year,month))]
    
        return dc
    
