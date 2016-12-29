Parts Implemented by Yusuf Ekiz
===============================

I implemented 6 tables and their operations in this project. Tables can be seen below

* **LISTS**
* **LISTMEMBERS**
* **POLLS**
* **CHOICES**
* **VOTES**
* **LIKES**


LISTS Implementation
--------------------
A list is a curated group of accounts. You can create your own lists or subscribe to lists created by others.
When the user clicks the list,the list will show the tweets which are tweeted by members of the lists.
For lists I implemented *LISTS* and *LISTMEMBERS* table. LISTS table is an entity. LISTMEMBERS is a auxiliary table

LISTS Table and Operations (1st ENTITY)
---------------------------------------
LISTS table holds the all lists in the application.It is referenced by *LISTMEMBERS* table.

This table has following columns

* *LISTID* as serial primary key
      Primary key of the table
* *SUBSCRIBERS* as integer and default 0
      Holds the number of users who are subscribing the list
* *MEMBERS* as integer and default 0
      Holds the number of users who are the insiders of the list
* *NAME* as varchar and not null
      Name of the list
* *CREATORID* as integer and not null references userprofile table
      Holds the id of the user who created the list

SQL CODE:

.. code-block:: sql

         CREATE TABLE LISTS(
            LISTID SERIAL PRIMARY KEY,
            SUBSCRIBERS INTEGER DEFAULT 0,
            MEMBERS INTEGER DEFAULT 0,
            NAME VARCHAR(30) NOT NULL,
            CREATORID INTEGER NOT NULL REFERENCES USERPROFILE (ID) ON DELETE CASCADE
            );

Also python classes listoflists and list are used for operations.
These classes are implemented in listoflist.py and list.py files.

**List class**

.. code-block:: python

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

**ListofList class**

.. code-block:: python

   class ListOfLists:
    def __init__(self,name):
        self.name=name


*Create a New List*
^^^^^^^^^^^^^^^^^^^
A list is created in a addList function which is implemented in listoflist.py file (ListofLists class).
This function will take a list object as an input. And inserts the new list to the LISTS table

.. code-block:: python

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
        return

*Delete List*
^^^^^^^^^^^^^
A list is deleted in deleteList() function which is implemented in listoflist.py file (ListofLists class).
This function will take listname and creatorname as inputs. At first it will find the creatorid then it will execute a **DELETE** query with creatorid and listname.

.. code-block:: python

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

*Update List*
^^^^^^^^^^^^^
Name of a list is updated in updateName function which is implemented in list.py file(List class). It has only one input which is newName.
It executes a simple **UPDATE** SQL query.

