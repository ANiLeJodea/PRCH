# Python default packages
import os

# External packages
import psycopg2

save_all: tuple[dict, str] = None

def get_all_data() -> tuple[dict, str]:
    global save_all

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute("""SELECT * FROM main_data""")
    all_data = {}
    for key, value, type_v in cur.fetchall():
        if type_v == 'int':
            all_data[key] = int(value)
        elif type_v == 'list':
            all_data[key] = value.split('~')
        else:
            all_data[key] = value
    cur.execute("""SELECT value FROM admin_id""")
    all_data['admins'] = [d[0] for d in cur.fetchall()]

    save_all = (
        all_data,
        "ALL DATA:\n{}".format(all_data['separator'].join("{} ::\n{}".format(key, data) for key, data in all_data))
    )
    return save_all


