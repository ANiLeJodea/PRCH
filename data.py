# Python default packages
import os

# External packages
import psycopg2

def get_data() -> dict:
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

    return all_data

