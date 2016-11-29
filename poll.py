from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user

class Poll():
    def __init__(self,question,creatorname):
        self.votenumber=0
        self.question=question
        self.creatorname=creatorname
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(creatorname,))
        temp=cursor.fetchone()
        self.creatorid=temp
        cursor.close()
        connection.close()
        return
    def addChoice(self,choicecontent):
        try:
            connection=dbapi2.connect(current_app.config['dsn'])
            cursor=connection.cursor()
            cursor.execute("""SELECT POLLID FROM POLLS WHERE CREATORID=%s AND POLLQUESTION =%s """,(self.creatorid,self.question))
            temp=cursor.fetchone()
            pollid=temp[0]
            cursor.execute("""INSERT INTO CHOICES (POLLID,CONTENT) VALUES (%s,%s)""",(pollid,choicecontent))
            cursor.execute("""UPDATE POLLS SET CHOICENUMBER=CHOICENUMBER + 1 WHERE POLLID=%s""",(pollid,))
            connection.commit()
            cursor.close()
            connection.close()
            return
        except:
            print("Database Problems")
            return
    def deleteChoice(self,choicecontent):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT POLLID FROM POLLS WHERE CREATORID=%s AND POLLQUESTION =%s """,(self.creatorid,self.question))
        temp=cursor.fetchone()
        pollid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""DELETE FROM CHOICES WHERE POLLID=%s AND CONTENT =%s""",(pollid,choicecontent))
        cursor.execute("""UPDATE POLLS SET CHOICENUMBER=CHOICENUMBER -1 WHERE POLLID=%s"""(pollid,))
        connection.commit()
        cursor.close()
        connection.close()
        return
    def getVotes(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT POLLID FROM POLLS WHERE CREATORID=%s AND POLLQUESTION =%s """,(self.creatorid,self.question))
        temp=cursor.fetchone()
        pollid=temp[0]
        cursor.execute("""SELECT U.USERNAME,T.CONTENT FROM (SELECT USERID,CHOICES.CHOICEID,
        CONTENT,CHOICES.POLLID FROM VOTES JOIN CHOICES
        ON VOTES.CHOICEID=CHOICES.CHOICEID)
        AS T JOIN USERS AS U ON U.ID =T.USERID""")
        votes=[ (vote[0],vote[1]) for vote in cursor.fetchall() ]
        return votes
    def updateQuestion(self,newquestion):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""UPDATE POLLS SET POLLQUESTION = %s WHERE POLLQUESTION =%s AND CREATORID=%s """,(newquestion,self.question,self.creatorid))
        self.question=newquestion
        connection.commit()
        cursor.close()
        connection.close()
        return

    def getChoices(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT POLLID FROM POLLS WHERE CREATORID=%s AND POLLQUESTION =%s """,(self.creatorid,self.question))
        temp=cursor.fetchone()
        pollid=temp
        cursor.execute("""SELECT CONTENT FROM CHOICES WHERE POLLID=%s""",(pollid,))
        choices=[temp[0] for temp in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return choices


