import calendar
import datetime as dt
import numpy as np
from database_connection import CURSOR


class Calendar:

    def __init__(self):
        calendar.setfirstweekday(calendar.SUNDAY)
        self.day = dt.datetime.now().day
        self.month = dt.datetime.now().month
        self.year = dt.datetime.now().year
        self.current_month = calendar.monthcalendar(self.year, self.month)
        self.month_name = calendar.month_name[self.month]
        self.business_days()

    def business_days(self):
        month_now = f"{self.year}-0{self.month}"
        next_month = self.month + 1
        if next_month > 12:
            next_month = 1

        next_month = f"{self.year}-0{next_month}"
        business_days = np.busday_count(month_now, next_month)
        return business_days

    def annual_leaves(self, user):
        CURSOR.execute(f'''SELECT HIRE_DATE FROM EMPLOYEE where ID = {user}''')
        data = CURSOR.fetchone()[0]
        split_date = data.split("-")
        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])
        start_date = dt.datetime(year, month, day)
        num_months = (self.year - start_date.year) * 12 + (self.month - start_date.month)
        annual_days = int(round(num_months * 1.7, 0))
        return annual_days

    def timesheet_completed(self, user):
        CURSOR.execute(f'''SELECT count(*) FROM REQ_TIMESHEET WHERE USER_ID = {user}; ''')
        data = CURSOR.fetchall()[0][0]
        percent = (data / self.business_days()) * 100
        return int(round(percent, 0))


def select_month(year, month):
    selected_month = calendar.monthcalendar(year, month)
    return selected_month
