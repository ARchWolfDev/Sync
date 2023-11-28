import datetime

from database_connection import Database
from mycalendar import Calendar
import json
import pandas as pd
import calendar


class Dashboard(Calendar, Database):

    def __init__(self, filter_by):
        super().__init__()
        self.select_month(filter_by)
        self.date = f"{self.year}-{self.month}"
        self.date_yyyy_mm = self.date_format("yyyy-mm")
        self.month_name = calendar.month_name[self.month]

    def all_employees_count(self):
        """All employees count until a specified date"""
        employees_number = self.Select("v_employees").where(operator="<=", hire_date=f"{self.date_yyyy_mm}%")
        employees_count = len(employees_number)
        return employees_count

    def hired_on_selected_month(self):
        """All employees that has been hired on selected month"""
        employees_number = self.Select("v_employees").where(operator="like", hire_date=f"{self.date_yyyy_mm}%")
        employees_count = len(employees_number)
        return employees_count

    def percent_by_department(self, department_id):
        all_employees_count = self.Select("v_employees").count()
        employees_from_department = len(self.Select("v_employees").where(department_id=department_id))
        percent = (employees_from_department/all_employees_count) * 100
        return round(percent)

    def month_in_progres(self):
        currtent = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}"
        if self.date == currtent:
            percent = (self.day / self.business_days()) * 100
            return round(percent)
        elif self.date < currtent:
            return 100
        else:
            return 0

    def month_status(self):
        if self.month_in_progres() == 100:
            return '<span class="badge text-bg-success" style="float:right;">Completed</span>'
        elif self.month_in_progres() < 100:
            return '<span class="badge text-bg-secondary" style="float:right;">In progress</span>'
        else:
            return '<span class="badge text-bg-light" style="float:right;">Not started yer</span>'

    def employee_list(self):
        """ Return a list of all employees in json type for Timesheet CHART"""
        all_employees = self.Select("v_employees").where(operator="<=", hire_date=f"{self.date}%")
        data_list = [x[3] for x in all_employees]
        return json.dumps(data_list)

    def timesheet_completed_list(self):
        """ Return a list from timesheet for all employees table for Timesheet CHART """
        tsc = []
        employees = self.Select("v_employees").where(operator="<=", hire_date=f"{self.date}-%")
        for _ in employees:
            ts_data = self.Select("v_req_timesheet").where(user_id=_[0], date=f"{self.date}-%")
            percent = (len(ts_data) / self.business_days()) * 100
            tsc.append(round(percent))
        return tsc

    def departments_list(self):
        all_departments = self.Select("t_departments").all()
        departments_list = [dep[1] for dep in all_departments]
        return json.dumps(departments_list)

    def percent_by_department_chart(self):
        percent_list = []
        all_departments = self.Select("t_departments").all()
        for x in all_departments:
            percent = self.percent_by_department(x[0])
            percent_list.append(percent)
        return percent_list

    def timesheet_count(self, status):
        date = f"{self.date}%"
        data = self.Select("v_req_timesheet").where(date=date, status=status)
        return len(data)

    def average_timesheet(self):
        all_requests = self.Select("v_req_timesheet").where(operator="like", date=f"{self.date}-%")
        per_employees = len(all_requests) / self.Select("v_employees").count()
        completed = round((per_employees / self.business_days()) * 100)
        not_completed = 100 - completed
        average_list = [completed, not_completed]
        return average_list

    def people_off_in_calendar(self, day):
        date_list = []
        date_y_m = self.date_format("yyyy-mm")
        if len(str(day)) == 1:
            day = f"0{day}"
        else:
            day = day
        complete_current_date = f"{date_y_m}-{day}"
        db_dates = self.Select("v_req_time_off").all()
        for db_dt in db_dates:
            if db_dt[8] == 2:
                date_range = pd.date_range(db_dt[5], db_dt[6])
                for dr in date_range:
                    string_dt = str(dr)[:10]
                    date_list.append(string_dt)
        if complete_current_date in date_list:
            return True
        else:
            return False
