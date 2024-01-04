import psycopg2.extras
import numpy as np
import os

import encoder
import send_email

CONNECTION = psycopg2.connect(database="syncdb", user="sync001", password="Fuckth3systemE@",
                              host="localhost", port="5432")
CURSOR = CONNECTION.cursor(cursor_factory=psycopg2.extras.DictCursor)


class Database:

    def __init__(self):
        self.select = self.Select()
        # self.insert = self.Insert()

    class Select:

        def __init__(self, *args, row="*", order=False, order_by="id", asc=True, limit="null"):
            self.row = row
            if order:
                self.order_by = order_by
                self.limit = limit
                if asc:
                    self.asc = "ASC"
                else:
                    self.asc = "DESC"
                self.extra = f"ORDER BY {self.order_by} {self.asc} LIMIT {self.limit}"
            else:
                self.extra = ""
            self.description = CURSOR.description
            if not args:
                self.current_date()
                self.current_timestamp()
            else:
                for arg in args:
                    self.table = arg

        def current_date(self):
            CURSOR.execute('''SELECT current_date;''')
            return CURSOR.fetchone()[0]

        def current_timestamp(self):
            CURSOR.execute('''SELECT current_timestamp;''')
            data = CURSOR.fetchone()[0]
            str_data = str(data).split(".")
            return str_data[0]

        def all(self):
            """SELECT everything from a specific table"""
            CURSOR.execute(f'''SELECT {self.row} FROM {self.table} {self.extra};''')
            return CURSOR.fetchall()

        def count(self, *args):
            """*args is for a specific column to be count"""
            condition = ''
            if not args:
                condition = "*"
            else:
                for arg in args:
                    condition = arg
            CURSOR.execute(f'''SELECT count({condition}) FROM {self.table}''')
            return CURSOR.fetchall()[0][0]

        def where(self, operator="=", **kwargs):
            """Select all conditioned. Operator is by default '=' but can be modified in 'like' or 'in'.
             Can be used dictionary too, EX: any=dict """
            key_type = ""
            value_type = ""
            for k, v in kwargs.items():
                key_type = k
                value_type = v

            if type(value_type) == dict:
                if len(kwargs[key_type]) == 0:
                    result = [self.all()]
                    return result
                else:
                    result = []
                    for k in kwargs:
                        # print("Kwargs", kwargs[k])
                        CURSOR.execute(self.multiplewhere(kwargs[k]))
                        result.append(CURSOR.fetchall())
                    return result

            elif len(kwargs) > 1:
                CURSOR.execute(self.multiplewhere(kwargs))
                return CURSOR.fetchall()
            else:
                for key, values in kwargs.items():
                    if type(values) == str:
                        values = f"'{values}'"
                    CURSOR.execute(f'''SELECT {self.row} FROM {self.table} WHERE {key.upper()} {operator} {values} {self.extra};''')
                    return CURSOR.fetchall()

        def multiplewhere(self, kwargs):
            where = []
            select = f"SELECT {self.row} FROM {self.table}"
            for key, values in kwargs.items():
                where.append(key)
                if len(str(values)) == 1:
                    where.append("=")
                    values = f"'{values}'"
                elif str(values)[1] == "%" or str(values)[-1] == "%":
                    where.append("LIKE")
                    values = f"'{values}'"
                elif str(values)[0] == "n" and str(values)[-1] == ")":
                    where.append("NOT IN")
                    values = values[1:]
                elif str(values)[0] == "(" or str(values)[-1] == ")":
                    where.append("IN")
                    values = values
                else:
                    where.append("=")
                    values = f"'{values}'"
                where.append(f"{values}")
                where.append("AND")
            where.pop(-1)
            q_where = " ".join(where)
            query = f"{select} WHERE {q_where};"
            # print(query)
            return query

    class Insert:

        def __init__(self, req_type, data):
            self.db = Database()
            self.table = self.db.Select("ct_type_table").where(type=req_type)[0][1]
            self.id = self.db.Select("cv_table_id").where(table_name=self.table)[0][3]
            self.data = data
            self.data['id'] = self.id

            if req_type == "timesheet":
                if self.db.Select("v_req_timesheet").where(date=data['date'], user_id=data['user_id']):
                    for duplicate in self.db.Select("v_req_timesheet").where(date=data['date'],
                                                                             user_id=data['user_id']):
                        self.db.Delete(req_type, duplicate[0])
                        self.db.Delete(req_type="timesheetTask", id=duplicate[0])
                self.timesheet()
            elif req_type == "timeOff":
                self.time_off()
            elif req_type == "tickets":
                self.tickets()
            elif req_type == "employee":
                self.employee()
            elif req_type == "tasksList":
                self.tasks()
            else:
                self.insert(self.data)

            self.update_id()

        def insert(self, data):
            column = []
            values = []

            for key, value in data.items():
                column.append(key)
                values.append(f"'{value}'")

            insert = f'INSERT INTO {self.table}({", ".join(column)}) VALUES ({", ".join(values)});'

            CURSOR.execute(insert)
            CONNECTION.commit()

        def timesheet(self):
            self.data['created_date'] = self.db.Select().current_date()
            self.data['status'] = 1
            for tsk in self.data.copy():
                if tsk[:3] == 'TSK':
                    task_data = {
                        'id': self.data['id'],
                        'task_id': tsk,
                        'date': self.data['date'],
                        'user_id': self.data['user_id']
                    }
                    del self.data[tsk]
                    self.table = "t_req_timesheet_tasks"
                    self.insert(task_data)
            self.table = "t_req_timesheet"
            self.insert(self.data)

        def time_off(self):
            self.data['status'] = 1
            self.data['number_of_days'] = np.busday_count(self.data['start_date'], self.data['end_date']) + 1
            self.insert(self.data)

            # Insert into t_emp_time_off
            req_type = "empTimeOff"
            row = self.data['type_id']
            current_number = self.db.Select("t_emp_time_off", row=row).where(id=self.data['user_id'])[0][0]
            number_of_days_str = str(self.data['number_of_days'])
            number_of_days_int = int(number_of_days_str)
            final_value = current_number - number_of_days_int
            used_time_off_days = {
                "id": self.data['user_id'],
                row: final_value
            }
            self.db.Update(req_type=req_type, data=used_time_off_days)

        def tickets(self):
            self.data['status'] = 1
            self.insert(self.data)

        def employee(self):
            # Insert into t_employees
            app_role = self.data["app_role"]
            del self.data["app_role"]
            self.insert(self.data)

            # Insert into t_users
            self.table = "t_users"
            app_user_data = {
                "id": self.data['id'],
                "email": self.data['email'],
                "app_role": app_role
            }
            self.insert(app_user_data)

            # Insert into t_emp_time_off
            self.table = "t_emp_time_off"
            time_off_user_data = {
                "id": self.data['id'],
                "hire_id": self.data['hire_date']
            }
            self.insert(time_off_user_data)

            # Insert into t_emp_avatar
            self.table = "t_emp_avatar"
            user_avatar = {
                "id": self.data['id'],
                "location": "static",
                "file_name": "images/avatar/avatar.png"
            }
            self.insert(user_avatar)
            self.table = "t_employees"
            send_email.send_user_email(self.data['id'])

        def tasks(self):
            tasks = self.data['tasks']
            del self.data['tasks']
            self.insert(self.data)

            for task in tasks:
                if task == "":
                    pass
                else:
                    task_data = {
                        'name': task,
                        'task_list_id': self.data['id']
                    }
                    self.db.Insert(req_type="tasks", data=task_data)

        def update_id(self):
            next_number_id = self.db.Select("cv_table_id").where(next_id=self.id)[0][2]
            CURSOR.execute(f'''UPDATE ct_table_id SET last_number_id = {next_number_id}
                                                        WHERE table_name = '{self.table}'; ''')
            CONNECTION.commit()
            print("ID updated!")

    class Update:

        def __init__(self, req_type, data):
            self.db = Database()
            self.table = self.db.Select("ct_type_table").where(type=req_type)[0][1]

            if req_type == 'timesheet' or req_type == 'tickets':
                self.requests(data)

            elif req_type == 'timeOff':
                # If the request is rejected, the number of days taken will be reallocated to user.
                if data[1] == 3 or data[1] == "3":
                    req_info = self.db.Select('t_req_time_off', row="number_of_days, type_id, user_id").where(id=data[0])[0]
                    number_of_days = req_info[0]
                    type_id = req_info[1]
                    user_id = req_info[2]
                    current_number = self.db.Select("t_emp_time_off", row=type_id).where(id=user_id)[0][0]
                    final_number = current_number + int(number_of_days)
                    update = {
                        "id": user_id,
                        type_id: final_number
                    }
                    self.db.Update(req_type="empTimeOff", data=update)
                self.requests(data)

            elif req_type == 'employee':
                if "app_role" in data:
                    app_data = {
                        'id': data['id'],
                        'app_role': data['app_role']
                    }
                    self.db.Update(req_type='users', data=app_data)
                    del data["app_role"]
                self.update(data)

            elif req_type == 'department':
                li = []
                # Delete task list assigned to this department.
                for tasks in self.db.Select("t_dep_tasklist_link").where(department_id=data['id']):
                    self.db.Delete(req_type="depLinkTasklist", id=tasks[0])

                # Identify the Tasks List assigned and add to t_dep_tasklist_link
                for key in data:
                    if key[:4] == 'TSKL':
                        link_data = {
                            'department_id': data['id'],
                            'task_list_id': key
                        }
                        # print(link_data)
                        self.db.Insert(req_type="depLinkTasklist", data=link_data)
                        li.append(key)

                # Delete TSKL from Departments Data
                for x in li:
                    if x in data:
                        del data[x]
                # print(data)

                # Update table with edited data.
                self.update(data)

            else:
                self.update(data)

        def update(self, data):
            row_id = data['id']
            del data['id']
            #

            data_list = []
            for key, value in data.items():
                data_list.append(f"{key} = '{value}'")
            final_list = ", ".join(data_list)

            CURSOR.execute(f'''UPDATE {self.table} SET {final_list} WHERE id = '{row_id}';''')
            CONNECTION.commit()

        def requests(self, data):
            CURSOR.execute(f'''UPDATE {self.table} SET STATUS = {data[1]} WHERE ID = '{data[0]}';''')
            CONNECTION.commit()

    class Delete:

        def __init__(self, req_type, id):
            self.db = Database()
            self.table = self.db.Select("ct_type_table").where(type=req_type)[0][1]
            self.id = id

            if req_type == "employee":
                self.employee()
            elif req_type == "department":
                self.department()
            elif req_type == "tasksList":
                self.tasks_list()
            elif req_type == "doc":
                self.document()
            else:
                self.delete()

        def delete(self):
            CURSOR.execute(f'''DELETE FROM {self.table} WHERE id = '{self.id}'; ''')
            CONNECTION.commit()

        def employee(self):
            self.delete()
            self.table = "t_users"
            self.delete()
            self.table = "t_emp_time_off"
            self.delete()
            self.table = "t_emp_avatar"
            self.delete()

        def department(self):
            self.delete()
            for role in self.db.Select("t_roles").where(department_id=self.id):
                for emp in self.db.Select("t_employees").where(role=role[0]):
                    self.db.Delete(req_type="employee", id=emp[0])
                self.db.Delete(req_type="roles", id=role[0])

        def tasks_list(self):
            self.delete()
            for tasks in self.db.Select("t_tasks").where(task_list_id=self.id):
                self.db.Delete(req_type="tasks", id=tasks[0])
            for link in self.db.Select("t_dep_tasklist_link").where(task_list_id=self.id):
                self.db.Delete(req_type="depLinkTasklist", id=link[0])

        def document(self):
            db_data = self.db.Select(self.table).where(id=self.id)[0]
            path = db_data[2]
            file_name = db_data[3]
            file_to_delete = os.path.join(path, file_name)
            os.remove(file_to_delete)
            self.delete()

    def checked(self, day, user, task_id):
        date = str(self.Select().current_date())[:8] + str(day)
        if self.Select('t_req_timesheet_tasks').where(date=date, user_id=user, task_id=task_id):
            return True
        else:
            return False

    def log_requests(self, user, request_type, data=None, admin=False):
        current_date = self.Select().current_date()

        db_message = {
            'sender': user,
            'date': current_date,
        }
        if admin:
            if request_type == "timeOff":
                req_info = self.Select('v_req_time_off').where(id=data[0])
                db_message['receiver'] = req_info[0][3]
                admin_name = self.Select("v_employees").where(id=user)[0][3]
                if data[1] == str(2):
                    db_message['message'] = f"{admin_name} approve your Time Off Request."
                else:
                    db_message['message'] = f"{admin_name} rejected your Time Off Request."
            elif request_type == "tickets" and data[1] == str(2):
                req_info = self.Select('v_req_tickets').where(id=data[0])
                # print(req_info)
                db_message['receiver'] = req_info[0][1]
                admin_name = self.Select("v_employees").where(id=user)[0][3]
                db_message['message'] = f"{admin_name} resolved your ticket."
                # print(db_message)
            db_message['date'] = self.Select().current_timestamp()

        else:
            if request_type == 'timesheet':
                x = "Timesheet"
            elif request_type == 'timeOff':
                x = "Time Off"
            else:
                x = "Ticket"
            db_message['message'] = f"Create a new {x} request."
            db_message['receiver'] = "Admins"

        # print(db_message)
        self.Insert("logReq", db_message)


