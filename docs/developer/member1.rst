Parts Implemented by İsmail Emre Çetiner
========================================

**User Entity:**

User entity is the main entity of the application, which is referenced by most of the tables. User entity consists of two tables:

   * Users
   * Userprofile

Registeration information of all users are kept in **Users** table which has 4 columns. ID is the primary key of the table which is used nearly for all references to this table.

   .. code-block:: sql

      CREATE TABLE USERS(
         ID SERIAL PRIMARY KEY,
         USERNAME VARCHAR(20) UNIQUE NOT NULL,
         PASSWORD VARCHAR(150),
         JDATE DATE NOT NULL DEFAULT CURRENT_DATE
      );

The code above shows the creation of the **Users** table. Here, username is a candidate key and it could be the primary key of the table but for practicality of the application, an extra column **ID** is added and used as a primary key.

Other user information such as nickname, bio and other profile information are kept in **Userprofile** table and it has 8 columns. ID is the primary key and foreign key to users of this table.

   .. code-block:: sql

      CREATE TABLE USERPROFILE(
         ID INTEGER PRIMARY KEY REFERENCES USERS ON DELETE CASCADE,
         USERNAME VARCHAR(20) UNIQUE NOT NULL,
         NICKNAME VARCHAR(20) NOT NULL,
         TWEETS INTEGER DEFAULT 0,
         FOLLOWING INTEGER DEFAULT 0,
         FOLLOWERS INTEGER DEFAULT 0,
         LIKES INTEGER DEFAULT 0,
         BIO VARCHAR(100)
      );

Creation of the **Userprofile** table is shown above. For the simplicity of some queries, username is included also in this table. Other than that, following and follower numbers, bio, tweet and like counts and such information is kept in the table. **Userprofile** table is also referenced by various tables, especially for the operations which needs the username or nickname of the user.

   .. code-block:: python

      class User(UserMixin):
          def __init__(self, username, password):
              self.username = username
              self.password = password
              self.active = True
              self.is_admin = False
              self.activetab = 0

Definition of the User class of shown above. It stores login information and the active tab which is used to indicate that tab to the user on the navigation bar. It also stores the user type which is either admin or a normal user. If it is admin, it has some privilages. User object is used nearly in all operations in the application. The first and basic usage of the class is register and login operations, which are explained below.

**Register:**

The register page is used to add new users to the application. For the registeration, user should type a username and password (twice) and submit the form. After submitting the form, register function is processed like that:

   .. code-block:: python

      if request.method == 'POST' and form.validate():
        username = form.username.data
        password = pwd_context.encrypt(form.password.data)
        try:
            #insertions to users and userprofile tables
            login_user(get_user(username))
            return redirect(url_for('home_page'))
        except:
            flash('Username is already taken')

As it is seen above, the username and hashed password is taken as variables and the application tries to insert them into the related tables. If they are successfully inserted, the user is automatically logged in and user is redirected to the home page. Otherwise, a flash message is displayed which states that the username is already taken.

Insertions into the tables are held as follows:

   .. code-block:: python

      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                cursor.execute("""INSERT INTO USERS (USERNAME, PASSWORD) VALUES (%s, %s)""", (username, password))

      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                userid = get_userid(username)
                cursor.execute("""INSERT INTO USERPROFILE (ID, NICKNAME, USERNAME, BIO) VALUES(%s, %s, %s, %s)""", (userid, username, username, 'bio'))

Here, the first insertion is committed for **Users** table. If the insertion is successful, the user ID is got by the related function and user is inserted into the **Userprofile** table with this ID. The reason for two-step insertion is about unsuccessful insertion attempts. When a user tries to register with a username which already exists, the serial ID is incremented for **Users** table and the connection is terminated without attempting an insertion to **Userprofile** table. Next time, even if the username is different, the mismatch between ID attributes of tables, foreign key constraint could not be satisfied and register operation fails. To get rid of that, ID is got from the first table and inserted into the second one.

**Login:**

If a user is not logged in yet, he is not allowed to access any of the pages and redirected to the login page automatically. Login operation is implemented as follows:

   .. code-block:: python

      if request.method == 'POST' and form.validate():
        username = form.username.data
        user = get_user(username)
        if user is not None:
            password = form.password.data
            if pwd_context.verify(password, user.password):
                login_user(user)
                #automatic database initialization
                flash('You have logged in.')
                next_page = request.args.get('next', url_for('home_page'))
                return redirect(next_page)
        flash('Invalid credentials.')
    return render_template('login.html', form=form)

