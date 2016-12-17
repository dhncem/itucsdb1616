import psycopg2 as dbapi2
from flask import current_app
from tag import Tag
from flask_login import current_user

class TagList:
    def __init__(self):
        self.tag = {}
        self.last_key = 0

    def add_tag(self, username, photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        tageduserid = cursor.fetchone()
        cursor.execute("""INSERT INTO TAGS (TAGEDPHOTOID, TAGEDUSERID) VALUES (%s, %s)""", (photoid, tageduserid))
        connection.commit()

    def update_tag(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()

    def delete_tag(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()

    def get_tags(photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("SELECT T1.PHOTOID, USERS.USERNAME FROM MEDIA AS T1 INNER JOIN TAGS AS T2 ON PHOTOID = TAGEDPHOTOID INNER JOIN USERS ON T2.TAGEDUSERID = USERS.ID WHERE PHOTOID=%s""",(photoid,))
        tags = []
        for photoid, username in cursor:
            tags += [(photoid,username)]
        print(tags)
        return tags