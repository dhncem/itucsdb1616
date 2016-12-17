import psycopg2 as dbapi2
from flask import current_app
from quiz import Quiz
from flask_login import current_user

class QuizList:
    def __init__(self):
        self.tag = {}
        self.last_key = 0

    def add_quiz(self, reciever, options, content, choice):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        senderid = cursor.fetchone()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (reciever,))
        recieverid = cursor.fetchone()
        cursor.execute("""INSERT INTO QUIZ (SENDERID, RECIEVERID, CONTENT) VALUES (%s, %s, %s)""", (senderid, recieverid, content))
        connection.commit()
        cursor.execute("""SELECT ID FROM QUIZ WHERE CONTENT=%s""", (content,))
        quizid = cursor.fetchone()
        for i in range(len(options)):
            if i == int(choice)-1:
                cursor.execute("""INSERT INTO OPTIONS (QUESTIONID, CHOICE, CORRECTNESS) VALUES (%s, %s, TRUE)""",(quizid, options[i]))
                connection.commit()
            else:
                cursor.execute("""INSERT INTO OPTIONS (QUESTIONID, CHOICE, CORRECTNESS) VALUES (%s, %s, FALSE)""",(quizid, options[i]))
                connection.commit()

    def add_points(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("""INSERT INTO POINTS (USERID, POINT) VALUES (%s, 5)""",(userid,))
        connection.commit()

    def get_points(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("""SELECT POINT FROM POINTS WHERE USERID=%s""", (userid,))
        points = cursor.fetchone()
        print(points)
        return points

    def update_points(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("UPDATE POINTS SET POINT =POINT+5 WHERE USERID=%s""",(userid,))
        connection.commit()

    def update_quiz(self, questionid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("UPDATE QUIZ SET ISANSWERED = TRUE WHERE ID = %s""",(questionid,))
        connection.commit()

    def check_correctness(self, optionid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT CORRECTNESS FROM OPTIONS WHERE OPTIONID=%s""", (optionid,))
        correctness = cursor.fetchone()
        return correctness

    def delete_quiz(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("DELETE FROM QUIZ")
        connection.commit()

    def get_quiz(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        recieverid = cursor.fetchone()
        cursor.execute("""SELECT T1.ID, T1.CONTENT, T1.ISANSWERED, T2.OPTIONID, T2.CHOICE, T2.CORRECTNESS FROM QUIZ AS T1 INNER JOIN OPTIONS AS T2 ON T1.ID = T2.QUESTIONID WHERE RECIEVERID = %s""", (recieverid,))
        connection.commit()
        questions = []
        for id, content, isanswered, optionid, choice, correctness in cursor:
            questions +=[(id, content, isanswered, optionid, choice, correctness)]
        print(questions)
        return questions