class User(Database):

    def __init__(self, **kwargs):
        super().__init__()
        self.db = Database()
        global key
        for key, value in kwargs.items():
            self.key = value
        CURSOR.execute(f'''SELECT * FROM t_users WHERE {key} = '{self.key}'; ''')
        self.user_auth_data = CURSOR.fetchone()
        self.validation()
        if self.validation():
            self.email = self.user_auth_data[1]
            self.id = self.user_auth_data[0]
            self.password = self.user_auth_data[2]
            self.role = self.user_auth_data[3]
            self.info()

    def validation(self):
        if self.user_auth_data is None:
            return False
        else:
            return True

    def info(self):
        user = self.db.Select("v_employees").where(id=self.id)
        for data in user:
            emp = {
                'id': data[0],
                'first': data[1],
                'last': data[2],
                'complete_name': data[3],
                'email': data[4],
                'phone': data[5],
                'hire': data[7],
                'address': data[6],
                'manager': data[12],
                'role_id': data[8],
                'role': data[9],
                'department_id': data[10],
                'department': data[11],
                'admin': self.role,
                'manager_id': data[12],
                'manager_name': data[13]
            }
            return emp


def select_all(table):
    if table == "users":
        CURSOR.execute(f'''select * from public."USERS";''')
        return CURSOR.fetchall()
    else:
        CURSOR.execute(f'''select * from {table} ORDER BY ID ASC''')
        return CURSOR.fetchall()


