# -*- coding: utf-8 -*-
import datetime
import os
import json
import re
import psycopg2 as dbapi2

from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_login import LoginManager
from flask_login import current_user, login_required, login_user, logout_user
from passlib.apps import custom_app_context as pwd_context
from twitlist import Twitlist
from twit import Twit
from message import Message
from media import Media
from messageList import MessageList
from mediaList import MediaList
from list import List
from listoflist import ListOfLists
from flask import current_app, request
from user import get_user, get_userid
from applications import *
from forms import *
from followoperations import *
from usersettings import *
from notifications import *
from poll import Poll
from listofpolls import ListOfPolls


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

    app.Twitlist = Twitlist()

    app.messageList = MessageList()

    app.mediaList = MediaList()

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
                    login_user(get_user(username))
                    return redirect(url_for('home_page'))
        except:
            flash('Username is already taken')

    return render_template('register.html', form=form)


@app.route('/home', methods=['GET'])
@login_required
def home_page():
    now = datetime.datetime.now()
    if    request.method == 'GET':
        return render_template('home.html', username=request.args.get('username'), current_time=now.ctime())

@app.route('/twits/<int:twit_id>', methods=['GET', 'POST'])
@login_required
def twits_page(twit_id):
    if request.method == 'GET':
        twits = current_app.Twitlist.get_twit(twit_id)
        return render_template('twit.html', twits=twits)
    else:
        if request.form['submit'] == 'delete':
            tweetid=request.form['tweetid']
            current_app.Twitlist.delete_twit(tweetid)
            return redirect(url_for('home_page'))

        elif request.form['submit'] == 'update':
            tweetid=request.form['tweetid']
            title=request.form['title']
            context=request.form['context']
            twits = Twit(title, context, tweetid)
            current_app.Twitlist.update_twit(tweetid, twits)

        elif request.form['submit'] == 'addlink':
            tweetid=request.form['tweetid']
            linked=request.form['linked']
            current_app.Twitlist.add_link(tweetid, linked)
            return redirect(url_for('home_page'))

        elif request.form['submit'] == 'updatelink':
            tweetid=request.form['tweetid']
            linked=request.form['linked']
            current_app.Twitlist.update_link(tweetid, linked)
            return redirect(url_for('home_page'))

        elif request.form['submit'] == 'deletelink':
            tweetid=request.form['tweetid']
            current_app.Twitlist.delete_link(tweetid)
            return redirect(url_for('home_page'))





            return redirect(url_for('home_page'))

@app.route('/twits')
@login_required
def twit_page():
    now = datetime.datetime.now()
    twits = current_app.Twitlist.get_twits()
    return render_template('twits.html', twits=twits)

@app.route('/twits/add', methods=['GET', 'POST'])
@login_required
def twit_add_page():
    if request.method == 'GET':
        return render_template('add_twit.html')
    else:
        title = request.form['title']
        content = request.form['content']
        twitid=0
        twit = Twit(title, content, twitid)
        current_app.Twitlist.add_twit(twit)
        return render_template('add_twit.html')

@app.route('/followuser', methods=['GET', 'POST'])
@login_required
def follow_page():
    if request.method == 'POST':
        username = request.form['follow-username']
        if request.form['followbutton']=='Follow':
            if follow(username):
                flash('%s is followed. %s is followed by %s user(s). You are following %s user(s).'
                      % (username, username, get_followercount(username), get_followingcount(current_user.username)))
            else:
                flash('%s cannot be followed' % username)
        else:
            if unfollow(username):
                flash('%s is unfollowed. %s is followed by %s user(s). You are following %s user(s).'
                      % (username, username, get_followercount(username), get_followingcount(current_user.username)))
            else:
                flash('%s cannot be unfollowed' % username)
        return render_template('followuser.html')
    else:
        return render_template('followuser.html')

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages_page():
    messages = current_app.messageList.get_messages()
    if request.method == 'POST':
        value = request.form.getlist('message')
        for i in value:
            current_app.messageList.delete_message(i)
    return render_template('messages.html', messages=messages)


