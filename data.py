# Python default packages
import os

# External packages
import psycopg2

save_all_data: dict = None

def get_data() -> dict:
    global save_all_data

    conn = psycopg2.connect(os.environ['DB_LINK'])
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

    save_all_data = all_data
    return all_data