def select(f, w, e):
    CURSOR.execute(f'''SELECT * FROM {f} WHERE {w} = '{e}';''')
    return CURSOR.fetchall()


def select_count(table):
    CURSOR.execute(f'''SELECT count(*) FROM {table}''')
    return CURSOR.fetchone()[0]


def query(**kwargs):
    cursour = []
    for key, value in kwargs.items():
        cursour.append(key)
        cursour.append(value)
    string = " ".join(cursour)
    CURSOR.execute(string)
    return CURSOR.fetchall()


def delete(id, table):
    if table == "DEPARTMENTS":
        CURSOR.execute(f'''DELETE FROM ROLES WHERE DEPARTMENT_ID = '{id}';''')
        CONNECTION.commit()
    elif type(id) == str:
        CURSOR.execute(f'''DELETE FROM {table} WHERE ID = '{id}';''')
        CONNECTION.commit()
    else:
        CURSOR.execute(f'''DELETE FROM {table} WHERE ID = {id}''')
        CONNECTION.commit()


def day_check(day, month, year, user_id):
    CURSOR.execute(
        f'''SELECT STATUS FROM REQ_TIMESHEET where DATE = '{day}/{month}/{year}' and USER_ID = {user_id} ''')
    complete_date = CURSOR.fetchone()
    if complete_date is None:
        return ''
    else:
        status = complete_date[0]
        if status == 1:
            return 'background-color: #fff5cc;'
        elif status == 2:
            return 'background-color: #ccffcc;'
        elif status == 3:
            return 'background-color: #ffcccc;'


