# -*- coding: utf-8 -*-
import datetime
import os
import json
import re
import psycopg2 as dbapi2
import math

from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_login import LoginManager
from flask_login import current_user, login_required, login_user, logout_user
from passlib.apps import custom_app_context as pwd_context
from twitlist import *
from twit import *
from message import Message
from media import Media
from tag import Tag
from tagList import TagList
from quizList import QuizList
from messageList import MessageList
from mediaList import MediaList
from list import List
from listoflist import ListOfLists
from flask import current_app, request
from user import *
from applications import *
from forms import *
from followoperations import *
from usersettings import *
from notifications import *
from poll import Poll
from listofpolls import ListOfPolls
from likeoperations import *
from credit import *
from creditlist import *
from rtoperations import *
from bug import *
from buglist import *

lm = LoginManager()
app = Flask(__name__)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
            dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)

def create_app():
    app.config.from_object('settings')

    app.Buglist = Buglist()
    app.Twitlist = Twitlist()
    app.Creditlist = Creditlist()
    app.messageList = MessageList()
    app.mediaList = MediaList()
    app.tagList = TagList()
    app.quizList = QuizList()

    lm.init_app(app)
    lm.login_view='login_page'

    return app


@app.route('/')
def root_page():
    return redirect(url_for('home_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        user = get_user(username)
        if user is not None:
            password = form.password.data
            if pwd_context.verify(password, user.password):
                login_user(user)
                flash('You have logged in.')
                next_page = request.args.get('next', url_for('home_page'))
                return redirect(next_page)
        flash('Invalid credentials.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = pwd_context.encrypt(form.password.data)
        try:
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO USERS (USERNAME, PASSWORD) VALUES (%s, %s)""", (username, password))

            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    userid = get_userid(username)
                    cursor.execute("""INSERT INTO USERPROFILE (ID, NICKNAME, USERNAME, BIO) VALUES(%s, %s, %s, %s)""", (userid, username, username, 'bio'))
                    cursor.execute("""INSERT INTO USERINFO (USERID, NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(%s, %s, %s, %s, %s, %s)""",
                                   (userid, '', '', '', '', ''))
                    cursor.execute("""INSERT INTO POINTS (USERID) VALUES(%s)""", (userid,))
                    login_user(get_user(username))
                    return redirect(url_for('home_page'))
        except:
            flash('Username is already taken')

    return render_template('register.html', form=form)

@app.route('/profile/<usrhandle>', methods=['GET'])
@login_required
def profile_page(usrhandle):
    if request.method == 'GET':
        twits = current_app.Twitlist.get_elsetwits(usrhandle)

    return render_template('profile.html', twits=twits)

@app.route('/home', methods=['GET'])
@login_required
def home_page():
    current_user.activetab = 0
    now = datetime.datetime.now()
    if    request.method == 'GET':
        now = datetime.datetime.now()
        twits = current_app.Twitlist.get_hometwit()
        return render_template('home.html', username=request.args.get('username'), twits=twits,  current_time=now.ctime())

@app.route('/404', methods=['GET'])
@login_required
def error_page():
    now = datetime.datetime.now()
    if    request.method == 'GET':
        return render_template('error.html')


@app.route('/twits/<int:twit_id>/link', methods=['GET', 'POST'])
@login_required
def links_page(twit_id):
    current_user.activetab = 1
    ids=0;
    id_twit=twit_id
    holderid=current_app.Twitlist.getownerid(twit_id)
    cduserid=current_app.Twitlist.getid()
    guest=0;
    if holderid == cduserid:
        guest=0;
    else:
        guest=1;

    if request.method == 'GET':

        if guest==1:
            links = current_app.Twitlist.get_link(twit_id)
            return render_template('glink.html', links=links)

        else:
            links = current_app.Twitlist.get_link(twit_id)
            return render_template('link.html', links=links)

    else:
        if request.form['submit'] == "updatelink":
            ids=request.form['sbutton']
            contextl=request.form['linked']

            if contextl == '':
               contextl = "Dont Leave This Space Empty UPD"

            links= Link(ids, contextl, twit_id)
            current_app.Twitlist.update_link(linkid, links)
            return redirect(url_for('links_page', twit_id=twit_id))

        elif request.form['submit'] == "addlink":
            contextl=request.form['linked']
            if contextl == '':
               contextl = "Dont Leave This Space Empty ADD"

            links=Link(ids, contextl, twit_id)
            current_app.Twitlist.add_link(id_twit, links)
            return redirect(url_for('links_page', twit_id=twit_id))

        elif request.form['submit'] == "deletelink":
            ids=request.form['sbutton']
            current_app.Twitlist.delete_link(ids)
            return redirect(url_for('links_page', twit_id=twit_id))


@app.route('/bugreport', methods=['GET', 'POST'])
@login_required
def bugs_page():
    current_user.activetab=16
    if request.method == 'GET':
        usrid=current_app.Buglist.getid()
        adminid=current_app.Buglist.getadmin()

        if usrid==adminid:
            bugs = current_app.Buglist.get_bugs()
            return render_template('bugspageadmin.html', bugs=bugs)

        else:
            return render_template('bugspageusr.html')

    else:
        bugid = 0
        bugcs = request.form['bugcs']
        usrid=current_app.Buglist.getid()
        focus = 0
        fixed = 0
        bug = Bug(bugid, bugcs, usrid, focus, fixed)
        current_app.Buglist.add_bug(bug)
        flash("Thanks For Helping Us")
        flash("Your Report Is Added To Our Issues Que")
        return redirect(url_for('bugs_page'))

@app.route('/bugreport/adminonly/<int:bug_id>', methods=['GET', 'POST'])
@login_required
def bug_page(bug_id):
    bugid=bug_id
    usrid=current_app.Buglist.getid()
    adminid=current_app.Buglist.getadmin()

    if request.method == 'GET':

        if usrid==adminid:
            bugs = current_app.Buglist.get_bug(bugid)
            return render_template('bugpage.html', bug=bugs)

        else:
            return redirect(url_for('bugs_page'))

    else:
        postres=request.form['submit']

        if postres == 'delete':
            current_app.Buglist.delete_bug(bugid)

        elif postres == 'setfocus':
            current_app.Buglist.set_focus(bugid)

        elif postres == 'defocus':
            current_app.Buglist.defocus(bugid)

        elif postres == 'setfixed':
            current_app.Buglist.setfixed(bugid)

        return redirect(url_for('bug_page', bug_id=bugid))


@app.route('/twits/<int:twit_id>', methods=['GET', 'POST'])
@login_required
def twits_page(twit_id):
    current_user.activetab = 1
    id_twit=twit_id
    holderid=current_app.Twitlist.getownerid(twit_id)
    cduserid=current_app.Twitlist.getid()
    guest=0;
    if holderid == cduserid:
        guest=0;
    else:
        guest=1;

    if request.method == 'GET':
        twit = current_app.Twitlist.get_twit(twit_id)
        isTweetLiked=isLiked(current_user.username,twit_id)
        if twit==None:
            return(redirect(url_for('error_page')))

        if guest == 1:
            return render_template('gtwit.html', twits=twit,isTweetLiked=isTweetLiked)

        else:
            return render_template('twit.html', twits=twit,isTweetLiked=isTweetLiked)
    else:

        if request.form['submit'] == 'delete':
            current_app.Twitlist.delete_linktw(id_twit)
            current_app.Twitlist.delete_twit(id_twit)
            return redirect(url_for('home_page'))

        elif request.form['submit'] == 'update':
            title=request.form['title']
            context=request.form['context']

            if title == '':
                title = "IDont Like Emptyness"

            if context == '':
               context = "Dont Leave This Space Empty Too"

            twit = current_app.Twitlist.get_twit(twit_id)
            numlike=twit.numberoflikes
            numrt=twit.numberofrts
            isrt=0
            rtowner=0
            twits = Twit(title, context, id_twit, current_user.username, numlike, numrt, isrt, rtowner)
            current_app.Twitlist.update_twit(id_twit, twits)
            return redirect(url_for('twits_page', twit_id=id_twit))

        elif request.form['submit']=='liketweet':
            isTweetLiked=like(twit_id)
            if isTweetLiked:
                flash("Tweet is liked")
            else:
                flash("Tweet can not be liked")

            twit = current_app.Twitlist.get_twit(twit_id)
            return render_template('gtwit.html',twits=twit,isTweetLiked=isTweetLiked)
        elif request.form['submit']=='unliketweet':

            isTweetUnliked=unlike(twit_id)
            if isTweetUnliked:
                flash("Tweet is unliked")
            else:
                flash("Tweet can not be unliked")

            twit = current_app.Twitlist.get_twit(twit_id)
            isTweetLiked=isLiked(current_user.username,twit_id)
            return render_template('gtwit.html',twits=twit,isTweetLiked=isTweetLiked)
        elif request.form['submit']=='retweet':
            RT(twit_id)
            twit = current_app.Twitlist.get_twit(twit_id)
            isTweetLiked=isLiked(current_user.username,twit_id)
            return render_template('gtwit.html',twits=twit,isTweetLiked=isTweetLiked)
@app.route('/twits', methods=['GET', 'POST'])
@login_required
def twit_page():
    current_user.activetab = 1
    if request.method == 'GET':
        now = datetime.datetime.now()
        twits = current_app.Twitlist.get_twits()
        return render_template('twits.html', twits=twits)

    else:
        title = request.form['title']
        content = request.form['content']
        twitid=0
        userh="NONE"
        numlike=0
        numrt=0
        isrt=0
        rtowner=0
        twit = Twit(title, content, twitid, userh, numlike, numrt, isrt, rtowner)
        current_app.Twitlist.add_twit(twit)
        return redirect(url_for('twit_page'))

@app.route('/credits', methods=['GET', 'POST'])
@login_required
def credit_page():
    current_user.activetab = 14
    if request.method == 'GET':
        now = datetime.datetime.now()
        credit = current_app.Creditlist.get_credit()
        return render_template('credit.html', credits=credit)

    else:
        credits = current_app.Creditlist.get_credit()

        value = request.form['value']
        holder = request.form['holder']
        cardid = request.form['cardid']
        expmon = request.form['expmon']
        expyear = request.form['expyear']
        cvv = request.form['cvv']
        credik=Credit(value, holder, cardid, expmon, expyear, cvv)
        current_app.Creditlist.add_credit(credik)
        cred = current_app.Creditlist.get_credit()
        return render_template('credit.html', credits=cred)

@app.route('/followuser', methods=['GET', 'POST'])
@login_required
def follow_page():
    current_user.activetab = 2
    if request.method == 'POST':
        username = request.form['selecteduser']
        nickname = get_nickname(username)
        if username == '':
            flash('Please select a user')
        elif request.form['followbutton']=='Follow':
            if follow(username):
                flash('%s is followed. %s is followed by %s user(s). You are following %s user(s).'
                      % (nickname, nickname, get_followercount(username), get_followingcount(current_user.username)))
            else:
                flash('%s cannot be followed' % nickname)
        else:
            if unfollow(username):
                flash('%s is unfollowed. %s is followed by %s user(s). You are following %s user(s).'
                      % (nickname, nickname, get_followercount(username), get_followingcount(current_user.username)))
            else:
                flash('%s cannot be unfollowed' % nickname)
        return redirect(url_for('follow_page'))
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT USERNAME, NICKNAME FROM USERPROFILE""")
                users=cursor.fetchall()
            with connection.cursor() as cursor2:
                cursor2.execute("""SELECT USERNAME, NICKNAME FROM FOLLOWS INNER JOIN USERPROFILE ON FOLLOWEDUSER=ID WHERE FOLLOWERID=%s""",(get_userid(current_user.username),))
                followedusers = cursor2.fetchall()
            with connection.cursor() as cursor3:
                cursor3.execute("""SELECT USERNAME, NICKNAME FROM FOLLOWS INNER JOIN USERPROFILE ON FOLLOWERID=ID WHERE FOLLOWEDUSER=%s""",(get_userid(current_user.username),))
                followers = cursor3.fetchall()
            with connection.cursor() as cursor4:
                cursor4.execute("""SELECT USERNAME FROM FOLLOWS INNER JOIN USERPROFILE ON FOLLOWEDUSER=ID WHERE FOLLOWERID=%s""",(get_userid(current_user.username),))
                followedusernames = cursor4.fetchall()

        return render_template('followuser.html', users=users, followedusers=followedusers, followers=followers, followedusernames=followedusernames)

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages_page():
    current_user.activetab = 3
    messages = current_app.messageList.get_messages()
    if request.method == 'POST':
        value = request.form.getlist('message')
        for i in value:
            current_app.messageList.delete_message(i)
        return redirect(url_for('messages_page'))
    return render_template('messages.html', messages=messages)


@app.route('/newmessage', methods=['GET', 'POST'])
@login_required
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

@app.route('/media', methods=['GET', 'POST'])
@login_required
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

@app.route('/newphoto', methods=['GET', 'POST'])
@login_required
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

@app.route('/updatemedia', methods=['GET', 'POST'])
@login_required
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

@app.route('/tagphoto', methods=['GET', 'POST'])
@login_required
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

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
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

@app.route('/sendquestion', methods=['GET', 'POST'])
@login_required
def sendquestion_page():
    current_user.activetab = 5
    users = None
    if request.method == 'POST':
        reciever = request.form['reciever']
        content = request.form['question']
        value = request.form.getlist('options')
        options = []
        options += [(request.form['option1'])]
        options += [(request.form['option2'])]
        options += [(request.form['option3'])]
        options += [(request.form['option4'])]
        for i in value:
            current_app.quizList.add_quiz(reciever, options,content, i)
    with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT USERNAME FROM USERS""")
                users = cursor.fetchall()
    return render_template('sendquestion.html', users = users)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    current_user.activetab = 7
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

@app.route('/notifications',methods=['GET','POST'])
@login_required
def notifs_page():
    current_user.activetab = 9
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


@app.route('/list/owner/<string:listname>',methods=['GET','POST'])
@login_required
def list_page_of_creator(listname):
    current_user.activetab = 6
    if request.method=='POST':
            if request.form['submit']=='update':
                newlistname=request.form['listname']
                list= List(listname,current_user.username)
                list.updateName(newlistname)
                tweets=list.getTweets()
                return redirect(url_for('list_page_of_creator',listname=newlistname))
            if request.form['submit']=='delete':
                app.templistoflist=ListOfLists('temp')
                app.templistoflist.deleteList(listname,current_user.username)
                createdlist=app.templistoflist.getCreatedLists()
                return redirect(url_for('subscribelists_page'))
            if request.form['submit']=='insider':
                insidername=request.form['listname']
                list=List(listname,current_user.username)
                isInsiderAdded=list.addInsider(insidername)
                tweets=list.getTweets()
                if isInsiderAdded==1:
                    flash('%s is added in to the list as a insider' % insidername)
                else:
                    flash('User can not be added to the list as a insider')
            return redirect(url_for('list_page_of_creator',listname=listname))

    else:
        list=List(listname,current_user.username)
        tweets=list.getTweets()
        return render_template('listownerperspective.html',listname=listname,tweets=tweets)

@app.route('/list/<string:listname>',methods=['GET','POST'])
@login_required
def list_page_of_subscriber(listname):
    current_user.activetab = 6
    if request.method=='POST':
            if request.form['submit']=='unsubscribe':
                app.templistoflist=ListOfLists('temp')
                templist=app.templistoflist.getList(listname)
                templist.deleteSubscriber(current_user.username)

            if request.form['submit']=='subscribe':
                app.templistoflist=ListOfLists('temp')
                templist=app.templistoflist.getList(listname)
                templist.addSubscriber(current_user.username)

            return redirect(url_for('subscribelists_page'))

    else:
        app.templistoflist=ListOfLists('temp')
        templist=app.templistoflist.getList(listname)
        isSubscriber=templist.isSubscriber(current_user.username)
        tweets=templist.getTweets()
        return render_template('listsubscriberperspective.html',listname=listname,isSubscriber=isSubscriber,tweets=tweets)


@app.route('/subscribedlists',methods=['GET','POST'])
@login_required
def subscribelists_page():
    current_user.activetab = 6
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.subscribedList.addList(List(listname,current_user.username))
            subscribedlist=app.subscribedList.getSubscribeLists()
        return redirect(url_for('subscribelists_page'))
    else:
            app.subscribedList=ListOfLists('Subscribed to')
            subscribedlist=app.subscribedList.getSubscribeLists()
            return render_template('subscribedlists.html',subscribedlist=subscribedlist)


@app.route('/memberoflists',methods=['GET','POST'])
@login_required
def memberoflists_page():
    current_user.activetab = 6
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.memberOfList.addList(List(listname,current_user.username))
            memberlist=app.memberOfList.getInsiderLists()
        return redirect(url_for('memberoflists_page'))
    else:
            app.memberOfList=ListOfLists('memberOfList')
            memberoflist=app.memberOfList.getInsiderLists()
            return render_template('memberoflist.html',memberoflist=memberoflist)

@app.route('/createdlists',methods=['GET','POST'])
@login_required
def createdlists_page():
    current_user.activetab = 6
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.createdLists.addList(List(listname,current_user.username))
            createdlist=app.createdLists.getCreatedLists()
        return redirect(url_for('createdlists_page'))
    else:
            app.createdLists=ListOfLists('CreatedLists')
            createdlist=app.createdLists.getCreatedLists()
            return render_template('createdlists.html',createdlist=createdlist)

@app.route('/polls',methods=['GET','POST'])
@login_required
def polls_page():
    current_user.activetab = 10
    if request.method=='POST':
        if request.form['submit']=='add':
            pollquestion=request.form['pollname']
            app.polls=ListOfPolls('polls')
            temppoll=Poll(pollquestion,current_user.username)
            app.polls.addPoll(temppoll)
            polllist=app.polls.getAllPolls()

        return redirect(url_for('polls_page'))

    else:
        app.polls=ListOfPolls('polls')
        polllist=app.polls.getAllPolls()
        return render_template('polls.html',polllist=polllist)


@app.route('/poll/<string:creatorname>/<string:pollquestion>',methods=['GET','POST'])
@login_required
def poll_page(pollquestion,creatorname):
    current_user.activetab = 10
    if request.method=='POST':
        if request.form['submit']=='update':
            current_app.tempPollList=ListOfPolls('temp')
            poll=current_app.tempPollList.getPoll(pollquestion,creatorname)
            newquestion=request.form['choiceorquestion']
            poll.updateQuestion(newquestion)
            choices=poll.getChoices()
            isVoted=poll.isVoted(current_user.username)
            return redirect(url_for('poll_page',pollquestion=newquestion,creatorname=creatorname))
        elif request.form['submit']=='delete':
            app.polls=ListOfPolls('polls')
            polllist=app.polls.getAllPolls()
            app.polls.deletePoll(pollquestion,creatorname)
            return redirect(url_for('polls_page'))
        elif request.form['submit']=='addchoice':
            current_app.tempPollList=ListOfPolls('temp')
            poll=current_app.tempPollList.getPoll(pollquestion,creatorname)
            choiceinfo=request.form['choiceorquestion']
            poll.addChoice(choiceinfo)
            choices=poll.getChoices()
            isVoted=poll.isVoted(current_user.username)
        elif request.form['submit']=='vote':
            current_app.tempPollList=ListOfPolls('temp')
            poll=current_app.tempPollList.getPoll(pollquestion,creatorname)
            choiceContent=request.form['answer']
            poll.voteforPoll(choiceContent)
            choices=poll.getChoices()
            isVoted=poll.isVoted(current_user.username)


        return redirect(url_for('poll_page',pollquestion=pollquestion,creatorname=creatorname))



    else:
        current_app.templist=ListOfPolls('temp')
        poll=current_app.templist.getPoll(pollquestion,creatorname)
        choices=poll.getChoices()
        isVoted=poll.isVoted(current_user.username)
        counter=0
        if (creatorname==current_user.username):
            return render_template('pollownerperspective.html',pollquestion=pollquestion,choices=choices,isVoted=isVoted,counter=counter)
        else:
            return render_template('pollvoterperspective.html',pollquestion=pollquestion,choices=choices,isVoted=isVoted,counter=counter)

@app.route('/Likes/<string:username>')
@login_required
def likes_page(username):
        current_user.activetab = 11
        likedTweets=getLikedTweets(username)
        return render_template('like.html',likedTweets=likedTweets)

@app.route('/managegifts', methods=['GET','POST'])
@login_required
def admin_managegifts():
    current_user.activetab = 15
    if not current_user.is_admin:
        abort(401)
    addform = AddGiftForm(request.form)
    updateform = UpdateGiftForm(request.form)
    updateform.gifts.choices=[]
    description = ''
    if request.method == 'POST':
        if request.form['btn'] == 'add':
            if addform.validate():
                giftname = addform.giftname.data
                description = addform.description.data
                with dbapi2.connect(app.config['dsn']) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""INSERT INTO GIFTS (GIFTNAME, DESCRIPTION) VALUES (%s,%s)""", (giftname,description))
                return redirect(url_for('admin_managegifts'))
        elif request.form['btn'] == 'delete':
            giftname = updateform.gifts.data
            with dbapi2.connect(app.config['dsn']) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""DELETE FROM GIFTS WHERE GIFTNAME=%s""",(giftname,))
            return redirect(url_for('admin_managegifts'))
        elif request.form['btn'] == 'update':
            giftname = updateform.gifts.data
            description = updateform.description.data
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE GIFTS SET DESCRIPTION=%s WHERE GIFTNAME=%s""",(description,giftname))
            return redirect(url_for('admin_managegifts'))
        elif request.form['btn'] == 'getinfo':
            giftname = updateform.gifts.data
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT DESCRIPTION FROM GIFTS WHERE GIFTNAME=%s""",(giftname,))
                    description = cursor.fetchone()[0]

    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT GIFTNAME FROM GIFTS""")
            gifts=cursor.fetchall()
    for (giftname,) in gifts:
        updateform.gifts.choices+=[(giftname,giftname)]
    return render_template('managegifts.html', addform=addform, updateform=updateform, description=description)

