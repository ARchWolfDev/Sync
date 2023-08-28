from database_connection import Database
import json
from mycalendar import Calendar
import pandas as pd

db = Database()
calendar = Calendar()


class Dashboard:

    def __init__(self, filter_by=0):
        self.filter = filter_by
        self.list = self.List(self.filter)
        self.count = self.Count(self.filter)

    class List:

        def __init__(self, filter_by):
            self.filter_by = filter_by
            if type(self.filter_by) == dict:
                self.filter_on = True
                for key, value in self.filter_by.items():
                    new_value = f"{value}"
                    self.filter_by[key] = new_value.replace("[", "(").replace("]", ")")

        def employee(self):
            date = ""
            try:
                date = self.filter_by['date']
                del self.filter_by['date']
            except:
                pass
            data = db.Select("v_employees").where(condition=self.filter_by)[0]
            data_list = [x[3] for x in data]
            data_list2 = json.dumps(data_list)
            if len(data) > 0:
                self.filter_by['date'] = date
            return data_list2

        def timesheet(self):
            """ Return a list from timesheet table for Timesheet CHART"""
            date = ""
            try:
                date = self.filter_by['date']
                del self.filter_by['date']
            except:
                pass
            tsc = []
            data = db.Select("v_employees").where(condition=self.filter_by)[0]
            for _ in data:
                ts_data = db.Select("v_req_timesheet").where(user_id=_[0], date=date)
                percent = (len(ts_data) / calendar.business_days()) * 100
                tsc.append(int(round(percent, 0)))
            if len(data) > 0:
                self.filter_by['date'] = date
            return tsc

        def average_timesheet(self):
            try:
                print(self.filter_by["date"])
            except:
                self.filter_by['date'] = f"{calendar.date_format('yyyy-mm')}-%"
            data = db.Select("v_req_timesheet").where(condition=self.filter_by)[0]
            print(data)
            print(len(data))
            print(self.filter_by["date"])
            completed = int(round((len(data) / calendar.business_days()) * 100, 0))
            not_completed = 100 - completed
            print(completed)
            average_list = [completed, not_completed]
            print(average_list)
            return average_list

        def projects(self):
            name_project_list = []
            projects = db.Select("t_projects").all()

            for name in projects:
                name_project_list.append(name[2])
            return json.dumps(name_project_list)

    class Count:

        def __init__(self, filter_by):

            self.filter_by = filter_by
            if type(self.filter_by) == dict:
                self.filter_on = True
                for key, value in self.filter_by.items():
                    new_value = f"{value}"
                    self.filter_by[key] = new_value.replace("[", "(").replace("]", ")")

        def projects(self):
            project_filter = self.filter_by
            projects = db.Select("t_projects").all()
            percent_project_list = []

            for project in projects:
                project_filter['project_id'] = project[0]
                data = db.Select("v_req_timesheet").where(condition=project_filter)[0]
                project_count = len(data)
                all_inputs = db.Select("v_req_timesheet").count()
                if all_inputs == 0:
                    percent = (project_count / 1) * 100
                else:
                    percent = (project_count / all_inputs) * 100
                percent_project_list.append(round(percent))
            del project_filter['project_id']
            return percent_project_list

        def timesheet(self, status):
            timesheet_filter = self.filter_by
            timesheet_filter['status'] = status
            try:
                print(timesheet_filter["date"])
            except:
                timesheet_filter['date'] = f"{calendar.date_format('yyyy-mm')}-%"
            data = db.Select("v_req_timesheet").where(condition=timesheet_filter)[0]
            del timesheet_filter['status']
            return len(data)

        def timeoff(self, status, id):
            time_off_filter = self.filter_by
            time_off_filter['status'] = status
            try:
                time_off_filter['start_date'] = time_off_filter["date"]
                del time_off_filter["date"]
            except:
                time_off_filter['start_date'] = f"{calendar.date_format('yyyy-mm')}-%"

            if id == "other":
                time_off_filter['type_id'] = "n('AN', 'MD')"
                data = db.Select("v_req_time_off").where(condition=time_off_filter)[0]
            elif id == "all":
                data = db.Select("v_req_time_off").where(condition=time_off_filter)[0]
            else:
                time_off_filter['type_id'] = id
                data = db.Select("v_req_time_off").where(condition=time_off_filter)[0]
            try:
                del time_off_filter['type_id']
            except KeyError:
                pass
            del time_off_filter['status']
            time_off_filter['date'] = time_off_filter['start_date']
            del time_off_filter['start_date']

            return len(data)

        def requests(self, status):
            data = db.Select("v_req_tickets").where(status=status)
            return len(data)


    def calendar(self, day):
        date_list = []
        date_y_m = calendar.date_format("yyyy-mm")
        if len(str(day)) == 1:
            day = f"0{day}"
        else:
            day = day
        complete_current_date = f"{date_y_m}-{day}"
        db_dates = db.Select("v_req_time_off").all()
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

    def off_today(self):
        off_list = []
        users = db.Select("v_employees").all()

        for user in users:
            off = calendar.timeoff_days(user[0], calendar.day)
            if off:
                off_list.append(user[3])
        return off_list

    def role_department(self, department_id):
        data = db.Select("t_roles").where(department_id=department_id)
        name = [x[1] for x in data]
        return name