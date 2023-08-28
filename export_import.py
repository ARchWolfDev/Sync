from database_connection import Database
import pandas as pd

db = Database()
PATH = 'static/csv/'


def create_csv(req_type, req_type_index=2):
    index = int(req_type_index)
    table = db.Select("ct_type_table").where(type=req_type)[0][index]
    data = db.Select(table).all()
    des = db.Select().description
    current_date = db.Select().current_date()
    name = f"{req_type}_{current_date}.csv"

    data_dict = {}
    for x in des:
        header = x[0]
        data_list = []
        for dt in data:
            data_list.append(dt[header])
        data_dict[header] = data_list

    print(data_dict)

    df = pd.DataFrame(data_dict)
    df.to_csv(f"{PATH}{name}", index=False)

    return f"{PATH}{name}"


def import_csv(req_type, file_name):
    csv = f"{PATH}{file_name}"
    with open(csv) as file:
        header = file.readline()
        header_format = header.replace("\n", "")
        splited_head = header_format.split(",")
        data = file.readlines()
        for x in data:
            x1 = x.replace("\n", "")
            splited = x1.split(",")
            data_dict = {}
            index = 0
            for head in splited_head:
                data_dict[head] = splited[index]
                index += 1
            db.Insert(req_type, data_dict)
