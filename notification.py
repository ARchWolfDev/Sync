import json
from database_connection import Database
from mycalendar import Calendar

db = Database()
cal = Calendar()

notification_list = []


def insert(user, request_type):
    global notification_list
    complete_name = db.Select("v_employees").where(id=user)[0][3]
    current_time = cal.date_format("dd-mm-yyyy")

    new_update = {
        f"{user}:{request_type}:{current_time}": {
            "name": complete_name,
            "request": f"Created a new {request_type} request",
            "timestamp": current_time,
        },
    }

    with open("notification_file.json", "r") as data_file:
        data = json.load(data_file)
        data.update(new_update)

    with open("notification_file.json", "w") as data_file:
        data_file.seek(0)
        json.dump(data, data_file, indent=4)
        data_file.close()


def read():
    with open("notification_file.json", "r") as data_file:
        data = json.load(data_file)
        # print(data)
        for _ in data:
            notification_list.insert(0, data[_])
        # print(notification_list)
        # notification_list.sort(key=lambda x: x['timestamp'], reverse=True)
        # format(notification_list)
        if len(notification_list) <= 4:
            return notification_list
        else:
            sliced_list = notification_list[0:4]
            return sliced_list