def timeoff(data):
    data = data
    request_id = int(str(data['user']) + data['start'].replace('-', ''))
    status = 1
    CURSOR.execute(f'''INSERT INTO REQ_TIMEOFF
    VALUES ({request_id}, '{data['type']}', '{data['user']}', '{data['start']}', '{data['end']}', {status}, '{data['note']}')''')
    CONNECTION.commit()


#
# def hr_request(data):
#     CURSOR.execute('''SELECT ID FROM req_hr ORDER BY ID DESC LIMIT 1;''')
#     request_id = CURSOR.fetchone()[0] + 1
#     status = 1
#     CURSOR.execute(f'''INSERT INTO REQ_HR
#     VALUES ({request_id}, '{data['id']}', '{data['title']}', {data['user']}, {status}, '{data['note']}', {data['assigned']})''')
#     CONNECTION.commit()
#
#
# def timesheet(data):
#     id = int(str(data['user']) + data['date'].replace('/', ''))
#     status = 1
#     department_id = select("DEPARTMENTS", "NAME", data['department'])[0]
#     role_id = select("ROLES", "NAME", data['role'])[0]
#     if select("REQ_TIMESHEET", "ID", id):
#         CURSOR.execute(f'''DELETE FROM REQ_TIMESHEET WHERE ID = {id}''')
#         CONNECTION.commit()
#         CURSOR.execute(f'''INSERT INTO REQ_TIMESHEET
#             VALUES ({id}, '{data['date']}', '{data['current_date']}', {status}, '{data['project']}', {data['user']}, '{role_id[0]}', '{department_id[0]}')''')
#         CONNECTION.commit()
#     else:
#         CURSOR.execute(f'''INSERT INTO REQ_TIMESHEET
#         VALUES ({id}, '{data['date']}', '{data['current_date']}', {status}, '{data['project']}', {data['user']}, '{role_id[0]}', '{department_id[0]}')''')
#         CONNECTION.commit()


