Parts Implemented by Serkan Bekir
=================================

In this project Messages, Media and Quiz operations are done by me.

Six tables are created for handling these three entities such as *MESSAGES*, *MEDIA*, *TAGS*,
*QUIZ*, *OPTIONS* and *POINTS*.

**Messages Entity:**

Firstly *MESSAGE* table is created for this operation.

.. code-block:: SQL

   CREATE TABLE MESSAGES(
      MESSAGEID SERIAL PRIMARY KEY,
      SENDERID INTEGER REFERENCES USERPROFILE (ID) ON DELETE SET NULL,
      RECIEVERID INTEGER REFERENCES USERPROFILE (ID) ON DELETE SET NULL,
      CONTENT VARCHAR(100) NOT NULL,
      SENT BOOLEAN DEFAULT FALSE,
      MTIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

There are 6 columns in this table. *Messageid* holds the ID of the message, *senderid* and *recieverid*
hold the sender and receiver of the message. These columns are refereced by ID of the *USERPROFILE*
table. Content and mtime hold the content and time of the message.


Message.py:

.. code-block:: python

   class Message:
    def __init__(self, sender, reciever, content, sent = None):
        self.sender = sender
        self.reciever = reciever
        self.content = content
        self.sent = sent

In this python file the Message class has created for using in the operations such as add and delete.

After that firstly **add_message** feature is added. For doing this at the beginning *add_message**
function is added and it is shown below.

.. code-block:: python

   def add_message(self, message):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (message.reciever,))
        recieverid = cursor.fetchone()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        senderid = cursor.fetchone()
        cursor.execute("""INSERT INTO MESSAGES (SENDERID, RECIEVERID, CONTENT, SENT) VALUES (%s, %s, %s, %s)""", (senderid, recieverid, message.content, message.sent))
        connection.commit()

This function takes message object for parameter. Firstly, we have the username of the reciever in *message.reciever*
With the first query we got the ID of the reciever user. Secondly, it had done the same thing for getting the ID of the sender person.
After all, senderid, recieverid, content, and sent values are inserted into the *MESSAGE* table.

In server.py file, there is a *new_message_page()* method. In this function, *content* variable has the content of the message, it takes
that from the html file. *reciever* is taken from the dropdown menu which named reciever in html file. As it is seen below of the function
that query retrieves all users username and send it to the html for adding into the dropdown menu. sender is given 1 for preventing
the object error because it is retrieved in **add_message** function which is explained above. After that all these values are put
in the message object and sent to **add_message** for inserting the *MESSAGE* table.

.. code-block:: python

   def new_message_page():
    current_user.activetab = 3
    users = None
    if request.method == 'POST':
        content = request.form['content']
        sender = 1
        reciever = request.form['reciever']
        sent = True
        messagesend = Message(sender, reciever, content, sent)
        current_app.messageList.add_message(messagesend)
        return redirect(url_for('messages_page'))
    with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT USERNAME FROM USERS""")
                users = cursor.fetchall()
    return render_template('new_message.html', users = users)


The function below (**get_message**) is used for getting the message that belongs to current user. First, current user's ID is retrieved
in the first query. After that the messages which the current user is sender or reciever, are retrieved and returned as messages object.

.. code-block:: python

   def get_messages(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("SELECT T1.MESSAGEID, T1.SENDERID, T1.RECIEVERID, T1.CONTENT, T2.NICKNAME AS SENDERNICK, T3.NICKNAME AS RECIEVERNICK FROM MESSAGES AS T1 INNER JOIN USERPROFILE AS T2 ON T1.SENDERID = T2.ID INNER JOIN USERPROFILE AS T3 ON T1.RECIEVERID = T3.ID WHERE SENDERID = %s OR RECIEVERID = %s""",(userid,userid))
        messages = [(key, Message(sendernick, recievernick, content))
                    for key, sender, reciever, content, sendernick, recievernick in cursor]
        return messages


The messages are taken here and sent to the html for printing. Also delete operation is handled here. *Value* consist of the messageid
retrieved from the checkbox button from html. After that it is sent to **delete_message()** in a loop because considering the possibility
of more then one checkedbox.

