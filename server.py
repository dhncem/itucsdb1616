from flask import Flask
import datetime
import os
from handlers import site
from flask import Blueprint, render_template
from store import Store
from twit import Twit

from flask import Flask

from handlers import site


def create_app():
    app = Flask(__name__)
    app.config.from_object('settings')
    app.register_blueprint(site)

    app.store = Store()
    app.store.add_twit(Twit('Mr First Tweet', 'Just so you don\'t get tired we posted your first tweet'))




    return app


def main():
    app = create_app()
    debug = app.config['DEBUG']
    port = app.config.get('PORT', 5000)
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
