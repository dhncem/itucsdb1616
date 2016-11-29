from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user

def follow(followed):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (current_user.username,))
        values=cursor.fetchone()
        followerid=values[0]
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (followed,))
        values=cursor.fetchone()
        followedid=values[0]
        if followerid and followedid:
            cursor.execute("""INSERT INTO FOLLOWS (FOLLOWERID, FOLLOWEDUSER) VALUES (%s, %s)""",(followerid,followedid))
            cursor.execute("""UPDATE USERPROFILE SET FOLLOWING = FOLLOWING +1 WHERE (ID = %s) """,(followerid,))
            cursor.execute("""UPDATE USERPROFILE SET FOLLOWERS = FOLLOWERS +1 WHERE (ID = %s) """,(followedid,))

            cursor.execute("""INSERT INTO NOTIFS (USERID, FOLLOWERID, PERM) VALUES (%s, %s,%s)""",(followedid,followerid, '1'))
        else:
            connection.commit()
            cursor.close()
            connection.close()
            return False
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except:
        return False

def unfollow(followed):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (current_user.username,))
        values=cursor.fetchone()
        followerid=values[0]
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (followed,))
        values=cursor.fetchone()
        followedid=values[0]
        if followerid and followedid:
            cursor.execute("""DELETE FROM FOLLOWS WHERE (FOLLOWERID = %s) AND (FOLLOWEDUSER = %s)""",(followerid,followedid))
            cursor.execute("""UPDATE USERPROFILE SET FOLLOWING = FOLLOWING -1 WHERE (ID = %s)""",(followerid,))
            cursor.execute("""UPDATE USERPROFILE SET FOLLOWERS = FOLLOWERS -1 WHERE (ID = %s)""",(followedid,))

        else:
            connection.commit()
            cursor.close()
            connection.close()
            return False
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except:
        return False

def get_followercount(username):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT FOLLOWERS FROM USERPROFILE WHERE USERNAME = %s""", (username,))
        values=cursor.fetchone()
        followercount=values[0]
        connection.commit()
        cursor.close()
        connection.close()
        return followercount
    except:
        return False

def get_followingcount(username):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT FOLLOWING FROM USERPROFILE WHERE USERNAME = %s""", (username,))
        values=cursor.fetchone()
        followingcount=values[0]
        connection.commit()
        cursor.close()
        connection.close()
        return followingcount
    except:
        return False