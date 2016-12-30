Parts Implemented by Mert Kurtcan
=================================

In this project Settings, Notifications and Style operations are done by me.

Four tables are created for handling these three entities such as *USERINFO*, *NOTIFS* and *STYLEINFO*.

**Userinfo Entity:**
--------------------

Firstly *USERINFO* table is created with this operation.

SQL Code:

.. code-block:: SQL

   CREATE TABLE USERINFO(
      USERID INTEGER PRIMARY KEY NOT NULL REFERENCES USERS (ID) ON DELETE CASCADE,
      NAME VARCHAR(20) NOT NULL,
      SURNAME VARCHAR(20) NOT NULL,
      NICKNAME VARCHAR(20) NOT NULL,
      EMAIL VARCHAR(25) NOT NULL,
      LANGUAGE VARCHAR(20) NOT NULL
    );

There are 6 columns in this table. *userid* is primary key that holds the ID of the userinfo and refereced by ID of the *USERPROFILE*.
Other instances of table are name, surname, nickname, email, and language which holds each information of the Userinfo.

*Insert Userinfo*
^^^^^^^^^^^^^^^^^

User information is inserted with empty data when registration occurs and implemented in server.py file

.. code-block:: pyton

   userid = get_userid(username)
   cursor.execute("""INSERT INTO USERINFO (USERID, NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(%s, %s, %s, %s, %s, %s)""",
                                   (userid, '', '', '', '', ''))


*Update Userinfo*
^^^^^^^^^^^^^^^^^
User information is updated in change_settings method which is implemented in usersettings.py file.
This method takes current user and other information comes from user side as an input and search for users' identity number from USERS table.
Then executes a simple **UPDATE** SQL statement.

**Usersettings.py:**

.. code-block:: python

   def change_settings(email,language, nickname,username, name, surname):
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
        values=cursor.fetchone()
        id=values[0]
        cursor.execute("""UPDATE USERINFO SET NAME=%s, SURNAME=%s, NICKNAME=%s, EMAIL=%s, LANGUAGE=%s WHERE USERID=%s""",
                       (name,surname, nickname, email, language, id))

        connection.commit()
        cursor.close()
        connection.close()
        return True
    except:
        return False

*Select Userinfo*
^^^^^^^^^^^^^^^^^
User information is viewed in show_settings method which is implemented in usersettings.py file.
This method takes current user and other information comes from user side as an input and search for users' identity number from USERS table.
Then executes a simple **SELECT** SQL statement.

**Usersettings.py:**

.. code-block:: python

   def show_settings(username):
       try:
           connection = dbapi2.connect(current_app.config['dsn'])
           cursor = connection.cursor()
           cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
           values=cursor.fetchone()
           id=values[0]
           cursor.execute("""SELECT NAME, SURNAME, NICKNAME, EMAIL,LANGUAGE FROM USERINFO WHERE USERID=%s""", (id,))
           values = cursor.fetchone()

           connection.commit()
           cursor.close()
           connection.close()
           return values
       except:
           return False

*Delete Userinfo*
^^^^^^^^^^^^^^^^^
User information is removed in delete_settings method which is implemented in usersettings.py file.
This method takes current user and other information comes from user side as an input and search for users' identity number from USERS table.
Then executes **DELETE** SQL statement, then **INSERT** SQL statement to consistency for other operations .

**Usersettings.py:**

.. code-block:: python

   def delete_settings(username):
       try:
           connection = dbapi2.connect(current_app.config['dsn'])
           cursor = connection.cursor()
           cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
           values=cursor.fetchone()
           id=values[0]
           cursor.execute("""DELETE FROM USERINFO WHERE USERID=%s""", (id,))
           cursor.execute("""INSERT INTO USERINFO (USERID, NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(%s,%s, %s, %s, %s, %s)""",
                              (id,'', '', '', '', ''))

           connection.commit()
           cursor.close()
           connection.close()
           return values
       except:
           return False

**Server.py:**

Personal information about user taken here which sent to the html for printing. Also delete operation is handled here.

