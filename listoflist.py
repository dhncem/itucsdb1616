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
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""INSERT INTO LISTS (NAME,CREATORID) VALUES (%s, %s)""", (list.name,userid))
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CreatorID =%s """,(list.name,userid))
        temp2=cursor.fetchone()
        listid=temp2[0]
        cursor.execute("""INSERT INTO LISTMEMBERS (LISTID,USERID,USERTYPE) VALUES (%s,%s,%s)""",(listid,userid,'Owner'))
        connection.commit()
        cursor.close()
        connection.close()

    def deleteList(self, listname,creatorname):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(creatorname,))
        temp=cursor.fetchone()
        creatorid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""DELETE FROM LISTS WHERE NAME=%s AND CreatorID=%s """,(listname,creatorid))
        connection.commit()
        cursor.close()
        connection.close()
        return

    def getList(self, listname):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT USERNAME FROM LISTS JOIN USERPROFILE ON LISTS.CREATORID = USERPROFILE.ID WHERE NAME=%s""",(listname,))
        temp=cursor.fetchone()
        username=temp[0]
        list=List(listname,username)
        connection.commit()
        cursor.close()
        connection.close()
        return list

    def updateNameOfAList(self,listname,newName):
        list=List(listname,current_user.username)
        list.updateName(newName)
        return

    def getSubscribeLists(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        tempid=cursor.fetchone()
        userid=tempid[0]
        cursor.execute("""SELECT NAME FROM LISTS JOIN LISTMEMBERS ON LISTS.LISTID=LISTMEMBERS.LISTID WHERE USERTYPE=%s  AND USERID=%s""",('Subscriber',userid))
        lists=[temp[0] for temp in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return lists

    def getInsiderLists(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        tempid=cursor.fetchone()
        userid=tempid[0]
        cursor.execute("""SELECT NAME FROM LISTS JOIN LISTMEMBERS ON LISTS.LISTID=LISTMEMBERS.LISTID WHERE USERTYPE=%s AND USERID=%s""",('Insider',userid))
        lists=[temp[0] for temp in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return lists

    def getCreatedLists(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        tempid=cursor.fetchone()
        userid=tempid[0]
        cursor.execute("""SELECT NAME FROM LISTS JOIN LISTMEMBERS ON LISTS.LISTID=LISTMEMBERS.LISTID WHERE USERTYPE=%s  AND USERID=%s""",('Owner',userid))
        lists=[temp[0] for temp in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return lists