import datetime
import os
from flask import current_app
from flask import Blueprint, redirect, render_template, url_for
from flask import current_app, request
from message import Message
from list import List
from listoflist import ListOfLists

site = Blueprint('site', __name__)



@site.route('/')
def root_page():
	return redirect(url_for('site.login_page'))

@site.route('/login', methods=['GET', 'POST'])
def login_page():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		username = request.form['inputEmail']
		return redirect(url_for('site.home_page', username=username))

@site.route('/home', methods=['GET'])
def home_page():
	now = datetime.datetime.now()
	if	request.method == 'GET':
		return render_template('home.html', username=request.args.get('username'), current_time=now.ctime())

@site.route('/twits')
def twit_page():
    now = datetime.datetime.now()
    twits = current_app.store.get_twit()
    return render_template('twits.html', twits=sorted(twits.items()), current_time=now.ctime())

@site.route('/twits/add', methods=['GET', 'POST'])
def twit_add_page():
    if request.method == 'GET':
        return render_template('add_twit.html')
    else:
        title = request.form['title']
        content = request.form['content']
        twit = Twit(title, content)
        current_app.store.add_twit(twit)
        return redirect(url_for('site.twit_page', movie_id=movie._id))

@site.route('/messages')
def messages_page():
    messages = current_app.messageList.get_messages()
    return render_template('messages.html', messages=messages)


@site.route('/message/<int:message_id>')
def message_page(message_id):
    message = current_app.messageList.get_message(message_id)
    return render_template('message.html', message=message)


@site.route('/settings')
def settings_page():
    now = datetime.datetime.now()
    return render_template('settings.html', current_time=now.ctime())

@site.route('/subscribedlists')
def subscribelists_page():
    subscribedlist=current_app.subscribedList.getLists()
    return render_template('subscribedlists.html',subscribedlist=subscribedlist)


@site.route('/memberoflists')
def memberoflists_page():
    memberoflist=current_app.memberOfList.getLists()
    return render_template('memberoflist.html',memberoflist=memberoflist)

#@site.route('/twits/<int:twit_id>')
#def twit_page(twit_id):
  #twits = current_app.store.get_twit(twit_id)
  #return render_template('twit.html', twit=twit, current_time=now.ctime())