.. code-block:: python

     def updateName(self,newName):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE LISTS SET NAME=%s WHERE NAME=%s AND CREATORID=%s""",(newName,self.name,self.creatorid) )
        self.name=newName
        connection.commit()
        cursor.close()
        connection.close()
        return

*Select List*
^^^^^^^^^^^^^
A list can be selected with getList function which is implemented in listoflist.py file (ListofLists class).
This function takes listname as an input. It executes a simple **SELECT** SQL statement.

.. code-block:: python

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

LISTMEMBERS Table and Operations (Auxiliary Table)
--------------------------------------------------
LISTMEMBERS holds all of the members of all of the lists in application.
This table has following columns

* *LISTID* as serial primary key
      Primary key of the table
* *USERID* as integer and not null references userprofile table
      Holds the id of the user.
* *USERTYPE* as varchar and not null
      Holds the role of the listmember in a list. Usertype can have string values like Insider,Owner or Subscriber.

*LISTID* and *CREATORID* are primary key together.

SQL CODE:

.. code-block:: sql

         CREATE TABLE LISTMEMBERS(
            LISTID INTEGER NOT NULL REFERENCES LISTS(LISTID) ON DELETE CASCADE,
            USERID INTEGER NOT NULL REFERENCES USERPROFILE(ID) ON DELETE CASCADE,
            USERTYPE VARCHAR(18) NOT NULL,
            PRIMARY KEY(LISTID,USERID,USERTYPE)
            );


Some operations are also implemented for LISTMEMBERS table in list.py file.

*Add Insider*
^^^^^^^^^^^^^
As it has been explained above,in application there are 3 member types.
A list can have only a one owner. Owner is added when it is created. You can see above.
We can also add insider members to the lists with addInsider function which is in list.py file(List class).
Its code can be seen below. Function takes membername as a parameter. At first function fetch listid from database.
Then it fetches member id from USERS Table. Finally it inserts the insider to the list.

.. code-block:: python

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

*Add Subscriber*
^^^^^^^^^^^^^^^^
Finally members with subscriber role also can be added to the list with addSubscriber function which is in list.py file(List class).
The only difference between addSubscriber and andMember function is USERTYPE value in the table. At first function fetch listid from database.
Then it fetches member id from USERS Table. Finally it inserts the subscriber.

.. code-block:: python

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


*Delete Insider*
^^^^^^^^^^^^^^^^
Members that who have insider role in list can be deleted with deleteInsider function in list.py file(List class).
This function takes membername as a parameter. At first it finds the member's userid. Then it tries to find the listid. And finally it deletes the listmember.

.. code-block:: python

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


*Delete Subscriber*
^^^^^^^^^^^^^^^^^^^
Members that who have subscriber role in list can be deleted also with deleteSubscriber function in list.py file(List class).
This function takes member name as a parameter. Firstly it will find the member's user id with SELECT query. Then it will try to find the list id.
Finally it will execute **DELETE** SQL statement and UPDATES the number of members in the list.

.. code-block:: python

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


POLLS Implementation
--------------------
Polls allow people to weigh in on questions posed by other people on this social media website. Users can also create their own polls and see the results instantly.
3 tables are created in order to implement  polls. These tables' names are *POLLS* *CHOICES* and *VOTES*.
POLLS and CHOICES are entities. VOTES is an auxiliary table.

POLLS Table and Operations (2nd ENTITY)
---------------------------------------
POLLS table holds all of the polls' data in application. It is referenced by *CHOICES* and *VOTES* tables.

This table has following columns

* *POLLID* as serial primary key
      Primary key of the table
* *POLLQUESTION* as varchar and not null
      Question of the poll
* *CREATORID* as integer and not null references userprofile table
      Holds the id of the user who created the poll
* *VOTENUMBER* as integer and default 0
      Holds the number of votes which are made by users
* *CHOICENUMBER* as integer and default 0
      Holds the number of choices in a poll

SQL CODE:

.. code-block:: sql

        CREATE TABLE POLLS(
           POLLID SERIAL PRIMARY KEY,
           CREATORID INTEGER NOT NULL REFERENCES USERPROFILE(ID) ON DELETE CASCADE,
           VOTENUMBER INTEGER NOT NULL DEFAULT 0,
           CHOICENUMBER INTEGER NOT NULL DEFAULT 0,
           POLLQUESTION VARCHAR(40) NOT NULL
           );

In order to implement the polls. ListofPolls and Poll classes are created. They are created in poll.py and listofpolls.py files.

**Poll class**

.. code-block:: python

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

**ListOfPolls class**

.. code-block:: python

   class ListOfPolls:
    def __init__(self,name):
        self.name=name
        return

*Create a New Poll*
^^^^^^^^^^^^^^^^^^^
A poll is created in a addPoll function which is implemented in listofpolls.py file(ListOfPolls class).
This function will take a poll object as an input. And inserts the new poll to the POLLS table with **INSERT** SQL statement.

.. code-block:: python

     def addPoll(self,poll):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""INSERT INTO POLLS (POLLQUESTION,CREATORID) VALUES (%s, %s)""", (poll.question,userid))
        connection.commit()
        cursor.close()
        connection.close()
        return

*Delete Poll*
^^^^^^^^^^^^^
A poll is deleted in deletePoll function which is implemented in listofpolls.py file(ListOfPolls class)
This function will take pollquestion and pollcreatorname as parameters.
After taking parameters it will find the creator id then executes a **DELETE** SQL query with pollquestion and creator id as parameters.

