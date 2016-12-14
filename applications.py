from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user
from user import get_userid

def getapplications():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (current_user.username,))
                values=cursor.fetchone()
                userid=values[0]
                cursor.execute("""SELECT APPNAME FROM APPUSERS INNER JOIN APPS ON APPS.ID = APPUSERS.APPID AND USERID=(%s)""", (userid,))
                values=cursor.fetchall()
                return values

def updateapps(activeapps):
    with dbapi2.connect(current_app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (current_user.username,))
            values=cursor.fetchone()
            userid=values[0]
            cursor.execute("""DELETE FROM APPUSERS WHERE USERID=%s""",(get_userid(current_user.username),))
            appids=[]
            for value in activeapps:
                print(value)
                cursor.execute("""SELECT ID FROM APPS WHERE APPNAME=%s""", (value,))
                appid=cursor.fetchone()
                appids+=[appid]
            print(appids)
            for (appid,) in appids:
                cursor=connection.cursor()
                cursor.execute("""INSERT INTO APPUSERS (USERID, APPID) VALUES (%s, %s)""", (userid,appid))
                print(appid,userid)