import psycopg2

CONNECTION = psycopg2.connect(database="syncdb", user="sync001", password="Fuckth3systemE@",
                              host="localhost", port="5432")
CURSOR = CONNECTION.cursor()


class User:

    def __init__(self, email):
        self.email = email
        CURSOR.execute(f'''SELECT * FROM public."USERS" WHERE "EMAIL" = '{self.email}'; ''')
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
        CURSOR.execute(f'''SELECT * FROM EMPLOYEE WHERE ID = {self.id} ''')
        data = CURSOR.fetchone()
        CURSOR.execute(f'''SELECT NAME FROM ROLES WHERE ID = '{data[8]}' ''')
        role = CURSOR.fetchone()[0]
        CURSOR.execute(
            f'''SELECT NAME FROM DEPARTMENTS WHERE ID = (SELECT DEPARTMENT_ID FROM ROLES WHERE ID = '{data[8]}')''')
        department = CURSOR.fetchone()[0]
        emp = {
            'id': data[0],
            'first': data[1],
            'last': data[2],
            'email': data[3],
            'phone': data[4],
            'hire': data[5],
            'address': data[6],
            'manager': data[7],
            'role': role,
            'department': department,
            'admin': self.role,
            'working_hours': data[9]
        }
        return emp


def select_all(table):
    CURSOR.execute(f'''select * from {table} ORDER BY id ASC''')
    return CURSOR.fetchall()


def select(f, w, e):
    CURSOR.execute(f'''SELECT * FROM {f} WHERE {w} = '{e}';''')
    return CURSOR.fetchall()


def query(**kwargs):
    cursour = []
    for key, value in kwargs.items():
        cursour.append(key)
        cursour.append(value)
    string = " ".join(cursour)
    CURSOR.execute(string)
    return CURSOR.fetchone()


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


def check_date_if_exist(day, month, year, user_id):
    CURSOR.execute(
        f'''SELECT count(DATE) FROM REQ_TIMESHEET where DATE = '{day}/{month}/{year}' and USER_ID = {user_id} ''')
    complete_date = CURSOR.fetchall()[0][0]
    if complete_date == 1:
        return 'background-color: #ccffcc;'
    else:
        return ''


def timeoff(data):
    data = data
    request_id = int(str(data['user']) + data['start'].replace('-', ''))
    status = 1
    CURSOR.execute(f'''INSERT INTO REQ_TIMEOFF
    VALUES ({request_id}, '{data['type']}', '{data['user']}', '{data['start']}', '{data['end']}', {status}, '{data['note']}')''')
    CONNECTION.commit()


def hr_request(data):
    data = data
    count = 1000
    request_id = str(data['user']) + str(count)
    status = 1
    CURSOR.execute(f'''INSERT INTO REQ_HR
    VALUES ({request_id}, '{data['id']}', '{data['title']}', {data['user']}, {status}, '{data['note']}')''')
    CONNECTION.commit()
    count += 1


def timesheet(data):
    id = int(str(data['user']) + data['date'].replace('/', ''))
    status = 1
    department_id = select("DEPARTMENTS", "NAME", data['department'])[0]
    role_id = select("ROLES", "NAME", data['role'])[0]
    if select("REQ_TIMESHEET", "ID", id):
        CURSOR.execute(f'''DELETE FROM REQ_TIMESHEET WHERE ID = {id}''')
        CONNECTION.commit()
        CURSOR.execute(f'''INSERT INTO REQ_TIMESHEET
            VALUES ({id}, '{data['date']}', '{data['current_date']}', {status}, '{data['project']}', {data['user']}, '{role_id[0]}', '{department_id[0]}')''')
        CONNECTION.commit()
    else:
        CURSOR.execute(f'''INSERT INTO REQ_TIMESHEET
        VALUES ({id}, '{data['date']}', '{data['current_date']}', {status}, '{data['project']}', {data['user']}, '{role_id[0]}', '{department_id[0]}')''')
        CONNECTION.commit()


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
    CURSOR.execute(f'''INSERT INTO PROJECTS 
    VALUES ('{data['id']}', '{data['client']}', '{data['project']}', {data['responsible']})''')
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
    CURSOR.execute(f'''INSERT INTO public."USERS" VALUES ({data['id']}, '{data['email']}', '{data['password']}', 1)''')
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