def check_table(class_name):
    CURSOR.execute(f'''SELECT table_name FROM class_table WHERE class_name = '{class_name}';''')
    table_name = CURSOR.fetchone()[0]
    return table_name


def create_department(data):
    CURSOR.execute(f'''INSERT INTO DEPARTMENTS 
    VALUES ('{data['id']}', '{data['name']}', {data['responsible']})''')
    CONNECTION.commit()


def edit_department(data):
    CURSOR.execute(f'''UPDATE DEPARTMENTS 
                        SET id = '{data['id']}',
                            name = '{data['name']}',
                            responsable = {data['responsible']}
                        WHERE id = '{data['id']}';''')
    CONNECTION.commit()


def create_role(data):
    CURSOR.execute(f'''INSERT INTO ROLES 
    VALUES ('{data['id']}', '{data['role']}', '{data['department']}')''')
    CONNECTION.commit()


def create_project(data):
    CURSOR.execute(f'''INSERT INTO t_projects 
    VALUES ('{data['id']}', '{data['client']}', '{data['project']}', '{data['responsible']}')''')
    CONNECTION.commit()


def edit_project(data):
    CURSOR.execute(f'''UPDATE PROJECTS 
                        SET id = '{data['id']}',
                            client_name = '{data['client']}',
                            project_name = '{data['project']}',
                            responsable = {data['responsible']}
                        WHERE id = '{data['id']}';''')
    CONNECTION.commit()


def add_employee(data):
    CURSOR.execute(f'''INSERT INTO EMPLOYEE
    VALUES ({data['id']}, '{data['first']}', '{data['last']}', '{data['email']}', '{data['phone']}',
     '{data['hire-date']}', '{data['address']}', {data['manager']}, '{data['role']}')''')
    CONNECTION.commit()
    CURSOR.execute(
        f'''INSERT INTO public."USERS" VALUES ({data['id']}, '{data['email']}', null, {data['application-role']})''')
    CONNECTION.commit()


def edit_employee(data):
    CURSOR.execute(f'''UPDATE EMPLOYEE 
                    SET id = {data['id']},
                        first_name = '{data['first']}',
                        last_name = '{data['last']}',
                        email = '{data['email']}',
                        phone = '{data['phone']}', 
                        hire_date = '{data['hire-date']}', 
                        addresses = '{data['address']}',
                        manager_id = '{data['manager']}',
                        role = '{data['role']}'
                    WHERE ID = {data['id']}''')
    CONNECTION.commit()


def check(self, d, m, y, ty, user):
    date = f"{d}/{m}/{y}"
    self.curr.execute(
        f'''select count(*) from req_ops_type where date_for = '{date}' and type_activity = '{ty}' and user_id = {user}; ''')
    data = self.curr.fetchall()[0][0]
    if data:
        return True
    else:
        return False


def annual_leaves_count():
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    annual_leaves_count_list = []
    for month in month_list:
        CURSOR.execute(
            f'''SELECT count(*) FROM REQ_TIMEOFF WHERE START_DATE LIKE '%-{month}-%' AND TIMEOFF_ID = 'ANL' AND STATUS = 2;''')
        data = CURSOR.fetchone()[0]
        annual_leaves_count_list.append(data)
    return annual_leaves_count_list
