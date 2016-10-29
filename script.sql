CREATE TABLE TWEETS(
	TWEETID SERIAL PRIMARY KEY NOT NULL,
	USERID INT NOT NULL,
	TITLE CHAR(20) NOT NULL,
	CONTEXT CHAR(140) NOT NULL
);

CREATE TABLE MESSAGES(
	MESSAGEID SERIAL PRIMARY KEY,
	SENDER VARCHAR(20),
	RECIEVER VARCHAR(20) NOT NULL,
	CONTENT VARCHAR(100) NOT NULL,
	SENT BOOLEAN DEFAULT FALSE
	);

INSERT INTO TWEETS (USERID, TITLE, CONTEXT) VALUES(
	1,
	'Admin Tweets',
	'First Tweet By Adminssss'
);

INSERT INTO MESSAGES(RECIEVER, CONTENT) VALUES(
	'Emre Cetiner',
	'Good afternoon'
	);


CREATE TABLE LISTS(
	LISTID SERIAL PRIMARY KEY,
	SUBSCRIBERS INTEGER DEFAULT 0,
	MEMBERS INTEGER DEFAULT 0,
	NAME VARCHAR(40) NOT NULL,
	CREATORID INTEGER NOT NULL
	);

INSERT INTO LISTS (NAME,CREATORID) VALUES(
	'First List',
	1);