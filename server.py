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
from messageList import MessageList
from list import List
from listoflist import ListOfLists
from flask import current_app, request
from user import get_user
from forms import LoginForm
from forms import RegisterForm
from followoperations import *
from usersettings import *


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
    try:
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            username = form.username.data
            password = pwd_context.encrypt(form.password.data)

            connection = dbapi2.connect(app.config['dsn'])
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO USERS (USERNAME, PASSWORD) VALUES (%s, %s)""", (username, password))
            cursor.execute("""INSERT INTO USERPROFILE (NICKNAME, USERNAME, BIO) VALUES(%s, %s, %s)""", (username, username, 'bio'))
            cursor.execute("""INSERT INTO USERINFO (NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(%s, %s, %s, %s, %s)""",
                           ('', '', '', '', ''))
            cursor.close()
            connection.commit()
            login_user(get_user(username))
            connection.close()
            return redirect(url_for('home_page'))

        return render_template('register.html', form=form)
    except:
        flash("Username is already taken!")

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
        current_app.messageList.delete_message()
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

@app.route('/list/<string:listname>',methods=['GET','POST'])
@login_required
def list_page(listname):
    if request.method=='POST':
        if request.form['submit']=='update':
            newlistname=request.form['listname']
            list= List(listname,current_user.username)
            list.updateName(newlistname)
            return render_template('list.html',listname=newlistname)
    else:
        return render_template('list.html',listname=listname)

@app.route('/subscribedlists',methods=['GET','POST'])
@login_required
def subscribelists_page():
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.subscribedList.addList(List(listname,current_user.username))
            subscribedlist=app.subscribedList.getLists()
            return render_template('subscribedlists.html',subscribedlist=subscribedlist)
        elif request.form['submit']=='delete':
            listname=request.form['listname']
            app.subscribedList.deleteList(listname,current_user.username)
            subscribedlist=app.subscribedList.getLists()
            return render_template('subscribedlists.html',subscribedlist=subscribedlist)
    else:
            app.subscribedList=ListOfLists('Subscribed to')
            subscribedlist=app.subscribedList.getLists()
            return render_template('subscribedlists.html',subscribedlist=subscribedlist)


@app.route('/memberoflists',methods=['GET','POST'])
@login_required
def memberoflists_page():
    if request.method=='POST':
        if request.form['submit']=='add':
            listname=request.form['listname']
            app.memberOfList.addList(List(listname,current_user.username))
            memberlist=app.memberOfList.getLists()
            return render_template('memberoflist.html',memberoflist=memberlist)
        elif request.form['submit']=='delete':
            listname=request.form['listname']
            app.memberOfList.deleteList(listname,current_user.username)
            memberoflists=app.memberOfList.getLists()
            return render_template('memberoflist.html',memberoflist=memberoflists)
    else:
            app.memberOfList=ListOfLists('memberOfList')
            memberoflist=app.memberOfList.getLists()
            return render_template('memberoflist.html',memberoflist=memberoflist)

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
def initialize_database():
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
