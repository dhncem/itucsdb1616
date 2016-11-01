from flask import current_app
from flask_login import UserMixin
import psycopg2 as dbapi2


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(username):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT PASSWORD FROM USERS WHERE USERNAME = %s""", (username,))
        values=cursor.fetchone()
        password=values[0]
        connection.commit()
        cursor.close()
        connection.close()
        user = User(username, password) if password else None
        return user
    except:
        pass