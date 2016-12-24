Parts Implemented by Cem Karagöz
================================
In this project Tweet, TweetLink, and Bug entities are done by me.

**Tweet Entity:**

   TweetId (Primary Key)
   Userıd  (Foreign Key)
   Tıtle
   Context
   Twtime
   Numberoflikes
   NumberofRTs
   isRT
   RtownerID  (Foreign Key)


SQL Table:

.. code-block::   sql

   CREATE TABLE TWEETS(
   TWEETID SERIAL PRIMARY KEY NOT NULL,
   USERID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
   TITLE VARCHAR(20) NOT NULL,
   CONTEXT VARCHAR(140) NOT NULL,
   TWTIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   NUMBEROFLIKES INTEGER NOT NULL DEFAULT 0,
   NUMBEROFRTS INTEGER NOT NULL DEFAULT 0,
   isRT INTEGER DEFAULT 0,
   RTOwnerID INTEGER DEFAULT 1 REFERENCES USERPROFILE(ID) ON DELETE  CASCADE
   );


Pyton Class used to represent the tweet:

.. code-block::   python

   class Twit:
    def __init__(self, title, context, twitid, userhandle, numberoflikes, numberofrts, isrt, rtowner):
        self.title = title
        self.context = context
        self.twitid = twitid
        self.userhandle = userhandle
        self.numberoflikes = numberoflikes
        self.numberofrts = numberofrts
        self.isrt = isrt
        self.rtowner = rtowner


Python classes and functions are used to make connection between the browser and the database.

When users visit other users profile or tweets they will see a diffrent page so for identifying owner from other users i used getid which gives current userid
and get ownerid which returns tweets ownerid back.

.. code-block::   sql

        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        owner = cursor.fetchone()
        return usernum

        cursor.execute("""SELECT USERID FROM TWEETS WHERE TWEETID=%s""", (twitid,))
        owner = cursor.fetchone()
        return owner


There is several functions for getting tweets:

For a **single tweet** (get_twit(self, twitid)):

.. code-block::   sql

   cursor.execute("""SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.tweetid = %s""", [twitid],)


For your **Feed** page(get_hometwit(self)):

.. code-block::   sql

   cursor.execute("""  SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN follows ON follows.followeduser = tweets.userid
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE follows.followerid = %s AND tweets.isrt = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE tweets.userid = %s AND tweets.isrt = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN follows ON follows.followeduser = tweets.rtownerid
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE follows.followerid = %s AND tweets.isrt = %s
                            UNION
                            SELECT tweets.title,
                            tweets.context,
                            tweets.tweetid,
                            users.username,
                            tweets.numberoflikes,
                            tweets.numberofrts,
                            tweets.isrt,
                            userprofile.username AS rtowner
                            FROM tweets
                            RIGHT JOIN users ON users.id = tweets.userid
                            RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                            WHERE tweets.rtownerid = %s AND tweets.isrt = %s
                            ORDER BY TWEETID DESC; """, (userid, 0, userid, 0, userid, 1, userid, 1))


For your and every other user **Profile** page(get_elsetwits(self, usrhandle)):

.. code-block::   sql

   cursor.execute("""SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.userid = %s AND tweets.isrt = %s
                        UNION
                        SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.rtownerid = %s AND tweets.isrt = %s
                        ORDER BY TWEETID DESC""", (userid, 0, userid, 1))


For your **Tweets** page(get_twits(self)):

.. code-block::   sql

   cursor.execute("""SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.userid = %s AND tweets.isrt = %s
                        UNION
                        SELECT tweets.title,
                        tweets.context,
                        tweets.tweetid,
                        users.username,
                        tweets.numberoflikes,
                        tweets.numberofrts,
                        tweets.isrt,
                        userprofile.username AS rtowner
                        FROM tweets
                        RIGHT JOIN users ON users.id = tweets.userid
                        RIGHT JOIN userprofile ON userprofile.id = tweets.rtownerid
                        WHERE tweets.rtownerid = %s AND tweets.isrt = %s
                        ORDER BY TWEETID DESC""", (userid, 0, userid, 1))


For adding new tweets(add_twit(self, twit)):

.. code-block::   sql

   cursor.execute("""INSERT INTO TWEETS (USERID, TITLE, CONTEXT)    VALUES    (%s, %s, %s)""", (userid, twit.title, twit.context))


For updating tweets(update_twit(self, twitid, twit)):

.. code-block::   sql

   cursor.execute("""UPDATE TWEETS SET TITLE=%s, CONTEXT=%s WHERE TWEETID=%s""", (twit.title, twit.context, twitid))


For deleting tweets(delete_twit(self, twitid)):

.. code-block::   sql

    cursor.execute("""DELETE FROM TWEETS WHERE TWEETID=%s""", [twitid],)


--------------------------------------------------------------------------


**TweetLink Entity**
   *TweetLId (Primary Key)
   *TweetId  (Foreign Key)
   *ContextL

SQL Table:

