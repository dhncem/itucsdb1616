from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from twit import Twit

class Twitlist:
    def __init__(self):
        self.twits = {}
        self.lists = {}
        self.last_key = 0


    def get_hometwit(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""  SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username
                            FROM tweets
                            RIGHT JOIN follows ON follows.followeduser = tweets.userid
                            RIGHT JOIN users ON users.id=tweets.userid
                            WHERE follows.followerid = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username
                            FROM tweets
                            RIGHT JOIN users ON users.id=tweets.userid
                            WHERE tweets.userid = %s ORDER BY TWEETID DESC""", (userid, userid))
        twit = [(Twit(title, context, twitid, userhandle))
                    for title, context, twitid, userhandle  in cursor]
        return twit

    def getid(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        usernum=cursor.fetchone()
        return usernum

    def getownerid(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT USERID FROM TWEETS WHERE TWEETID=%s""", (twitid,))
        owner = cursor.fetchone()
        return owner

    def add_link(self, twitid, list):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO TWEETLINK (TWEETID, CONTEXTL)    VALUES    (%s, %s)""", (twitid, list.contextl))
        connection.commit()
        connection.close()

    def delete_link(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM TWEETLINK WHERE TWEETID=%s""", [twitid],)
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
        cursor.execute("""DELETE FROM TWEETS WHERE TWEETID=%s""", [twitid],)
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
        cursor.execute("""SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username
                            FROM tweets
                            RIGHT JOIN users ON users.id=tweets.userid
                            WHERE tweets.userid = %s""", [twitid],)
        title, context = cursor.fetchone()
        return Twit(title, context, twitid)

    def get_twits(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username
                            FROM tweets
                            RIGHT JOIN users ON users.id=tweets.userid
                            WHERE tweets.userid = %s ORDER BY TWEETID DESC""", (userid,))
        twit = [(Twit(title, context, twitid, userhandle))
                    for title, context, twitid, userhandle  in cursor]
        return twit