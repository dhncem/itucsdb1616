from flask import current_app
import psycopg2 as dbapi2

def change_settings(email,language, nickname,username, name, surname):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        values=cursor.fetchone()
        id=values[0]
        cursor.execute("""UPDATE USERINFO SET NAME=%s, SURNAME=%s, NICKNAME=%s, EMAIL=%s, LANGUAGE=%s WHERE USERID=%s""",
                       (name,surname, nickname, email, language, id))

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except:
        return False

def show_settings(username):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        values=cursor.fetchone()
        id=values[0]
        cursor.execute("""SELECT NAME, SURNAME, NICKNAME, EMAIL,LANGUAGE FROM USERINFO WHERE USERID=%s""", (id,))
        values = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()
        return values
    except:
        return False

def delete_settings(username):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        values=cursor.fetchone()
        id=values[0]
        cursor.execute("""DELETE FROM USERINFO WHERE USERID=%s""", (id,))
        cursor.execute("""INSERT INTO USERINFO (USERID, NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(%s,%s, %s, %s, %s, %s)""",
                           (id,'', '', '', '', ''))

        connection.commit()
        cursor.close()
        connection.close()
        return values
    except:
        return False