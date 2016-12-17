from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user
def RT(tweetid):
    #try:

    connection=dbapi2.connect(current_app.config['dsn'])
    cursor=connection.cursor()
    cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
    temp=cursor.fetchone()
    rtownerid=temp[0]
    cursor.execute("""SELECT USERID,CONTEXT,TITLE FROM TWEETS WHERE TWEETID=%s""",(tweetid,) )
    values=[(temp[0],temp[1],temp[2]) for temp in cursor ]
    for usrid,context,title in values:
        tweetownerid=usrid
        tweetcontext=context
        tweettitle=title
    cursor.execute("""INSERT INTO TWEETS (USERID,CONTEXT,TITLE,isRT,RTOwnerID) VALUES(%s,%s,%s,%s,%s)""",(tweetownerid,tweetcontext,tweettitle,'1',rtownerid))
    cursor.execute("""UPDATE TWEETS SET NUMBEROFRTS=NUMBEROFRTS + 1 WHERE TWEETID=%s""",(tweetid,))
    connection.commit()
    cursor.close()
    connection.close()
    return 1
    #except:
    #    return 0

def UNRT(tweetid):
    try:
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
        temp=cursor.fetchone()
        rtownerid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT CONTEXT,TITLE,USERID FROM TWEETS WHERE TWEETID=%s""",(tweetid,))
        values=[(temp[0],temp[1],temp[2]) for temp in cursor ]
        for usrid,context,title in values:
            tweetownerid=usrid
            tweetcontext=context
            tweettitle=title
        cursor.execute("""DELETE FROM TWEETS WHERE RTOwnerID=%s AND TWEETID=%s""",(rtowner,tweetid))
        cursor.execute("""UPDATE TWEETS SET NUMBEROFRTS=NUMBEROFRTS - 1 WHERE (USERID =%s AND CONTEXT=%s AND TITLE=%s AND isRT=%s AND RTOwnerId=%s""",(tweetownerid,tweetcontext,tweettitle,0,1))
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    except:
        return 0

def isRT(tweetid):
    connection=dbapi2.connect(current_app.config['dsn'])
    cursor=connection.cursor()
    cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
    temp=cursor.fetchone()
    userid=temp[0]
    cursor.close()
    cursor=connection.cursor()
    cursor.execute("""SELECT isRT FROM TWEETS WHERE (USERID=%s AND TWEETID=%s)""",(userid,tweetid))
    temp=cursor.fetchone()
    isRetweet=temp
    connection.commit()
    cursor.close()
    connection.close()
    if isRetweet==1:
        return 1
    else:
        return 0

