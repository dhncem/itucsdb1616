from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user
from twit import Twit
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
        try:
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
            return 1
        except:
            return 0
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

    def getTweets(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT LISTID FROM LISTS WHERE NAME=%s AND CreatorID=%s""",(self.name,self.creatorid))
        temp=cursor.fetchone()
        listid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT TWEETID,R.USERID,CONTEXT,TITLE,NUMBEROFLIKES,NUMBEROFRTS,isRT,RTOWNERID,
        TWEETOWNERNAME,RTOWNERNAME FROM (SELECT USERNAME,USERID FROM USERS JOIN LISTMEMBERS ON USERS.ID=LISTMEMBERS.USERID
        WHERE ((USERTYPE='Insider' OR USERTYPE='Owner') AND LISTID=%s )) AS R JOIN
        (SELECT TWEETID,USERID,CONTEXT,TITLE,NUMBEROFLIKES,NUMBEROFRTS,isRT,RTOwnerID,U1.USERNAME AS TWEETOWNERNAME,
        U2.USERNAME AS RTOWNERNAME FROM TWEETS
        JOIN USERS AS U1 ON U1.ID=TWEETS.USERID JOIN USERS AS U2 ON U2.ID=TWEETS.RTOWNERID ) AS Y
        ON R.USERID=Y.USERID

        UNION

        SELECT TWEETID,E.USERID,CONTEXT,TITLE,NUMBEROFLIKES,NUMBEROFRTS,isRT,RTOWNERID,
        TWEETOWNERNAME,RTOWNERNAME
        FROM
        (SELECT USERNAME,USERID FROM USERS JOIN LISTMEMBERS ON USERS.ID=LISTMEMBERS.USERID
        WHERE ((USERTYPE='Insider' OR USERTYPE='Owner') AND LISTID=%s )) AS E
        JOIN
        (SELECT TWEETID,USERID,CONTEXT,TITLE,NUMBEROFLIKES,NUMBEROFRTS,isRT,RTOwnerID,U3.USERNAME AS TWEETOWNERNAME,U4.USERNAME AS RTOWNERNAME FROM TWEETS
        JOIN USERS AS U3 ON U3.ID=TWEETS.USERID JOIN USERS AS U4 ON U4.ID=TWEETS.RTOWNERID ) AS Z

        ON E.USERID=Z.RTOwnerID

        ORDER BY TWEETID DESC""",(listid,listid))
        twit = [(Twit(title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner))
                    for twitid,userid,context,title, numberoflikes,numberofrts,isrt, rtownerid,userhandle,rtowner  in cursor]
        cursor.close()
        connection.close()
        return twit


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