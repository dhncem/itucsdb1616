import psycopg2 as dbapi2
from flask import current_app
from message import Message
from flask_login import current_user

class MessageList:
    def __init__(self):
        self.messages = {}
        self.last_key = 0

    def add_message(self, message):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (message.reciever,))
        recieverid = cursor.fetchone()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        senderid = cursor.fetchone()
        cursor.execute("""INSERT INTO MESSAGES (SENDERID, RECIEVERID, CONTENT, SENT) VALUES (%s, %s, %s, %s)""", (senderid, recieverid, message.content, message.sent))
        connection.commit()

    def delete_message(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("DELETE FROM MESSAGES WHERE SENDERID = %s""", (userid,))
        connection.commit()

    def get_message(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        query = "SELECT MESSAGES.SENDERID, MESSAGES.RECIEVERID, MESSAGES.CONTENT, USERPROFILE.NICKNAME FROM MESSAGES INNER JOIN USERPROFILE ON MESSAGES.SENDERID = USERPROFILE.ID"
        cursor.execute(query)
        senderid, recieverid, content, nickname = cursor.fetchone()
        return Message(nickname, recieverid, content)

    def get_messages(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("SELECT T1.MESSAGEID, T1.SENDERID, T1.RECIEVERID, T1.CONTENT, T2.NICKNAME AS SENDERNICK, T3.NICKNAME AS RECIEVERNICK FROM MESSAGES AS T1 INNER JOIN USERPROFILE AS T2 ON T1.SENDERID = T2.ID INNER JOIN USERPROFILE AS T3 ON T1.RECIEVERID = T3.ID WHERE SENDERID = %s OR RECIEVERID = %s""",(userid,userid))
        messages = [(key, Message(sendernick, recievernick, content))
                    for key, sender, reciever, content, sendernick, recievernick in cursor]
        return messages