In this function, the username and password is got from the form and the user with the **username** is retrieved from the database. There is a special login prosedure for admin, which will be explained soon. If the username is found and a user is returned, its password is compared with the given one and if it is verified succesfully, user login is performed. That was the login prosedure for normal users. For admin users, there is a pre-defined password in the application, which is hashed value of the admin password:

   .. code-block:: python
   
      ADMINPASS = '$6$rounds=603422$ZgQRx3Mm/YuUaION$b/Vwzuno1Q7e1KPWehLbRdmvdf/Bjj5.4a.fvcz3TNCl.Rn2CLbQPCsGSIBarDYHMzq3jjN8KDLkBtKJzBclf0'

In **"get_user"** function, admin login is verified with this password:

   .. code-block:: python
   
      def get_user(username):
          if (username=='admin'):
              user = User(username, current_app.config['ADMINPASS'])
              user.is_admin = True
              return user
          try:
              #get user credentials from database

If the given username is **admin"", the pre-defined password is returned in the User object and is_admin attribute is marked as True.

In addition, there is an automatic database initializtion for the first login of the admin user, which is implemented as follows:

   .. code-block:: python
   
      try:
         with dbapi2.connect(app.config['dsn']) as connection:
              with connection.cursor() as cursor:
                   cursor.execute("""SELECT * FROM USERS WHERE ID=1""")
      except:
         return redirect(url_for('initialize_database'))

Here, after the successful login, we check the existance of the first user, which is **admin**, in the database. If the query is not successfully completed, it means that the database has not been initialized yet, because the admin is inserted into the User table as the database is initialized. So, admin is redirected to the database initialization page and database is initialized.

The update operations for these two tables are implemented in the **Update Profile** page and the queries for these operations are below:

   .. code-block:: python
   
      #form operations
      cursor.execute("""UPDATE USERS SET PASSWORD=%s WHERE USERNAME=%s""", (password,current_user.username))
      #form operations
      cursor.execute("""UPDATE USERPROFILE SET NICKNAME=%s, BIO=%s WHERE USERNAME=%s""", (updateForm.nickname.data,updateForm.bio.data,current_user.username))

Delete operation for **Users** table can be done only by the administrator, and **Userprofile** table has "ON DELETE CASCADE" option on its foreign key to **Users** table, which is ID. The delete query is below:

   .. code-block:: python
   
      #form operations
      cursor.execute("""DELETE FROM USERS WHERE USERNAME=%s""",(username,))

In addition to these tables, **Follows** table which has 2 columns can be counted as a part of the **User** entity and its creation query is as follows:

   .. code-block:: sql
   
      CREATE TABLE FOLLOWS(
         FOLLOWERID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
         FOLLOWEDUSER INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
         PRIMARY KEY (FOLLOWERID, FOLLOWEDUSER)
      );

Here, both of the columns reference to the **Users** table and they form a primary key together. By defining the couple as a primary key, we can prevent the table from duplicate follow operations. Insertion and delete operations for the table are implemented in **Follow/Unfollow** page and details are below:

   .. code-block:: python
   
      ##insert/follow operation:
      if followerid and followedid:
            cursor.execute("""INSERT INTO FOLLOWS (FOLLOWERID, FOLLOWEDUSER) VALUES (%s, %s)""",(followerid,followedid))
            cursor.execute("""UPDATE USERPROFILE SET FOLLOWING = FOLLOWING +1 WHERE (ID = %s) """,(followerid,))
            cursor.execute("""UPDATE USERPROFILE SET FOLLOWERS = FOLLOWERS +1 WHERE (ID = %s) """,(followedid,))

      ##delete/unfollow operation:
      if followerid and followedid:
            cursor.execute("""SELECT FOLLOWERID FROM FOLLOWS WHERE (FOLLOWERID = %s) AND (FOLLOWEDUSER = %s)""",(followerid,followedid))
            flag = cursor.fetchone()
            for i in flag:
                cursor.execute("""DELETE FROM FOLLOWS WHERE (FOLLOWERID = %s) AND (FOLLOWEDUSER = %s)""",(followerid,followedid))
                cursor.execute("""UPDATE USERPROFILE SET FOLLOWING = FOLLOWING -1 WHERE (ID = %s)""",(followerid,))
                cursor.execute("""UPDATE USERPROFILE SET FOLLOWERS = FOLLOWERS -1 WHERE (ID = %s)""",(followedid,))