@app.route('/message', methods=['GET', 'POST'])
@login_required
def message_page():
    message = current_app.messageList.get_message()
    if request.method == 'POST':
        content = request.form['content']
        sender = 1
        reciever = current_user.username
        sent = True
        messagesend = Message(sender, reciever, content, sent)
        current_app.messageList.add_message(messagesend)
    return render_template('message.html', message=message)

@app.route('/newmessage', methods=['GET', 'POST'])
@login_required
def new_message_page():
    if request.method == 'POST':
        content = request.form['content']
        sender = 1
        reciever = request.form['reciever']
        sent = True
        messagesend = Message(sender, reciever, content, sent)
        current_app.messageList.add_message(messagesend)
    return render_template('new_message.html')

@app.route('/media', methods=['GET', 'POST'])
@login_required
def media_page():
    media = current_app.mediaList.get_photos()
    if request.method == 'POST':
        if request.form['operation'] == 'delete':
            value = request.form.getlist('media')
            for i in value:
                current_app.mediaList.delete_photo(i)
            return redirect(url_for('media_page'))
        if request.form['operation'] == 'update':
            print('avel')
            value = request.form.getlist('media')
            print(value)
    return render_template('media.html', media = media)

@app.route('/newphoto', methods=['GET', 'POST'])
@login_required
def newphoto_page():
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
    media = current_app.mediaList.get_photos()
    if request.method == 'POST':
        value = request.form.getlist('media')
        description = request.form['newdes']
        print(value)
        print(description)
        for i in value:
                current_app.mediaList.update_photo(description,i)
        return redirect(url_for('media_page'))
    return render_template('updatemedia.html', media = media)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
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

@app.route('/notifications',methods=['GET','POST'])
@login_required
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


@app.route('/list/owner/<string:listname>',methods=['GET','POST'])
@login_required
def list_page_of_creator(listname):
    if request.method=='POST':
            if request.form['submit']=='update':
                newlistname=request.form['listname']
                list= List(listname,current_user.username)
                list.updateName(newlistname)
                return render_template('listownerperspective.html',listname=newlistname)
            if request.form['submit']=='delete':
                app.templistoflist=ListOfLists('temp')
                app.templistoflist.deleteList(listname,current_user.username)
                createdlist=app.templistoflist.getCreatedLists()
                return redirect(url_for('subscribelists_page'))
            if request.form['submit']=='insider':
                insidername=request.form['listname']
                list=List(listname,current_user.username)
                list.addInsider(insidername)
                return render_template('listownerperspective.html',listname=listname)
    else:
        return render_template('listownerperspective.html',listname=listname)

@app.route('/list/<string:listname>',methods=['GET','POST'])
@login_required
def list_page_of_subscriber(listname):
    if request.method=='POST':
            if request.form['submit']=='unsubscribe':
                app.templistoflist=ListOfLists('temp')
                templist=app.templistoflist.getList(listname)
                templist.deleteSubscriber(current_user.username)
                return redirect(url_for('subscribelists_page'))
            if request.form['submit']=='subscribe':
                app.templistoflist=ListOfLists('temp')
                templist=app.templistoflist.getList(listname)
                templist.addSubscriber(current_user.username)
                return redirect(url_for('subscribelists_page'))

    else:
        app.templistoflist=ListOfLists('temp')
        templist=app.templistoflist.getList(listname)
        isSubscriber=templist.isSubscriber(current_user.username)
        return render_template('listsubscriberperspective.html',listname=listname,isSubscriber=isSubscriber)


