from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from flask_login import current_user

class Twitlist:
    def __init__(self):
        self.twit = {}
        self.list = {}


    def add_link(self, twitid, list):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO TWEETLINK (TWEETID, CONTEXTL)    VALUES    (%s, %s)""", (twitid, list.contextl))
        connection.commit()
        connection.close()

    def delete_link(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM TWEETLINK WHERE TWEETID=%s""", twitid)
        connection.commit()
        connection.close()

    def update_link(self, twitid, list):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE TWEETLINK SET CONTEXTL=%s WHERE TWEETID=%s""", (list.contextl, twitid))
        connection.commit()
        connection.close()

    def add_twit(self, twit):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""INSERT INTO TWEETS (USERID, TITLE, CONTEXT)    VALUES    (%s, %s, %s)""", (userid, twit.title, twit.context))
        connection.commit()
        connection.close()

    def delete_twit(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM TWEETS WHERE TWEETID=%s""", twitid)
        connection.commit()
        connection.close()

    def update_twit(self, twitid, twit):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE TWEETS SET TITLE=%s, CONTEXT=%s WHERE TWEETID=%s""", (twit.title, twit.context, twitid))
        connection.commit()
        connection.close()

    def get_twit(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT TITLE, CONTEXT FROM TWEETS WHERE TWEETID=%s""", [twitid],)
        twit=cursor.fetchone()
        print (twit)
        connection.commit()
        connection.close()
        return twit

    def get_twits(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        print (userid)
        twit=cursor.execute("""SELECT TITLE, CONTEXT, TWEETID FROM TWEETS WHERE USERID=%s""", (userid,))
        print (twit)
        connection.commit()
        connection.close()
        return twit