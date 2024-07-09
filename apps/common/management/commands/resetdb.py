import sys

import pyodbc
from django.core.management.base import BaseCommand

from config.settings.base import env


class Command(BaseCommand):
    help = "Resets the database."

    def handle(self, *args, **kwargs):
        conn, cursor = self.get_cursor_and_conn()
        self.recreate_db(cursor=cursor, conn=conn)

    def recreate_db(self, cursor, conn):
        """Resets the database."""

        self.stdout.write("Resetting database.")

        cursor.execute(f"DROP DATABASE {env.str('DATABASE_DB')};")
        conn.commit()
        cursor.execute(f"CREATE DATABASE {env.str('DATABASE_DB')};")
        conn.commit()

        self.stdout.write("Reset successful.")

    def get_cursor_and_conn(self):
        """Return the connection and the cursor after connecting."""

        try:
            conn = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={env.str('DATABASE_HOST')};"
                f"UID={env.str('DATABASE_USER')};"
                f"PWD={env.str('DATABASE_PASSWORD')}"
            )
            conn.autocommit = True
            self.stdout.write("Connected to database.")
            return conn, conn.cursor()
        except Exception as e:
            self.stdout.write(e)
            self.stdout.write("Unable to connect to database.")
            sys.exit(-1)