.. code-block:: python

    def deletePoll(self,pollquestion,pollcreatorname):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(pollcreatorname,))
        temp=cursor.fetchone()
        creatorid=temp[0]
        cursor.execute("""DELETE FROM POLLS WHERE POLLQUESTION=%s AND CREATORID=%s """,(pollquestion,creatorid))
        connection.commit()
        cursor.close()
        connection.close()
        return

*Update Poll*
^^^^^^^^^^^^^
Question of a poll can be updated in updateQuestion function which is implemented in poll.py(Poll Class) file. It has only one input which is newquestion.
It will execute an **UPDATE** SQL statement with parameters such as newquestion,oldquestion(self.question) and creatorid(self.creatorid).

.. code-block:: python

      def updateQuestion(self,newquestion):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""UPDATE POLLS SET POLLQUESTION = %s WHERE POLLQUESTION =%s AND CREATORID=%s """,(newquestion,self.question,self.creatorid))
        self.question=newquestion
        connection.commit()
        cursor.close()
        connection.close()
        return

*Select Poll*
^^^^^^^^^^^^^
A list can be selected with getList function which is implemented in listofpolls.py file(ListOfPolls class).
This function takes listname as an input. It executes a simple SQL **SELECT** statement. Finally it returns a poll object.

.. code-block:: python

      def getAPoll(self,pollquestion):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT VOTENUMBER,CHOICENUMBER FROM POLLS WHERE POLLQUESTION=%s""",(pollquestion,))
        temp2=cursor.fetchone()
        votenumber=temp2[0]
        choicenumber=temp2[1]
        poll=Poll(pollquestion,creatorname)
        poll.votenumber=votenumber
        poll.choicenumber=choicenumber
        return poll

CHOICES Table and Operations (3rd ENTITY)
-----------------------------------------

CHOICES table holds the all of the choices for every poll in application. It is referenced by *VOTES* table.

This table has following columns

* *CHOICEID* as serial unique
      Serial number to represent choices
* *POLLID* as integer and not null references polls table
      Holds the id of the poll which consists of this choice
* *CONTENT* as varchar and not null
      Holds the content of the choice
* *NUMBEROFVOTES* as integer and default 0
      This columns shows how many votes are used for this choice.

*POLLID* , *CHOICEID* , *CONTENT* act as a primary key together.

SQL CODE:

.. code-block:: sql

         CREATE TABLE CHOICES(
            CHOICEID SERIAL UNIQUE,
            POLLID INTEGER NOT NULL REFERENCES POLLS(POLLID) ON DELETE CASCADE,
            CONTENT VARCHAR(20) NOT NULL,
            NUMBEROFVOTES INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (CHOICEID,POLLID,CONTENT)
            );

Operations of choices are implemented in polls.py file(Poll class).

*Create a New Choice*
^^^^^^^^^^^^^^^^^^^^^
Every choice of the poll can be created  in a addChoice function which is implemented in poll.py(Poll class) file.
This function will take the choicecontent as an input. At first it will try to find the current poll in database.
Then it inserts the new choice to the CHOICES table with **INSERT** SQL statement. Finally it updates the NUMBEROFCHOICES column of current poll in POLLS table.

.. code-block:: python

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

*Delete Choice*
^^^^^^^^^^^^^^^
A choice of the poll is deleted in deleteChoice function which is implemented in polls.py file(Polls class)
This function will take choicecontent as an input. At first it will find current poll in the database.
After finding the pollid from database it *DELETE** SQL statement will be executed with pollid and choicecontent parameters.

.. code-block:: python

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

*Select Choices*
^^^^^^^^^^^^^^^^
We can get all the choices with getChoices function in poll.py file(Poll class)
This function takes no additional parameters. It executes a simple SQL **SELECT** statement with current poll's id. And returns a choices array.

