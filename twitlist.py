from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from twit import Twit
from twit import Link

class Twitlist:
    def __init__(self):
        self.twits = {}
        self.links = {}
        self.last_key = 0

    def delete_linktw(self, id_twit):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM TWEETLINK WHERE tweetid=%s""", [id_twit],)
        connection.commit()
        connection.close()

    def get_hometwit(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""  SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN follows ON follows.followeduser = tweets.userid
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE follows.followerid = %s AND tweets.isrt = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE tweets.userid = %s AND tweets.isrt = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN follows ON follows.followeduser = tweets.userid
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE follows.followerid = %s AND tweets.isrt = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE tweets.userid = %s AND tweets.isrt = %s
                            ORDER BY TWEETID DESC; """, (userid, 0, userid, 0, userid, 1, userid, 1))
                            #title, context, id, userpostedthe tweet, like, trs, isrt, originalowner
        twit = [(Twit(title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner))
                    for title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner  in cursor]
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

    def get_link(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT tweetlid, CONTEXTL, TWEETID  FROM TWEETLINK WHERE TWEETID=%s""", (twitid,))
        link = [(Link(tweetlid, contextl, tweetid))
                    for tweetlid, contextl, tweetid in cursor]
        return link

    def add_link(self, twitid, link):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO TWEETLINK (TWEETID, CONTEXTL)    VALUES    (%s, %s)""", (twitid, link.contextl))
        connection.commit()
        connection.close()

    def delete_link(self, tweetlid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM TWEETLINK WHERE tweetlid=%s""", [tweetlid],)
        connection.commit()
        connection.close()

    def update_link(self, tweetlid, link):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE TWEETLINK SET CONTEXTL=%s WHERE tweetlid=%s""", (link.contextl, tweetlid))
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
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.tweetid = %s""", [twitid],)
        title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner = cursor.fetchone()
        twits=Twit(title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner)
        return twits

    def get_twits(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.userid = %s ORDER BY TWEETID DESC""", (userid,))
        twit = [(Twit(title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner))
                    for title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner  in cursor]
        return twit

    def get_elsetwits(self, usrhandle):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (usrhandle,))
        userid=cursor.fetchone()
        cursor.execute("""SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.userid = %s ORDER BY TWEETID DESC""", (userid,))
        twit = [(Twit(title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner))
                    for title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner  in cursor]
        return twit