@app.route('/gifts', methods=['GET','POST'])
@login_required
def gifts():
    current_user.activetab = 13
    sendform = SendGiftForm(request.form)
    sendform.gifts.choices=[]
    sendform.sendto.choices=[]
    sentgifts = []
    if request.method == 'POST':
        if request.form['btn'] == 'delete':
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""DELETE FROM SENTGIFTS WHERE RECEIVER = %s OR SENDER = %s""",(get_userid(current_user.username),get_userid(current_user.username)))
            flash('All gifts deleted.')
        else:
            try:
                with dbapi2.connect(app.config['dsn']) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""INSERT INTO SENTGIFTS VALUES(%s,%s,%s)""",(get_userid(current_user.username),sendform.sendto.data,sendform.gifts.data))
                        cursor.execute("""SELECT USERNAME FROM USERS WHERE ID=%s""",sendform.sendto.data)
                        sentto = cursor.fetchone()[0]
                        cursor.execute("""SELECT GIFTNAME, DESCRIPTION FROM GIFTS WHERE ID=%s""",(sendform.gifts.data,))
                        values = cursor.fetchall()
                        sentgift = None
                        description = None
                        for i,j in values:
                            sentgift = i
                            description = j
                        flash("Gift '%s' has sent to '%s'. Gift description: %s" % (sentgift, get_nickname(sentto), description))
            except:
                flash('You cannot send the same gift to the same person more than once')
        return redirect(url_for('gifts'))
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT ID, GIFTNAME FROM GIFTS""")
                gifts=cursor.fetchall()
            with connection.cursor() as cursor2:
                cursor2.execute("""SELECT ID, NICKNAME FROM USERPROFILE""")
                users=cursor2.fetchall()
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
        for (id,giftname) in gifts:
            sendform.gifts.choices+=[(id,giftname)]
        for (id,username) in users:
            sendform.sendto.choices+=[(id,username)]

    return render_template('gifts.html', sendform = sendform, receivedgifts=receivedgifts, sentgifts=sentgifts)

@app.route('/adminpanel')
@login_required
def adminpanel():
    current_user.activetab = 15
    if not current_user.is_admin:
        abort(401)
    return render_template('adminpanel.html')

@app.route('/deleteuser', methods=['GET','POST'])
@login_required
def deleteuser():
    current_user.activetab = 15
    if not current_user.is_admin:
        abort(401)
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                username=request.form['selecteduser']
                if username=='- Select user -':
                    flash('Please select a user to delete')
                else:
                    cursor.execute("""DELETE FROM USERS WHERE USERNAME=%s""",(username,))
                    flash("User '%s' is deleted." % get_nickname(username))
        return redirect(url_for('deleteuser'))
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT USERNAME, NICKNAME FROM USERPROFILE""")
                users=cursor.fetchall()
        return render_template('deleteuser.html', users=users)