.. code-block:: python

   def getChoices(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT POLLID FROM POLLS WHERE CREATORID=%s AND POLLQUESTION =%s """,(self.creatorid,self.question))
        temp=cursor.fetchone()
        pollid=temp
        cursor.execute("""SELECT CONTENT,NUMBEROFVOTES FROM CHOICES WHERE POLLID=%s ORDER BY CHOICEID""",(pollid,))
        choices=[(temp[0],temp[1]) for temp in cursor.fetchall()]
        connection.commit()
        cursor.close()
        connection.close()
        return choices

VOTES Table and Operations (Auxiliary Table)
--------------------------------------------
VOTES Table holds the all the votes for the polls.

This table has following columns

* *CHOICEID* as integer and not null references choices table
      Holds the id of the chosen choice.
* *POLLID* as integer and not null references polls table
      Holds the id of the poll
* *USERID* as integer and not null references userprofile table
      Holds the id of the user.

*POLLID* *CHOICEID* *USERID* act as a primary key together.

Operations of VOTES table are implemented in poll.py file(Poll class).

*Vote for the Poll*
^^^^^^^^^^^^^^^^^^^
A user can use their vote with the voteforPoll function.
This function takes choiceContent as a parameter.At first it tries to find pollid of current poll,choiceid of current choice and userid of voter.
Then it executes a *INSERT* SQL command for inserting this vote to the VOTES tables.

.. code-block:: python

     def voteforPoll(self,choiceContent):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT POLLID FROM POLLS WHERE CREATORID=%s AND POLLQUESTION =%s """,(self.creatorid,self.question))
        temp=cursor.fetchone()
        pollid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        cursor.execute("""SELECT CHOICEID FROM CHOICES WHERE CONTENT=%s AND POLLID =%s """,(choiceContent,pollid))
        temp=cursor.fetchone()
        choiceid=temp[0]
        cursor.close()
        cursor=connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""INSERT INTO VOTES (POLLID,CHOICEID,USERID) VALUES (%s,%s,%s)""",(pollid,choiceid,userid))
        cursor.execute("""UPDATE CHOICES SET NUMBEROFVOTES=NUMBEROFVOTES+1 WHERE CHOICEID=%s""",(choiceid,))
        connection.commit()
        cursor.close()
        connection.close()

LIKES Table and Operations (Auxiliary Table)
--------------------------------------------
In this application users can like each other's posts. This action is implemented by LIKES table operations.
LIKES Table holds the data of liked tweets.

This table has following columns

* *USERID* as integer and not null references userprofile table
      Holds the id of the user who liked the tweet
* *TWEETID* as integer and not null references tweets table
      Holds the id of the tweet which is liked by the user.
* *LikeTime* as integer and not null default current_timestamp
      Holds the time of the like action.

*USERID* and *TWEETID* act as a primary key together.
Operations of LIKES table are implemented in likeoperations.py file.

*Like A Tweet*
^^^^^^^^^^^^^^
A user can like someone's tweet with like function. This function will take only tweetid as a parameter. Firstly, it tries to find the id of current user.
Then it executes a simple INSERT SQL command. Then it updates the TWEETS and USERPROFILE table for LIKE stats.

.. code-block:: python

   def like(tweetid):
    try:
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""INSERT INTO LIKES (USERID,TWEETID) VALUES(%s,%s)""",(userid,tweetid))
        cursor.execute("""UPDATE TWEETS SET NUMBEROFLIKES=NUMBEROFLIKES + 1 WHERE TWEETID=%s""",(tweetid,))
        cursor.execute("""UPDATE USERPROFILE SET LIKES=LIKES + 1 WHERE ID=%s""",(userid,))
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    except:
        return 0

*Unlike a Tweet*
^^^^^^^^^^^^^^^^
Unliking a tweet is similar to liking a tweet. We can do this action with unlike function. It also takes only tweetid as a parameter.Then it tries to find
the id of current user. Then it executes a DELETE SQL command and makes update for USERPROFILE and TWEETS table.

.. code-block:: python

   def unlike(tweetid):
    try:
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(current_user.username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""DELETE FROM LIKES WHERE USERID=%s AND TWEETID=%s""",(userid,tweetid))
        cursor.execute("""UPDATE TWEETS SET NUMBEROFLIKES=NUMBEROFLIKES - 1 WHERE TWEETID=%s""",(tweetid,))
        cursor.execute("""UPDATE USERPROFILE SET LIKES=LIKES - 1 WHERE ID=%s""",(userid,))
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    except:
        return 0