.. code-block:: python

   def settings_page():
       try:
           if request.method == 'POST' and request.form['btn']=="update":
               name = request.form['name']
               surname = request.form['surname']
               email = request.form['email']
               language = request.form['Language']
               nickname = request.form['nickname']
               username = current_user.username
               if change_settings(email,language,nickname,username, name, surname):
                   flash("Updated")
               else:
                   flash("Could not update")
                   return render_template('settings.html')

           elif request.method == 'POST' and request.form['btn']=="show":
               username = current_user.username
               values=show_settings(username)
               return render_template('settings.html', table=values)

           elif request.method == 'POST' and request.form['btn']=="delete":
               username = current_user.username
               if delete_settings(username):
                   flash("Deleted")
               else:
                   flash("Could not delete")
                   return render_template('settings.html')

           return render_template('settings.html')
       except:
           pass
       return render_template('home.html')


**Notification Entity:**
------------------------
Firstly *NOTIFS* table is created with this operation.

SQL Code:

.. code-block:: SQL

   CREATE TABLE NOTIFS(
       NOTIFID SERIAL PRIMARY KEY,
       USERID INTEGER NOT NULL REFERENCES USERS (ID) ON DELETE CASCADE,
       FOLLOWERID INTEGER NOT NULL,
       PERM INTEGER NOT NULL
   );


There are 4 columns in this table. *notifid* is a primary key that holds the ID of the notif table. *userid* is a foreign key refereced by ID of the *USERPROFILE*
Other two columns of table are *followerid* which holds follower's id on each row and *perm* which holds "on" or "off" status of  notification.

*Insert Notifications*
^^^^^^^^^^^^^^^^^^^^^^
Notification information is inserted with followed user's id, follower user's id when follow operation occurs and implemented in followoperations.py file

.. code-block:: pyton

   cursor.execute("""INSERT INTO NOTIFS (USERID, FOLLOWERID, PERM) VALUES (%s, %s,%s)""",(followedid,followerid, '1'))

*Update and Delete Notifications*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Notification view status is change in notif_settings method which is implemented in usersettings.py file.
This method takes username and "on" or "off" status as an input and search for users' username from USERS table.
Then executes **UPDATE** SQL statement.

**Usersettings.py:**

.. code-block:: python

   def notif_settings(username, notif):
       try:
           connection = dbapi2.connect(current_app.config['dsn'])
           cursor = connection.cursor()
           cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
           values=cursor.fetchone()
           id=values[0]
           cursor.execute("""UPDATE NOTIFS SET PERM=%s WHERE USERID=%s""",(notif, id))

           connection.commit()
           cursor.close()
           connection.close()
           return True
       except:
           return False


*Select Notifications*
^^^^^^^^^^^^^^^^^^^^^^

User Notifications can be selected  in notifications.py file
This function takes username as an input. It executes a SQL **SELECT** statement, then join *USERS* and *NOTIFs* tables. After that, function returns the followers username.

**Notifications.py:**

.. code-block:: python

    def show_set(username):
       try:
           connection = dbapi2.connect(current_app.config['dsn'])
           cursor = connection.cursor()
           cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (username,))
           values=cursor.fetchone()
           id=values[0]

           cursor.execute("""select users.username from users inner join notifs on users.id = (select followerid from notifs where userid = %s) where notifs.perm = '1'""", (id,))
           value=cursor.fetchone()
           followername=value[0]

           connection.commit()
           cursor.close()
           connection.close()
           return followername
       except:
           return False

**Server.py:**

In this **notifs_page** function, if "on" or "off" status selected,it sends notifications status to *notif_setting*. Then, followers name would be viewed
according to return this function and taken here and sent to the html for printing.

.. code-block:: python

   def notifs_page():
       if request.method=='POST' and request.form['btn']=="notif":
           username = current_user.username
           follower=show_set(username)
           return render_template('notifications.html', person=follower)

       elif request.method == 'POST' and request.form['btn']=="notif_update":
           case = request.form['notif']
           username = current_user.username
           if notif_settings(username, case):
               flash("Updated")
           else:
               flash("Could not update")
               return render_template('home.html')
       else:
           return render_template('notifications.html')


**Style Entity:**
-----------------
Firstly *STYLEINFO* and *COLORINFO* table is created with this operation. These tables created for user side interface operations.

SQL Code:

.. code-block:: SQL

   CREATE TABLE COLORINFO(
      COLORID SERIAL PRIMARY KEY,
      COLOR VARCHAR(30) NOT NULL
   );

.. code-block:: SQL

   CREATE TABLE STYLEINFO(
      STYLEID SERIAL PRIMARY KEY,
      USERID INTEGER NOT NULL REFERENCES USERINFO(USERID) ON DELETE CASCADE,
      COLORID INTEGER NOT NULL REFERENCES COLORINFO ON DELETE CASCADE
   );