In unfollow operation, we use a flag and check the existance of the (follower-followed) couple before decrementing related attributes. If this check is not done, delete operation would run successfully but not delete any rows from the database, so that we can end up with wrong attributes, i.e. negative numbers.


**Application Entity**

Application entity forms a base for possible implementations of extensions or external applications for the website. Application entity consists of 2 tables, which are:

   * Apps
   * Appusers

**Apps** table holds the basic information about the application in 4 columns and the creation of the table is as follows:

   .. code-block:: sql
   
      CREATE TABLE APPS(
         ID SERIAL PRIMARY KEY,
         APPNAME VARCHAR(30) NOT NULL,
         USERCOUNT INTEGER DEFAULT 0,
         ACTIVE BOOLEAN DEFAULT FALSE
      );


ID is the serial primary key of the table and referenced from the other table of the entity, **Appusers**. Each application has a boolean attribute **Active** and keeps the status of the application. In application settings, only active apps will be available for users. Insertion function of the **Apps** table is given below:

   .. code-block:: python
   
      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                cursor.execute("""INSERT INTO APPS (APPNAME) VALUES (%s)""", (appname,))
                if request.form['btn'] == 'add_act':
                   cursor.execute("""UPDATE APPS SET ACTIVE=TRUE WHERE APPNAME=(%s)""", (appname,))

Here, the application with the given name by **admin** is inserted into the **Apps** table with the default **Active** attribute, false. Then the button is checked and if the clicked button is "Add and Activate", an update operation is done and the attribute is changed to True.

After adding the application, it is possible to activate and deactivate it at any time. The query is the same as the last one. For delete operation, following query is used:

   .. code-block:: python
   
      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                if selection == 'Delete':
                    cursor.execute("""DELETE FROM APPS WHERE APPNAME=(%s)""", (appname,))

**Appusers** table keeps the application usage information and has 3 columns. Creation query of the table is given:

   .. code-block:: sql
   
      CREATE TABLE APPUSERS(
         USERID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
         APPID INTEGER REFERENCES APPS(ID) ON DELETE CASCADE,
         SUB_DATE DATE NOT NULL DEFAULT CURRENT_DATE,
         PRIMARY KEY (USERID, APPID)
      );

The table has two foreign keys. Userid is the reference to the **Users** table, and Appid references to the **Apps** table. At the same time, the combination of these attributes form the primary key, and duplicate rows are not allowed.

When a user changes the application settings, the **Appusers** table is affected from those changes. Related code block is as follows:

   .. code-block:: python
   
      cursor.execute("""DELETE FROM APPUSERS WHERE USERID=%s""",(get_userid(current_user.username),))
            #getting selected applications
            for (appid,) in appids:
                cursor=connection.cursor()
                cursor.execute("""INSERT INTO APPUSERS (USERID, APPID) VALUES (%s, %s)""", (userid,appid))
                print(appid,userid)

Since the table does not have an attribute which indicates the changes in application preferences, all rows with the ID of the current user is deleted, and the selected applications are coupled with the user ID and inserted into the table.

**Gift Entity:**

Gift entity is created for improving the connection between users and users can send gifts to each other. Gifts are defined and managed by the **admin** and the entity consists of 2 tables.

   * Gifts
   * Sentgifts

Basic information about the gifts are kept in **Gifts** table and it consists of 3 columns:

   .. code-block:: sql
   
      CREATE TABLE GIFTS(
         ID SERIAL PRIMARY KEY,
         GIFTNAME VARCHAR(30) NOT NULL,
         DESCRIPTION VARCHAR(100)
      );

As it is seen, ID is the serial primary key and the table has two more attributes, which are giftname and description. All of the operations about the **Gifts** table done by the **admin** and it has the right to create, update, delete gifts. Under the admin panel, there is a link to **Manage Gifts** page and database operations for the table are done in this page. First of all, insertion is done by the following code:

   .. code-block:: python
   
      giftname = addform.giftname.data
      description = addform.description.data
         with dbapi2.connect(app.config['dsn']) as connection:
              with connection.cursor() as cursor:
                   cursor.execute("""INSERT INTO GIFTS (GIFTNAME, DESCRIPTION) VALUES (%s,%s)""", (giftname,description))

