from flask import current_app
import psycopg2 as dbapi2

def show_set(username):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        values=cursor.fetchone()
        id=values[0]

        cursor.execute("""select users.username from users inner join notifs on users.id = (select followerid from notifs where userid = %s) where notifs.perm = '1'""", (id,))
        value=cursor.fetchone()
        followername=value[0]

        connection.commit()
        cursor.close()
        connection.close()
        return followername
    except:
        return False