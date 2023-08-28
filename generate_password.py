from werkzeug.security import generate_password_hash
from database_connection import CONNECTION, CURSOR


email = "andrei.rachieru@arch-dev.com"
password = generate_password_hash('password123')
user_id = 'EMP-1001'
app_role = 1


CURSOR.execute(f'''INSERT INTO t_users VALUES ('{user_id}', '{email}', '{password}', {app_role})''')
CONNECTION.commit()

print(password)