.. code-block:: python

   def messages_page():
    current_user.activetab = 3
    messages = current_app.messageList.get_messages()
    if request.method == 'POST':
        value = request.form.getlist('message')
        for i in value:
            current_app.messageList.delete_message(i)
        return redirect(url_for('messages_page'))
    return render_template('messages.html', messages=messages)



The messages are deleted for that correspondin ID, as shown below

.. code-block:: python

   def delete_message(self, messageid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("DELETE FROM MESSAGES WHERE MESSAGEID = %s""", (messageid,))
        connection.commit()




**Media Entity:**

*MEDIA* and *TAGS* tables are created for this entity.

In *MEDIA* table there are 4 columns which are *photoid*, *ownerid*, *content* and *url*.

.. code-block:: SQL

   CREATE TABLE MEDIA(
      PHOTOID SERIAL PRIMARY KEY,
      OWNERID INTEGER REFERENCES USERPROFILE (ID) ON DELETE SET NULL,
      DESCRIPTION VARCHAR (100),
      URL VARCHAR(500)
   );

Photo is stored as URL in the website.


In **add_photo** function, it takes media object as parameter. Besides, it retrieves the ownerid like in message example.
After that it inserts the ownerid, description and url in the *MEDIA* table. Media object consist of all necessary data.

.. code-block:: python

   def add_photo(self, media):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        ownerid = cursor.fetchone()
        cursor.execute("""INSERT INTO MEDIA (OWNERID, DESCRIPTION, URL) VALUES (%s, %s, %s)""", (ownerid, media.description, media.url))
        connection.commit()


In server.py file, content and url are taken from the html file and put in to the media object.Finally, **add_photo** function
 is called.

.. code-block:: python

   def newphoto_page():
    current_user.activetab = 4
    if request.method == 'POST':
        content = request.form['content']
        url = request.form['url']
        ownerid = 1
        media = Media(ownerid, content, url)
        current_app.mediaList.add_photo(media)
        return redirect(url_for('media_page'))
    return render_template('newphoto.html')



For shows the photos that user added and tagged, second query is written for retrieving the photoids of the corresponding photos.
Then with using this IDs ownerid, description and url of the photo are retrieved and return into the media object, as shown below.

.. code-block:: python

   def get_photos(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT * FROM ((SELECT DISTINCT PHOTOID FROM MEDIA WHERE OWNERID = %s) UNION (SELECT DISTINCT TAGEDPHOTOID FROM TAGS WHERE TAGEDUSERID = %s)) AS PHOTOS""",(userid,userid))
        photosid=cursor.fetchall()
        media = []
        for id in photosid:
            cursor.execute("SELECT T1.*, T2.ID FROM MEDIA AS T1 INNER JOIN USERS AS T2 ON T1.OWNERID = T2.ID WHERE T1.PHOTOID = %s""",(id,))
            media += [(key, Media(ownerid, description, url))
                    for key, ownerid, description, url, id in cursor]
        print (media)
        return media


In this **media_page** function, photos are retrieved first, then the tag of the photos are taken that will be explained later.
Then, if delete button is clicked, it takes which items are checked and send them in **delete_photo** function. Finally, media and
tagList objects are sent to html file for printing to the screen.

.. code-block:: python

   def media_page():
    current_user.activetab = 4
    media = current_app.mediaList.get_photos()
    tagList = []
    for item in media:
        tagList += TagList.get_tags(item[0])
    if request.method == 'POST':
        if request.form['operation'] == 'delete':
            value = request.form.getlist('media')
            for i in value:
                current_app.mediaList.delete_photo(i)
            return redirect(url_for('media_page'))
        if request.form['operation'] == 'update':
            value = request.form.getlist('media')
    return render_template('media.html', media = media, tagList=tagList)


Delete operations are done in below. It takes the photoid and deletes from the table which item has that id.

.. code-block:: python

    def delete_photo(self, photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("DELETE FROM MEDIA WHERE PHOTOID = %s""", (photoid,))
        connection.commit()


Update operations are done below. New description and id of that corresponding photo are taken and updated in the database.

.. code-block:: python

   def update_photo(self, description,photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("UPDATE MEDIA SET DESCRIPTION = %s WHERE PHOTOID = %s""",(description,photoid))
        connection.commit()


In this function, new description and id of that corresponding photo is taken from html and sent to **update_photo** function.

.. code-block:: python

   def updatemedia_page():
    current_user.activetab = 4
    media = current_app.mediaList.get_photos()
    if request.method == 'POST':
        value = request.form.getlist('media')
        description = request.form['newdes']
        for i in value:
                current_app.mediaList.update_photo(description,i)
        return redirect(url_for('media_page'))
    return render_template('updatemedia.html', media = media)


*TAGS* table is created for adding tag into the photos it has ID of the photo which is tagged as references to ID of *MEDIA* table and
ID of the user which is tagged that photo as references to ID of *USERPROFILE* table.

.. code-block:: SQL

   CREATE TABLE TAGS(
   TAGID SERIAL PRIMARY KEY,
   TAGEDPHOTOID INTEGER REFERENCES MEDIA (PHOTOID) ON DELETE CASCADE,
   TAGEDUSERID INTEGER REFERENCES USERPROFILE (ID) ON DELETE CASCADE
);


Tag is added in this function below. It takes the username and photoid as parameter and insert it into the *TAGS* table.

.. code-block:: python

   def add_tag(self, username, photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        tageduserid = cursor.fetchone()
        cursor.execute("""INSERT INTO TAGS (TAGEDPHOTOID, TAGEDUSERID) VALUES (%s, %s)""", (photoid, tageduserid))
        connection.commit()


This function which is below is used for getting the current tags on that current photo which is given to the function *photoid*
as parameter. It returns the tags object which has photoid and username in it. And this object is used in html file for printing
the tag in corresponding photo.

.. code-block:: python

   def get_tags(photoid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("SELECT T1.PHOTOID, USERS.USERNAME FROM MEDIA AS T1 INNER JOIN TAGS AS T2 ON PHOTOID = TAGEDPHOTOID INNER JOIN USERS ON T2.TAGEDUSERID = USERS.ID WHERE PHOTOID=%s""",(photoid,))
        tags = []
        for photoid, username in cursor:
            tags += [(photoid,username)]
        print(tags)
        return tags


In this **tag_page** function, value consist of the ID of the photo which is selected with the radio button. Tagname has the name of
the user which is selected from the dropdown menu. Finally it is sent to **add_tag** function with tagname and the ID of the selected
photo.

.. code-block:: python

   def tag_page():
    current_user.activetab = 4
    users = None
    media = current_app.mediaList.get_photos()
    if request.method == 'POST':
        value = request.form.getlist('media')
        tagname = request.form['tag']
        for i in value:
            current_app.tagList.add_tag(tagname, i)
        return redirect(url_for('media_page'))
    with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT USERNAME FROM USERS""")
                users = cursor.fetchall()
    return render_template('tagphoto.html', media=media, users = users)




**Quiz Entity:**


There are three tables are used for creating the quiz entity. These tables are *QUIZ*, *OPTIONS* and *POINTS*. Quiz table is used
for holding the questions and the sender and reciever of the questions. Options holds the ID of the question as references to the
ID of the *QUIZ* table and also consist of the option of the questions and holds the correctness boolean variable for deciding
if that option is correct answer or not. Lastly, in *POINTS* table, it is held the points of the users. All corresponding tables
are shown below.

Quiz table:

.. code-block:: SQL

   CREATE TABLE QUIZ(
   ID SERIAL PRIMARY KEY,
   SENDERID INTEGER REFERENCES USERPROFILE (ID) ON DELETE SET NULL,
   RECIEVERID INTEGER REFERENCES USERPROFILE (ID) ON DELETE SET NULL,
   CONTENT VARCHAR(500),
   ISANSWERED BOOLEAN DEFAULT FALSE
);

Options table:

.. code-block:: SQL

   CREATE TABLE OPTIONS(
   OPTIONID SERIAL PRIMARY KEY,
   QUESTIONID INTEGER REFERENCES QUIZ (ID) ON DELETE CASCADE,
   CHOICE VARCHAR(100),
   CORRECTNESS BOOLEAN DEFAULT FALSE
);

Points table:

.. code-block:: SQL

   CREATE TABLE POINTS(
   USERID INTEGER PRIMARY KEY REFERENCES USERPROFILE (ID) ON DELETE CASCADE,
   POINT INTEGER DEFAULT 0
);




**add_quiz** function takes reciever user, options, content of the question and choice as parameter. Firstly, ID of the sender
is found in the first query. After that ID of the receiver user is taken in the second query. Then content, sender and receiver
users are inserted into the *QUIZ* table. Then the options of the question are added. If the i value in the loop is equal to
value of the choice which indicates to correct answer, insert it into the *OPTIONS* table as true otherwise insert it as false.

.. code-block:: python

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


**get_quiz** is used for list the questions which are sent to that user. It returns the ID of the question, content, isanswered boolean
which is used if the question is answered or still waiting to answer. Because according to that boolean value the question is shown on
the quiz page or not. Optionid, choice of the user and correctness of that choice.

.. code-block:: python

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


This function below is used for deciding if the choosen option is correct or not. It takes the optionid and checks the correctness
value. If it is true returns true otherwise returns false.

.. code-block:: python

   def check_correctness(self, optionid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT CORRECTNESS FROM OPTIONS WHERE OPTIONID=%s""", (optionid,))
        correctness = cursor.fetchone()
        return correctness



In **quiz_page**, firstly the questions are got if exist. Then the points of that user is taken(it will be explained below).
Then the choice of the user is held and **check_correctness** function is called for checking the correctness of users choices.
If choice is correct **update_points** is called for adding 5 points to user. Finally, in **update_quiz** function the isanswered
boolean variable is changed and if the question is answered it is not shown on the quiz page anymore.

.. code-block:: python

   def quiz_page():
    current_user.activetab = 5
    quiz = current_app.quizList.get_quiz()
    (points,) = current_app.quizList.get_points()
    idList = []
    answers = []
    corList = []
    if request.method == 'POST':
        if request.form['operation'] == 'send':
            for id, content, isanswered, optionid, choice, correctness in quiz:
                idList += [(id)]
            for i in range(0, len(idList), 4):
                choosen = request.form.getlist(str(idList[i]))
                for j in choosen:
                    (cor,) = current_app.quizList.check_correctness(j)
                    if cor:
                        if points == None:
                            current_app.quizList.add_points()
                        else:
                            current_app.quizList.update_points()
                    current_app.quizList.update_quiz(str(int(math.ceil(int(j)/4))))
            return redirect(url_for('quiz_page'))
        elif request.form['operation'] == 'delete':
            current_app.quizList.delete_quiz()
            return redirect(url_for('quiz_page'))
    return render_template('quiz.html', quiz = quiz, points = points)



In this function the points of the current user is retrieved from the *POINTS* table.

.. code-block:: python

   def get_points(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("""SELECT POINT FROM POINTS WHERE USERID=%s""", (userid,))
        points = cursor.fetchone()
        print(points)
        return points


In this function the points of current users is updated(added 5 points).

.. code-block:: python

   def update_points(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid = cursor.fetchone()
        cursor.execute("UPDATE POINTS SET POINT =POINT+5 WHERE USERID=%s""",(userid,))
        connection.commit()


In this function, isanswered value is changed to '*true*'.

.. code-block:: python

   def update_quiz(self, questionid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("UPDATE QUIZ SET ISANSWERED = TRUE WHERE ID = %s""",(questionid,))
        connection.commit()



In this **delete_quiz** function all questions that current user is recieved, is deleted.

.. code-block:: python

   def delete_quiz(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        recieverid = cursor.fetchone()
        cursor.execute("DELETE FROM QUIZ WHERE RECIEVERID = %s""", (recieverid,))
        connection.commit()










