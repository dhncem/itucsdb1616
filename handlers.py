import datetime
import os
from flask import current_app
from flask import Blueprint, redirect, render_template, url_for
from flask import current_app, request

site = Blueprint('site', __name__)

@site.route('/')
def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())

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









#@site.route('/twits/<int:twit_id>')
#def twit_page(twit_id):
  #twits = current_app.store.get_twit(twit_id)
  #return render_template('twit.html', twit=twit, current_time=now.ctime())