@app.route('/manageapps', methods = ['GET','POST'])
@login_required
def admin_manageapps():
    current_user.activetab = 15
    if not current_user.is_admin:
        abort(401)
    form = AddAppForm(request.form)
    form2 = UpdateAppForm(request.form)
    form3 = UpdateAppForm(request.form)
    form2.activeapps.choices=[]
    form3.deactiveapps.choices=[]
    if request.method == 'POST':
        if request.form['btn'] == 'add' or request.form['btn'] == 'add_act':
            if form.validate():
                appname = form.appname.data
                with dbapi2.connect(app.config['dsn']) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""INSERT INTO APPS (APPNAME) VALUES (%s)""", (appname,))
                        if request.form['btn'] == 'add_act':
                            cursor.execute("""UPDATE APPS SET ACTIVE=TRUE WHERE APPNAME=(%s)""", (appname,))
            else:
                flash('App name cannot be empty')
        elif request.form['btn'] == 'update' or request.form['btn'] == 'update2':
            appname = ''
            selection = ''
            if request.form['btn'] == 'update':
                appname = form2.activeapps.data
                selection = form2.activeradio.data
            else:
                appname = form3.deactiveapps.data
                selection = form3.deactiveradio.data
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    if selection == 'Delete':
                        cursor.execute("""DELETE FROM APPS WHERE APPNAME=(%s)""", (appname,))
                    if selection == 'Deactivate' or selection == 'Activate':
                        if selection == 'Deactivate':
                            cursor.execute("""UPDATE APPS SET ACTIVE=FALSE WHERE APPNAME=(%s)""", (appname,))
                        else:
                            cursor.execute("""UPDATE APPS SET ACTIVE=TRUE WHERE APPNAME=(%s)""", (appname,))

        return redirect(url_for('admin_manageapps'))
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT APPNAME FROM APPS WHERE ACTIVE=TRUE""")
                a_values=cursor.fetchall()
                cursor.execute("""SELECT APPNAME FROM APPS WHERE ACTIVE=FALSE""")
                d_values=cursor.fetchall()
        for (appname,) in a_values:
            form2.activeapps.choices+=[(appname,appname)]
        for (appname,) in d_values:
            form3.deactiveapps.choices+=[(appname,appname)]
    return render_template('manageapps.html', form=form, form2=form2, form3=form3)

