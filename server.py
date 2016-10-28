# -*- coding: utf-8 -*-
import datetime
import os
import json
import re
import psycopg2 as dbapi2

from flask import Flask
from flask import Blueprint, render_template, redirect, url_for
from store import Store
from twit import Twit
from message import Message
from messageList import MessageList
from list import List
from listoflist import ListOfLists
from flask import current_app, request

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


def create_app():
    app.config.from_object('settings')

    app.store = Store()
    app.store.add_twit(Twit('Mr First Tweet', 'Just so you don\'t get tired we posted your first tweet'))

    app.messageList = MessageList()
    app.messageList.add_message(Message('Emre Cetiner', 'Serkan Bekir', 'hello', sent = False))
    app.messageList.add_message(Message('Yusuf Ekiz', 'Serkan Bekir', 'good morning', sent = True))
    app.messageList.add_message(Message('Mert Kurtcan', 'Serkan Bekir', 'hi!'))
    app.messageList.add_message(Message('Cem Karagoz', 'Serkan Bekir', 'good afternoon'))

    app.subscribedList=ListOfLists('Subscribed to')
    app.memberOfList=ListOfLists('Member Of')
    app.subscribedList.addList(List('NBA Fans'))
    app.subscribedList.addList(List('Informatik'))
    app.memberOfList.addList(List('Basketball Games'))
    app.memberOfList.addList(List('History Of Science'))

    return app


@app.route('/')
def root_page():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['inputEmail']
        return redirect(url_for('home_page', username=username))

@app.route('/home', methods=['GET'])
def home_page():
    now = datetime.datetime.now()
    if    request.method == 'GET':
        return render_template('home.html', username=request.args.get('username'), current_time=now.ctime())

@app.route('/twits')
def twit_page():
    now = datetime.datetime.now()
    twits = current_app.store.get_twit()
    return render_template('twits.html', twits=sorted(twits.items()), current_time=now.ctime())

@app.route('/twits/add', methods=['GET', 'POST'])
def twit_add_page():
    if request.method == 'GET':
        return render_template('add_twit.html')
    else:
        title = request.form['title']
        content = request.form['content']
        twit = Twit(title, content)
        current_app.store.add_twit(twit)
        return redirect(url_for('app.twit_page', movie_id=movie._id))

@app.route('/messages')
def messages_page():
    messages = current_app.messageList.get_messages()
    return render_template('messages.html', messages=messages)


@app.route('/message/<int:message_id>')
def message_page(message_id):
    message = current_app.messageList.get_message(message_id)
    return render_template('message.html', message=message)


@app.route('/settings')
def settings_page():
    now = datetime.datetime.now()
    return render_template('settings.html', current_time=now.ctime())

@app.route('/subscribedlists')
def subscribelists_page():
    subscribedlist=current_app.subscribedList.getLists()
    return render_template('subscribedlists.html',subscribedlist=subscribedlist)


@app.route('/memberoflists')
def memberoflists_page():
    memberoflist=current_app.memberOfList.getLists()
    return render_template('memberoflist.html',memberoflist=memberoflist)

#@app.route('/twits/<int:twit_id>')
#def twit_page(twit_id):
  #twits = current_app.store.get_twit(twit_id)
  #return render_template('twit.html', twit=twit, current_time=now.ctime())

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

def initialize_database():
    try:
        connection = dbapi2.connect(app.config['dsn'])
        cursor = connection.cursor()

        cursor.execute("""CREATE TABLE TWEETS(TWEETID SERIAL PRIMARY KEY NOT NULL, USERID INT NOT NULL, TITLE CHAR(20) NOT NULL, CONTEXT CHAR(140) NOT NULL)""")


        cursor.execute("""INSERT INTO TWEETS (USERID, TITLE, CONTEXT)
                            VALUES
                            (1, 'Admin Tweets', 'First Tweet By Adminssss')""")


        connection.commit()
        connection.close()
    except:
        pass
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    main()
