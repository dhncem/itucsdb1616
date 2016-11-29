from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user

class List:
    def __init__(self,name,creatorname):
        self.name=name
        self.creatorname=creatorname
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(creatorname,))
        temp=cursor.fetchone()
        self.creatorid=temp[0]
        cursor.close()
        connection.close()

    def addSubscriber(self,membername):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CreatorID=%s""",(self.name,self.creatorid))
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(membername,))
        temp=cursor.fetchone()
        memberid=temp[0]
        cursor.execute("""INSERT INTO LISTMEMBERS (LISTID,USERID,USERTYPE) VALUES (%s, %s,%s)""", (listid,memberid,'Subscriber'))
        cursor.execute("""UPDATE LISTS SET MEMBERS=MEMBERS+1 WHERE LISTID =%s""",(listid,))
        connection.commit()
        cursor.close()
        connection.close()
        return

    def addInsider(self,membername):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CreatorID=%s""",(self.name,self.creatorid))
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(membername,))
        temp1=cursor.fetchone()
        memberid=temp1[0]
        cursor.execute("""INSERT INTO LISTMEMBERS (LISTID,USERID,USERTYPE) VALUES (%s, %s,%s)""", (listid,memberid,'Insider'))
        cursor.execute("""UPDATE LISTS SET MEMBERS=MEMBERS+1 WHERE LISTID =%s""",(listid,))
        connection.commit()
        cursor.close()
        connection.close()
        return

    def deleteSubscriber(self, membername):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(membername,))
        tempmemberid=cursor.fetchone()
        memberid=tempmemberid[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CREATORID=%s""",(self.name,self.creatorid))
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.execute("""DELETE FROM LISTMEMBERS  WHERE LISTID = %s AND USERID =%s AND USERTYPE = %s""",(listid,memberid,'Subscriber'))
        cursor.execute("""UPDATE LISTS SET MEMBERS=MEMBERS-1 WHERE LISTID =%s""",(listid,))
        connection.commit()
        cursor.close()
        connection.close()
        return
    def deleteInsider(self,membername):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(membername,))
        tempmemberid=cursor.fetchone()
        memberid=tempmemberid[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CREATORID=%s""",(self.name,self.creatorid))
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.execute("""DELETE FROM LISTMEMBERS  WHERE LISTID = %s AND USERID =%s AND USERTYPE""",(listid,memberid,'Insider'))
        cursor.execute("""UPDATE LISTS SET MEMBERS=MEMBERS-1 WHERE LISTID =%s""",(listid,))
        connection.commit()
        cursor.close()
        connection.close()
        return
    def updateName(self,newName):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE LISTS SET NAME=%s WHERE NAME=%s AND CREATORID=%s""",(newName,self.name,self.creatorid) )
        self.name=newName
        connection.commit()
        cursor.close()
        connection.close()

    def getPosts(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.close()
        connection.close()
        #eksik

    def getSubscribers(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME = %s AND CREATORID=%s""",(self.name,self.creatorid) )
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.execute("""SELECT USERNAME FROM LISTMEMBERS JOIN USERPROFILE ON LISTMEMBERS.ID = USERPROFILE.ID WHERE LISTID=%s AND USERTYPE=%s""",(listid,'Subscriber'))
        subscriberarray=[member[0] for member in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return subscriberarray

    def isSubscriber(self,membername):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(membername,))
        tempmemberid=cursor.fetchone()
        memberid=tempmemberid[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CreatorID=%s""",(self.name,self.creatorid))
        temp=cursor.fetchone()
        if temp is None:
            print("bigif")
            return 0
        else:
            listid=temp[0]
            cursor.execute("""SELECT USERID FROM LISTMEMBERS WHERE USERID=%s AND LISTID=%s AND USERTYPE=%s """,(memberid,listid,'Subscriber'))
            temp2=cursor.fetchone()
            if temp2 is None:

                return 0
            else:
                return 1