@app.route('/appsettings', methods = ['GET', 'POST'])
@login_required
def user_manageapps():
    current_user.activetab = 12
    if request.method=='GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT APPNAME FROM APPS WHERE ACTIVE=TRUE""")
                values=cursor.fetchall()
                applications = getapplications()
                apps = []
                for (appname,) in applications:
                    apps += [appname]
    else:
        activeapps = request.form.getlist('selections')
        updateapps(activeapps)
        flash('Your application settings are updated.')
        return redirect(url_for('user_manageapps'))
    return render_template('appsettings.html', values=values, apps=apps)

@app.route('/updateprofile', methods= ['GET', 'POST'])
@login_required
def updateprofile_page():
    current_user.activetab = 8
    passForm=ChangePassForm(request.form)
    updateForm=UpdateProfileForm(request.form)
    if request.method=='POST':
        if request.form['btn'] == 'Change Password':
            if passForm.validate():
                password = pwd_context.encrypt(passForm.password.data)
                with dbapi2.connect(app.config['dsn']) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""UPDATE USERS SET PASSWORD=%s WHERE USERNAME=%s""", (password,current_user.username))
                flash('Your password has been changed.')
        else:
            if updateForm.validate():
                with dbapi2.connect(app.config['dsn']) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""UPDATE USERPROFILE SET NICKNAME=%s, BIO=%s WHERE USERNAME=%s""", (updateForm.nickname.data,updateForm.bio.data,current_user.username))
                flash('Your profile has been updated.')


    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT NICKNAME, BIO FROM USERPROFILE WHERE USERNAME=%s""", (current_user.username,))
            values = cursor.fetchall()
            for nickname,bio in values:
                updateForm.nickname.data = nickname
                updateForm.bio.data = bio

    return render_template('updateprofile.html', passForm=passForm, updateForm=updateForm)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have logged out.')
    return redirect(url_for('home_page'))

def main():
    app = create_app()
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant' host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)

@app.route('/initdb')
@login_required
def initialize_database():
    if not current_user.is_admin:
        abort(401)
    with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute(open("script.sql", "r").read())
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    main()