.. code-block::   sql

   CREATE TABLE TWEETLINK(
   TWEETLID SERIAL PRIMARY KEY NOT NULL,
   TWEETID INTEGER NOT NULL REFERENCES TWEETS(TWEETID),
   CONTEXTL VARCHAR(150) NOT NULL
   );


Pyton Class used to represent the tweetlink:

.. code-block::   python

   class Link:
        def __init__(self, tweetlid, contextl, twitid):
            self.tweetlid = tweetlid
            self.contextl = contextl
            self.twitid = twitid


Every tweet can have it own link to the outsite of the site or inside.

For getting links for tweet(get_link(self, twitid)):

.. code-block::   sql
        cursor.execute("""SELECT tweetlid, CONTEXTL, TWEETID  FROM TWEETLINK WHERE TWEETID=%s""", (twitid,))
        link = [(Link(tweetlid, contextl, tweetid))
                    for tweetlid, contextl, tweetid in cursor]


For adding links for tweet(add_link(self, twitid, link):

.. code-block::   sql
        cursor.execute("""INSERT INTO TWEETLINK (TWEETID, CONTEXTL)    VALUES    (%s, %s)""", (twitid, link.contextl))


For deleting links for tweet(def delete_link(self, tweetid)):

.. code-block::   sql
    :
        cursor.execute("""DELETE FROM TWEETLINK WHERE tweetid=%s""", [tweetid],)


For updating links for tweet(update_link(self, tweetid, contextl)):

.. code-block::   sql

        cursor.execute("""SELECT tweetlid FROM TWEETLINK WHERE TWEETID=%s
                          ORDER BY TWEETLID DESC""", (tweetid,))
        twitlid=cursor.fetchone()
        cursor.execute("""UPDATE TWEETLINK SET contextl=%s WHERE tweetlid=%s""", (contextl, twitlid))


--------------------------------------------------------------------------


**Bug Entity**
   *Userid  (Foreign Key)
   *Bugid (Primary Key)
   *BUGCAUSE
   *FOCUS
   *FIXED

SQL Table:

.. code-block::   sql

   CREATE TABLE BUGS(
   USERID INTEGER REFERENCES USERS ON DELETE CASCADE,
   BUGID SERIAL PRIMARY KEY,
   BUGCAUSE VARCHAR(80) NOT NULL,
   FOCUS INTEGER DEFAULT 0,
   FIXED INTEGER DEFAULT 0
   );


Pyton Class used to represent the Bugs:

.. code-block::   python

        class Bug:
        def __init__(self, bugid, bugcause, userid, focus, fixed):
            self.bugid = bugid
            self.bugcause = bugcause
            self.userid = userid
            self.focus = focus
            self.fixed = fixed


Bugs can only seen by admins but everyone can submit one.

Getting current userid(getid(self)):

.. code-block::   sql
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        usernum=cursor.fetchone()


Getting admin userid(getadmin(self)):

.. code-block::   sql
        name='admin'
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (name,))


Function below is code for one bug(get_bug(self, bugid)):

.. code-block::   sql
        cursor.execute("""SELECT
                        bugs.bugid,
                        bugs.bugcause,
                        users.username,
                        bugs.focus,
                        bugs.fixed
                        FROM BUGS
                        LEFT JOIN users ON users.id = bugs.userid
                        WHERE bugs.bugid=%s""", (bugid,))
        bugid, bugcause, username, focus, fixed=cursor.fetchone()
        bugs=Bug(bugid, bugcause, username, focus, fixed)


Same function but gets all bugs(get_bugs(self)):

.. code-block::   sql
        cursor.execute("""SELECT
                        bugs.bugid,
                        bugs.bugcause,
                        users.username,
                        bugs.focus,
                        bugs.fixed
                        FROM BUGS
                        LEFT JOIN users ON users.id = bugs.userid
                        ORDER BY focus DESC, bugs.bugid DESC """)
        bugs = [(Bug(bugid, bugcause, username, focus, fixed))
                    for bugid, bugcause, username, focus, fixed  in cursor]
        return bugs


Adding bugs to the system(add_bug(self, bug)):

.. code-block::   sql
        cursor.execute("""INSERT INTO BUGS (bugcause, userid)
        VALUES    (%s, %s)""",  (bug.bugcause, bug.userid))


Since ever bug has three stages Normal, Focused and fixed admin can set thoose stages.

Setting Focus On a Bug(set_focus(self, bugid)):

.. code-block::   sql
        cursor.execute("""UPDATE BUGS SET FOCUS=%s WHERE bugid=%s""", (1, bugid))


DeFocus On a Bug(defocus(self, bugid)):

.. code-block::   sql
        cursor.execute("""UPDATE BUGS SET FOCUS=%s WHERE bugid=%s""", (0, bugid))


Setting Fixed a Bug(setfixed(self, bugid)):
.. code-block::   sql
    def :
        cursor.execute("""UPDATE BUGS SET FIXED=%s WHERE bugid=%s""", (1, bugid))
