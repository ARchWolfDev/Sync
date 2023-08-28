from werkzeug.security import generate_password_hash
from database_connection import Database

db = Database()

password = generate_password_hash('password123')

db.curr.execute(f'''UPDATE users SET user_password = '{password}' WHERE user_id IN (1, 2, 3, 4, 5)''')
db.connection.commit()

print(password)