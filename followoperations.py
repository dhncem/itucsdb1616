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

