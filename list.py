from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user

class List:
    def __init__(self,name,creatorname):
        self.name=name
        self.creatorname=creatorname
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(creatorname,))
        temp=cursor.fetchone()
        self.creatorid=temp[0]
        cursor.close()
        connection.close()

    def addMember(self,MemberId):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s && CreatorID""",(self.name,self.creatorID))
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.execute("""INSERT INTO LISTMEMBERS (LISTID,USERID) VALUES (%s, %s)""", (listid,MemberID))
        connection.commit()
        cursor.close()
        connection.close()

    def deleteMember(self, memberID):
        del self.members[memberID]

    def updateName(self,newName):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE LISTS SET NAME=%s WHERE NAME=%s AND CreatorID=%s""",(newName,self.name,self.creatorid) )
        self.name=newName
        connection.commit()
        cursor.close()
        connection.close()

    def getPosts(self):
        return sorted(self.posts.items())

    def getMembers(self):
        return sorted(self.members.items())