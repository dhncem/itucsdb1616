from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user
from  list import List

class ListOfLists:
    def __init__(self,name):
        self.name=name

    def addList(self,list):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""INSERT INTO LISTS (NAME,CREATORID) VALUES (%s, %s)""", (list.name,userid))
        connection.commit()
        cursor.close()
        connection.close()

    def deleteList(self, listname,creatorname):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(creatorname,))
        temp=cursor.fetchone()
        creatorid=temp[0]
        cursor.execute("""DELETE FROM LISTS WHERE NAME=%s AND CreatorID=%s """,(listname,creatorid))
        connection.commit()
        cursor.close()
        connection.close()

    def getList(self, list):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM LISTS WHERE NAME=%s ANDCreatorID::varchar=%s """,(list.name,list.creatorID))
        temp=cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()

    def updateNameOfAList(self,listname,newName):
        list=List(listname,current_user.username)
        list.updateName(newName)


    def getLists(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT NAME FROM LISTS""")
        lists=[temp[0] for temp in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return lists;