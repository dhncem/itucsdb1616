import psycopg2 as dbapi2
from flask import current_app
from message import Message

class MessageList:
    def __init__(self):
        self.messages = {}
        self.last_key = 0

    def add_message(self, message):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        senderid = cursor.fetchone()
        cursor.execute("""INSERT INTO MESSAGES (SENDERID, RECIEVERID, CONTENT) VALUES (%s, %s, %s)""", (senderid, 1, message.content))
        connection.commit()

    def delete_message(self, key):
        del self.messages[key]

    def get_message(self, key):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        query = "SELECT MESSAGES.SENDERID, MESSAGES.RECIEVERID, MESSAGES.CONTENT, USERPROFILE.NICKNAME FROM MESSAGES INNER JOIN USERPROFILE ON MESSAGES.SENDERID = USERPROFILE.ID WHERE (MESSAGEID = MESSAGEID)"
        cursor.execute(query, (key,))
        senderid, recieverid, content, nickname = cursor.fetchone()
        return Message(nickname, recieverid, content)

    def get_messages(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        query = "SELECT MESSAGES.MESSAGEID, MESSAGES.SENDERID, MESSAGES.RECIEVERID, MESSAGES.CONTENT, USERPROFILE.NICKNAME FROM MESSAGES INNER JOIN USERPROFILE ON MESSAGES.SENDERID = USERPROFILE.ID"
        cursor.execute(query)
        messages = [(key, Message(nickname, reciever, content))
                    for key, sender, reciever, content, nickname in cursor]
        return messages