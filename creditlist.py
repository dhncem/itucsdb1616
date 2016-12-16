from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from credit import *

class Creditlist:
    def __init__(self):
        self.credits = {}
        self.last_key = 0

    def get_credit(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""SELECT CASH FROM SITECR WHERE USERID=%s""", (userid,))
        cash = cursor.fetchone()
        return GETcredit(cash)

    def upd_credit(self, credit):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""UPDATE SITECR SET CASH=%s WHERE USERID=%s""", (credit, userid))
        connection.commit()
        connection.close()


    def add_credit(self, credit):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""INSERT INTO SITECR (USERID, CASH) VALUES (%s, %s)""", (userid, credit.cash))
        connection.commit()
        connection.close()

    def send_credit(self, credit, usrhandle):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (usrhandle,))
        userid=cursor.fetchone()
        cursor.execute("""SELECT CASH FROM SITECR WHERE USERID=%s""", (userid,))
        cash=cursor.fetchone()
        cash=cash+credit.cash
        cursor.execute("""UPDATE SITECR SET CASH=%s
                            WHERE USERID=%s""", (cash, userid))
        connection.commit()
        connection.close()

