import calendar
import datetime as dt
import numpy as np
from database_connection import CURSOR, Database
import pandas as pd

db = Database()


class Calendar:

    def __init__(self):
        calendar.setfirstweekday(calendar.SUNDAY)
        self.day = dt.datetime.now().day
        self.month = dt.datetime.now().month
        self.year = dt.datetime.now().year
        self.current_month = calendar.monthcalendar(self.year, self.month)
        self.month_name = calendar.month_name[self.month]
        self.current_month_year = f'{self.month}/{self.year}'
        self.current_year_month = f"{self.year}-{self.month}"
        self.business_days()

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
        next_month = self.month + 1
        if next_month > 12:
            next_month = 1
        if len(str(next_month)) == 1:
            next_month = f"{self.year}-0{next_month}"
        else:
            next_month = f"{self.year}-{next_month}"
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


def select_month(year, month):
    selected_month = calendar.monthcalendar(year, month)
    return selected_month
