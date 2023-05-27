# Python default packages
import os

# External packages
import psycopg2

# Project packages
from helpers import pretify

save_data: dict = None

class AllData:

    def __init__(self, mode: str = 'html'):
        self.mode = mode if mode in ['html', 'markdown'] else 'html'
        if self.mode == 'html':
            self.dec_text_start = '<strong>'
            self.dec_text_end = '</strong>'
            self.separator = "<br>"
        else:
            self.dec_text_start = self.dec_text_end = '**'
            self.separator = """

"""
        self.data: dict = self.get_data()
        self.data_str: str = self.data_to_str()

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

    def data_to_str(self) -> str:
        return "ALL DATA:\n{}".format(
            self.separator.join("{}{}{} ::\n{}".format(self.dec_text_start, key, self.dec_text_end,
                                pretify(data, dec_text_start=self.dec_text_start, dec_text_end=self.dec_text_end))
                                for key, data in self.data.items())
        )