@app.route('/subscribedlists',methods=['GET','POST'])
@login_required
def subscribelists_page():
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.subscribedList.addList(List(listname,current_user.username))
            subscribedlist=app.subscribedList.getSubscribeLists()
            return render_template('subscribedlists.html',subscribedlist=subscribedlist)
    else:
            app.subscribedList=ListOfLists('Subscribed to')
            subscribedlist=app.subscribedList.getSubscribeLists()
            return render_template('subscribedlists.html',subscribedlist=subscribedlist)


@app.route('/memberoflists',methods=['GET','POST'])
@login_required
def memberoflists_page():
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.memberOfList.addList(List(listname,current_user.username))
            memberlist=app.memberOfList.getInsiderLists()
            return render_template('memberoflist.html',memberoflist=memberlist)
    else:
            app.memberOfList=ListOfLists('memberOfList')
            memberoflist=app.memberOfList.getInsiderLists()
            return render_template('memberoflist.html',memberoflist=memberoflist)

@app.route('/createdlists',methods=['GET','POST'])
@login_required
def createdlists_page():
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.createdLists.addList(List(listname,current_user.username))
            createdlist=app.createdLists.getCreatedLists()
            return render_template('createdlists.html',createdlist=createdlist)
    else:
            app.createdLists=ListOfLists('CreatedLists')
            createdlist=app.createdLists.getCreatedLists()
            return render_template('createdlists.html',createdlist=createdlist)

@app.route('/polls',methods=['GET','POST'])
@login_required
def polls_page():
    if request.method=='POST':
        if request.form['submit']=='add':
            pollquestion=request.form['pollname']
            app.polls=ListOfPolls('polls')
            temppoll=Poll(pollquestion,current_user.username)
            app.polls.addPoll(temppoll)
            polllist=app.polls.getAllPolls()
            pollquestions=[pollquestion for pollquestion,creatorname in polllist]
            creatornames=[creatorname for pollquestion,creatorname in polllist]
            return render_template('polls.html',polllist=polllist)

    else:
        app.polls=ListOfPolls('polls')
        polllist=app.polls.getAllPolls()
        if polllist is not None:
            pollquestions=[pollquestion for pollquestion,creatorname in polllist]
            creatornames=[creatorname for pollquestion,creatorname in polllist]
            return render_template('polls.html',polllist=polllist)
        else:
            pollquestions=None
            creatornames=None
            return render_template('polls.html',polllist=polllist)


@app.route('/poll/<string:pollquestion>/<string:creatorname>',methods=['GET','POST'])
@login_required
def poll_page(pollquestion,creatorname):
    if request.method=='POST':
        if request.form['submit']=='update':
            app.tempPollList=ListOfPolls('temp')
            poll=app.tempPollList.getPoll(pollquestion,creatorname)
            newquestion=request.form['choiceorquestion']
            poll.updateQuestion(newquestion)
            choices=poll.getChoices()
            return render_template('poll.html',pollquestion=newquestion,choices=choices)
        elif request.form['submit']=='delete':
            app.tempPollList=ListOfPolls('temp')
            app.tempPollList.deletePoll(pollquestion,creatorname)
            return redirect(url_for('polls_page'))
        elif request.form['submit']=='addchoice':
            app.tempPollList=ListOfPolls('temp')
            poll=app.tempPollList.getPoll(pollquestion,creatorname)
            choiceinfo=request.form['choiceorquestion']
            poll.addChoice(choiceinfo)
            choices=poll.getChoices()
            return render_template('poll.html',pollquestion=pollquestion,choices=choices)

    else:
        app.templist=ListOfPolls('temp')
        poll=app.templist.getPoll(pollquestion,creatorname)
        choices=poll.getChoices()
        return render_template('poll.html',pollquestion=pollquestion,choices=choices)

@app.route('/manageapps', methods = ['GET','POST'])
@login_required
def admin_manageapps():
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
        return redirect(url_for('user_manageapps'))
    return render_template('appsettings.html', values=values, apps=apps)

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
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()

        cursor.execute(open("script.sql", "r").read())
        cursor.close()

        connection.commit()
        connection.close()
    except:
        pass
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    main()
