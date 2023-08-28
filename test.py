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

