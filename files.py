import os
from mycalendar import Calendar

cal = Calendar()


def reform_file(filename, user):
    userfile = str(user) + "--" + str(cal.day) + str(cal.month) + str(cal.year) + "--" + filename
    return userfile

def get_file():
    file_list = []
    path = "static/files/"
    dir_list = os.listdir(path)
    for file in dir_list:
        user_file = file.split("--")
        user_id = user_file[0]
        info = {
            "user": user_id,
            "name": file,
            "size": f'{os.path.getsize(path + file) / 1000} KB'
        }
        file_list.append(info)
    return file_list

