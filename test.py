import json
import database_connection
import mycalendar
import notification
from mycalendar import Calendar
from database_connection import Database
import database_connection as database
from database_connection import User
import files
import calendar
import numpy as np
from dashboard import Dashboard
import dashboard
import pandas as pd
import csv
import base64
import send_email

db = Database()
dash = Dashboard()
db_out = database_connection

cal = calendar
cale = Calendar()

PATH = 'static/csv/'
filename = 'timesheet_2023-08-17.csv'

data = {'user_id': 'EMP-1001', 'date': '2023-08-22', 'role_id': 'ROL-101', 'department_id': 'DEP-101', 'project_id': 'PROJ-101', 'TSK-102': '1', 'TSK-103': '1'}


x = db.Select("t_req_timesheet_tasks").where(id="TSH-10104")
print(x)

da

# month = list(cal.month_name)

# print(month)
# dict_months = {}
# num_month = []
# for x in range(1, 13):
#     dict_months[x] = month[x]
#
# print(dict_months)


# # def bd_count():
# #     db.CURSOR.execute(f'''SELECT * FROM REQ_TIMEOFF WHERE USER_ID = {user}''')
# #     dates = db.CURSOR.fetchall()[0]
# #     start = dates[3]
# #     end = dates[4]
# #
# #     print(start)
# #     print(end)
# #
# #     bd = np.busday_count(start, end)
# #     print(bd)
# #
# # # last day of a month
# # ddata = calendar.monthrange(year, month)[1]
# # print(ddata)
# #
# # db.CURSOR.execute(f'''SELECT * FROM REQ_TIMEOFF''')
# # data = db.CURSOR.fetchall()
# month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
# # for _ in data:
# #     if _[1] == 'ANL' and _[5] == 2:
# #         start_day = _[3][8:]
# #         last_day_of_month = ddata
# #         complete_start_date = _[3]
# #         last_date_of_month = f"{_[3][:8]}{ddata}"
# #         print(complete_start_date, last_date_of_month)
# #         count_days = np.busday_count(complete_start_date, last_date_of_month)
# #         print(count_days)
#
# db.CURSOR.execute(f'''SELECT * FROM REQ_TIMEOFF''')
# data = db.CURSOR.fetchall()
# # print(data)
# # for _ in data:
# #     month = _[3][5:7]
# #     if month in month_list and _[1] == 'ANL':
# #         print(month)
#
# # view = db.select_all("REQ_TIMEOFF_VIEW")
# # for _ in view:
# #     print(_)
#
# # id = 100120230330
# # al = cal.al_bd_count(id)
# # print(al)
# #
# #
# # table = db.check_table('request')
# # print(table)
#
# dash = dashboard
# dates = cal.timeoff_days(user, day)
# print(dates)