Here, the new gift is created with the given name and description by the **admin**. After adding a gift, **admin** has the opportunity to update or delete the gift at any time. Update operation is done as follows:

   .. code-block:: python
   
      giftname = updateform.gifts.data
      description = updateform.description.data
      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                cursor.execute("""UPDATE GIFTS SET DESCRIPTION=%s WHERE GIFTNAME=%s""",(description,giftname))

It is not possible to change de name of the gift, but **admin** can change the description of a gift by entering a new value to the related text area and submitting the form. In this form, there is also a delete button which removes the gift from the database and the related code block is:

   .. code-block:: python
   
      giftname = updateform.gifts.data
      with dbapi2.connect(app.config['dsn']) as connection:
           with connection.cursor() as cursor:
                cursor.execute("""SELECT DESCRIPTION FROM GIFTS WHERE GIFTNAME=%s""",(giftname,))

The second table of the entity is **Sentgifts** which stores the gift exchange between users. It consists of 4 columns and created with the following query:

   .. code-block:: sql
   
      CREATE TABLE SENTGIFTS(
         SENDER INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
         RECEIVER INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
         GIFTID INTEGER REFERENCES GIFTS(ID) ON DELETE CASCADE,
         S_TIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
         PRIMARY KEY (SENDER, RECEIVER, GIFTID)
      );

Sender and receiver are the foreign keys to the user table and giftid holds the value for corresponding gift. As the gift is sent, current timestamp is inserted into the related column as the sending time. Primary key of the table is combination of two columns, and sending a gift to a user twice is not allowed.

The insertions to the table is done by following lines:

   .. code-block:: python
   
      else:
         try:
             with dbapi2.connect(app.config['dsn']) as connection:
                  with connection.cursor() as cursor:
                       cursor.execute("""INSERT INTO SENTGIFTS VALUES(%s,%s,%s)""",(get_userid(current_user.username),sendform.sendto.data,sendform.gifts.data))
                       cursor.execute("""SELECT USERNAME FROM USERS WHERE ID=%s""",sendform.sendto.data)
                       sentto = cursor.fetchone()[0]
                       cursor.execute("""SELECT GIFTNAME, DESCRIPTION FROM GIFTS WHERE ID=%s""",(sendform.gifts.data,))
                       values = cursor.fetchall()
                       #flash gift sent message
         except:
            #flash cannot send message

Here, the selected gift id and user id is given as the values to the query and the insertion is completed. If there is a primary key violation, an error message is displayed.

For displaying sent and received gifts, following queries are used:

   .. code-block:: python
   
      with connection.cursor() as cursor3:
          cursor3.execute("""SELECT USERNAME, NICKNAME, GIFTNAME,
          DESCRIPTION, TO_CHAR(S_TIME, 'DD Mon YYYY, HH24:MI') FROM SENTGIFTS INNER JOIN GIFTS ON GIFTID=ID
          INNER JOIN USERPROFILE ON SENDER=USERPROFILE.ID WHERE (RECEIVER=%s) ORDER BY S_TIME DESC""",(get_userid(current_user.username),))
          receivedgifts = cursor3.fetchall()
      with connection.cursor() as cursor4:
          cursor4.execute("""SELECT USERNAME, NICKNAME, GIFTNAME,
          DESCRIPTION, TO_CHAR(S_TIME, 'DD Mon YYYY, HH24:MI') FROM SENTGIFTS INNER JOIN GIFTS ON GIFTID=ID
          INNER JOIN USERPROFILE ON RECEIVER=USERPROFILE.ID WHERE (SENDER=%s) ORDER BY S_TIME DESC""",(get_userid(current_user.username),))
          sentgifts = cursor4.fetchall()

Here, received gifts are fetched with the sender username and nickname, giftname, description and sending time with some formatting. Like received gifts, sent gifts are fetched with the same attributes and given to the html file in order to print them in the list.

If the user wants to delete the gifts, there is a "Delete all gifts" button at the end of the page and the following lines are executed after pressing the button:

   .. code-block:: python
   
      if request.form['btn'] == 'delete':
         with dbapi2.connect(app.config['dsn']) as connection:
              with connection.cursor() as cursor:
                   cursor.execute("""DELETE FROM SENTGIFTS WHERE RECEIVER = %s OR SENDER = %s""",(get_userid(current_user.username),get_userid(current_user.username)))
         flash('All gifts deleted.')

The lines above deletes all gifts that is sent or received by the current user.


