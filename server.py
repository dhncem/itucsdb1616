import datetime
import os
import json
import re

from flask import Flask
from handlers import site
from flask import Blueprint, render_template
from store import Store
from twit import Twit
from message import Message
from messageList import MessageList
from list import List
from listoflist import ListOfLists
from flask import Flask
from handlers import site




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
	app = Flask(__name__)
	app.config.from_object('settings')
	app.register_blueprint(site)

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
		app.config['dsn'] = """user='vagrant' password='vagrant' host='localhost' port=54321 dbname='itucsdb'"""

	app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
	main()
