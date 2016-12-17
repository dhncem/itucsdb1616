from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user
from like import Like
def like(tweetid):
    try:

        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""INSERT INTO LIKES (USERID,TWEETID) VALUES(%s,%s)""",(userid,tweetid))
        cursor.execute("""UPDATE TWEETS SET NUMBEROFLIKES=NUMBEROFLIKES + 1 WHERE TWEETID=%s""",(tweetid,))
        cursor.execute("""UPDATE USERPROFILE SET LIKES=LIKES + 1 WHERE ID=%s""",(userid,))
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    except:
        return 0

def unlike(tweetid):
    try:
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""DELETE FROM LIKES WHERE USERID=%s AND TWEETID=%s""",(userid,tweetid))
        cursor.execute("""UPDATE TWEETS SET NUMBEROFLIKES=NUMBEROFLIKES - 1 WHERE TWEETID=%s""",(tweetid,))
        cursor.execute("""UPDATE USERPROFILE SET LIKES=LIKES - 1 WHERE ID=%s""",(userid,))
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    except:
        return 0

def getAllLikes():
    connection=dbapi2.connect(current_app.config['dsn'])
    cursor=connection.cursor()
    cursor.execute("""SELECT U1.USERNAME as LIKERNAME, U2.USERNAME as TWITTERNAME, T2.TITLE, T2.CONTEXT, T2.LIKETIME FROM (SELECT L.USERID AS LIKERID,
    T.USERID AS TWITOWNERID,T.TITLE,T.CONTEXT,L.LIKETIME FROM LIKES AS L JOIN TWEETS as T ON L.TWEETID=T.TWEETID)
    AS T2 JOIN USERS AS U1 ON T2.LIKERID=U1.ID JOIN USERS AS U2 ON T2.TWITOWNERID=U2.ID""")
    likes=[(Like(likername,tweetownername,tweettitle,tweetcontext,liketime)) for likername,tweetownername,tweettitle,tweetcontext,liketime in cursor ]
    connection.commit()
    cursor.close()
    connection.close()
    return likes

def isLiked(username,tweetid):
    connection=dbapi2.connect(current_app.config['dsn'])
    cursor=connection.cursor()
    cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
    temp=cursor.fetchone()
    userid=temp[0]
    cursor.execute("""SELECT LikeTIME FROM LIKES WHERE USERID=%s AND TWEETID=%s""",(userid,tweetid))
    temp=cursor.fetchone()
    if temp is None:
        return 0
    else:
        return 1

def getLikedTweets(username):
    connection=dbapi2.connect(current_app.config['dsn'])
    cursor=connection.cursor()
    cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
    temp=cursor.fetchone()
    userid=temp[0]
    cursor.execute("""SELECT TITLE,CONTEXT,USERNAME,LIKETIME,T.TWEETID FROM LIKES  JOIN
    (SELECT TITLE,CONTEXT,USERNAME,TWEETID FROM TWEETS JOIN USERS ON USERS.ID=TWEETS.USERID)
    AS T ON LIKES.TWEETID=T.TWEETID WHERE USERID=%s ORDER BY LIKETIME DESC""",(userid,))
    likedTweets=[(username,tweetownername,tweettitle,tweetcontext,liketime,tweetid) for tweettitle,tweetcontext,tweetownername,liketime,tweetid in cursor]
    return likedTweets