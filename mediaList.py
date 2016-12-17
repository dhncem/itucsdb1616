import psycopg2 as dbapi2
from flask import current_app
from media import Media
from flask_login import current_user

class MediaList:
    def __init__(self):
        self.media = {}
        self.last_key = 0

    def add_photo(self, media):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        ownerid = cursor.fetchone()
        cursor.execute("""INSERT INTO MEDIA (OWNERID, DESCRIPTION, URL) VALUES (%s, %s, %s)""", (ownerid, media.description, media.url))
        connection.commit()

    def update_photo(self, description,photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("UPDATE MEDIA SET DESCRIPTION = %s WHERE PHOTOID = %s""",(description,photoid))
        connection.commit()

    def delete_photo(self, photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("DELETE FROM MEDIA WHERE PHOTOID = %s""", (photoid,))
        connection.commit()

    def get_photos(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT * FROM ((SELECT DISTINCT PHOTOID FROM MEDIA WHERE OWNERID = %s) UNION (SELECT DISTINCT TAGEDPHOTOID FROM TAGS WHERE TAGEDUSERID = %s)) AS PHOTOS""",(userid,userid))
        photosid=cursor.fetchall()
        media = []
        for id in photosid:
            cursor.execute("SELECT T1.*, T2.ID FROM MEDIA AS T1 INNER JOIN USERS AS T2 ON T1.OWNERID = T2.ID WHERE T1.PHOTOID = %s""",(id,))
            media += [(key, Media(ownerid, description, url))
                    for key, ownerid, description, url, id in cursor]
        print (media)
        return media