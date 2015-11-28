#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import os
from flask import make_response
import requests

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('mysql://root:oigalera8458@localhost/restaurant')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

DEBUG_ALL = True

app_path = os.getcwd()
os.chdir(app_path)

print "Pão de Quijo \n"

newRestaurant = Restaurant(name='AÁáPOIUYTW´®çµ√ˆƒøßπœ∑´ˆççˆµ˜∫√aass', user_id = 2)
session.add(newRestaurant)
session.commit()

print "Ok, DONE"

restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
#return render_template('publicrestaurants.html', restaurants=restaurants)
for restaurn in restaurants:
	print restaurn.id
	print restaurn.name
	print restaurn.user_id

# Create anti-forgery state token
@app.route('/debug')
def debug():
	print "Im Ok... Running......."
	restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
	for restaurn in restaurants:
		print restaurn.id
		print restaurn.name
		print restaurn.user_id

	a = u'Pão'

	return render_template('teste_utf8.html', list=a)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.debug = True
    app.run(host='0.0.0.0', port=5000)
