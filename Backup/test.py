import mycalendar as calendar
import database_connection as database
import files
u_email = "andrei.rachieru@arch-dev.com"

user = 1001
db = database
role = "People Manager"

data = db.select_all("TIMEOFF_CLASS")
for _ in data:
    if _[0] not in 'ANL' and _[0] not in 'SKL':
        print(_)