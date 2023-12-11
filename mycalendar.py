import calendar
import datetime as dt
import numpy as np
from database_connection import CURSOR, Database
import pandas as pd
from pytz import timezone
from dateutil.relativedelta import *

db = Database()


class Calendar:

    def __init__(self):
        calendar.setfirstweekday(calendar.SUNDAY)
        dt.datetime.now(timezone('CET'))
        self.current_complete_date = dt.datetime.now().date()
        self.day = dt.datetime.now().day
        self.month = dt.datetime.now().month
        self.year = dt.datetime.now().year
        self.current_month = calendar.monthcalendar(self.year, self.month)
        self.month_selected = None
        self.month_name = calendar.month_name[self.month]
        print(self.month_name)
        self.current_month_year = f'{self.month}/{self.year}'
        self.current_year_month = f"{self.year}-{self.month}"
        self.business_days()
        self.month_days_count = calendar.monthrange(self.year, self.month)[1]


    def select_month(self, *args):
        if not args[0] is None:
            print(args[0])
            x = args[0].split("-")
            year = int(x[0])
            month = int(x[1])
            print(year, month)
            self.month = month
            self.year = year
            self.month_selected = calendar.monthcalendar(self.year, self.month)
        else:
            self.month = dt.datetime.now().month
            self.year = dt.datetime.now().year
            self.month_selected = self.current_month

    def date_format(self, format):
        operator = ''
        for s in format:
            if s == "-" or s == "/" or s == ".":
                operator = s
        splited = format.split(operator)
        complete_date_list = []
        for x in splited:
            if x.count("m"):
                if len(str(x)) == len(str(self.month)):
                    final_month = str(self.month)
                else:
                    final_month = f"0{self.month}"
                complete_date_list.append(final_month)
            elif x.count("y"):
                if len(str(x)) == len(str(self.year)):
                    final_year = str(self.year)
                else:
                    final_year = str(self.year)[x.count("y"):]
                complete_date_list.append(final_year)
            elif x.count("d"):
                if len(str(x)) == len(str(self.day)):
                    final_day = str(self.day)
                else:
                    final_day = f"0{self.day}"
                complete_date_list.append(final_day)
        complete_date = operator.join(complete_date_list)
        return complete_date

    def business_days(self):
        month_now = self.date_format("yyyy-mm")
        next_month = self.current_complete_date + relativedelta(months=+1)
        if len(str(next_month.month)) == 1:
            next_month = f"{next_month.year}-0{next_month.month}"
        else:
            next_month = f"{next_month.year}-{next_month.month}"
        business_days = np.busday_count(month_now, next_month)
        return business_days

    def annual_leaves(self, user):
        CURSOR.execute(f'''SELECT HIRE_DATE FROM t_employees where ID = '{user}';''')
        data = CURSOR.fetchone()[0]
        split_date = data.split("-")
        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])
        start_date = dt.datetime(year, month, day)
        num_months = (self.year - start_date.year) * 12 + (self.month - start_date.month)
        annual_days = int(round(num_months * 1.7, 0))
        return annual_days

    def timesheet_completed(self, *args):
        if args:
            """ Return a percent for timesheet completed from the current month for a user"""
            CURSOR.execute(
                f'''SELECT count(*) FROM t_req_timesheet WHERE USER_ID = '{args[0]}' AND DATE LIKE '{self.date_format("yyyy-mm")}-%'; ''')
            data = CURSOR.fetchall()[0][0]
            percent = (data / self.business_days()) * 100
            return int(round(percent, 0))
        else:
            """ Return a percent for timesheet completed from the current month for all user"""
            CURSOR.execute(
                f'''SELECT count(*) FROM t_req_timesheet WHERE DATE LIKE '{self.date_format("yyyy-mm")}-%'; ''')
            data = CURSOR.fetchall()[0][0]
            percent = (data / self.business_days()) * 100
            return int(round(percent, 0))

    def timeoff_days(self, user, day):
        dates_list = []
        if len(str(day)) == 1:
            date = f"{self.date_format('yyyy-mm')}-0{day}"
        else:
            date = f"{self.date_format('yyyy-mm')}-{day}"
        db_data = db.Select("v_req_time_off").where(user_id=user)
        for data in db_data:
            if data[8] == 2:
                date_range = pd.date_range(data[5], data[6])
                for dt in date_range:
                    string_dt = str(dt)[:10]
                    dates_list.append(string_dt)
        if date in dates_list:
            return True
        else:
            return False

    def timeoff_days_list(self, day):
        if len(str(day)) == 1:
            date = f"{self.date_format('yyyy-mm')}-0{day}"
        else:
            date = f"{self.date_format('yyyy-mm')}-{day}"
        db_data = db.Select("v_req_time_off").all()

        for data in db_data:
            if data[8] == 2:
                date_range = pd.date_range(data[5], data[6])
                data_list = []
                if date in date_range:
                    data_list.append(data)
                    return data_list

    def day_check(self, day, user):
        db_check = db.Select("t_req_timesheet").where(date=f"{self.date_format('yyyy-mm')}-{day}", user_id=user)
        if len(db_check) == 0:
            return ''
        else:
            status = db_check[0][2]
            if status == 1:
                return 'background-color: #fff5cc;'
            elif status == 2:
                return 'background-color: #ccffcc;'
            elif status == 3:
                return 'background-color: #ffcccc;'

    def off_today(self):
        off_list = []
        users = db.Select("v_employees").all()

        for user in users:
            off = self.timeoff_days(user[0], self.day)
            if off:
                off_list.append(user[3])
        return off_list


def select_month(year, month):
    selected_month = calendar.monthcalendar(year, month)
    return selected_month
