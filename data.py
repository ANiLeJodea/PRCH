# Python default packages
import os

# External packages
import psycopg2

# Project packages
from helpers import pretify

save_data: dict = None


class AllData:

    def __init__(self, dec_text: str = "*"):
        self.data: dict = self.get_data()
        self.dec_text = dec_text
        self.data_str: str = self.data_to_str(self.dec_text)

    def get_data(self) -> dict:
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

        global save_data
        save_data = all_data

        return all_data

    def data_to_str(self, dec_text: str) -> str:
        return "ALL DATA:\n{}".format(
            self.data['separator'].join("{} ::\n{}".format(pretify(data, dec_text=dec_text),
                                                           pretify(data, dec_text=dec_text))
                                        for key, data in self.data)
        )
