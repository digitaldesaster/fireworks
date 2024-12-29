#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, datetime

#dont write pyc files!
sys.dont_write_bytecode = True

#returns isoDates
class dbDates():
    now = datetime.datetime.now()
    #print now.weekday()
    today = datetime.datetime(now.year,now.month,now.day)
    def firstDayThisMonth(self):
        date = self.today.replace(day=1)
        return date
    def firstDayLastMonth(self):
        date = self.today.replace(day=1,month=self.now.month-1)
        return date
    def firstDayNextMonth(self):
        date = self.today.replace(month=self.now.month+1, day=1)
        return date
    def firstDayThisYear(self):
        date = self.today.replace(month=1,day=1)
        return date
    def firstDayNextYear(self):
        date = self.today.replace(year=self.now.year+1,month=1,day=1)
        return date
    def thisYear(self):
        return {'$gte': self.firstDayThisYear(), '$lt': self.firstDayNextYear()}
    def thisMonth(self):
        return {'$gte': self.firstDayThisMonth(), '$lt': self.firstDayNextMonth()}
    def lastMonth(self):
        return {'$gte': self.firstDayLastMonth(), '$lt': self.firstDayThisMonth()}
    def thisWeek(self):
        start = self.today - datetime.timedelta(days=self.today.weekday())
        end = start + datetime.timedelta(days=7)
        return {'$gte': start, '$lt': end}
    def thisDay(self):
        return self.today
    def yesterDay(self):
        return self.today - datetime.timedelta(days=1)
    def tomorrow(self):
        return self.today + datetime.timedelta(days=1)
