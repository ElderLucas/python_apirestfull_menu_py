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

app = Flask(__name__)

app_path = '/var/www/restaurant_py/'

os.chdir(app_path)

j = open('client_secrets.json', 'r')

CLIENT_ID = json.loads(j.read())['web']['client_id']

APPLICATION_NAME = "Restaurant Menu Application"

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

    STATE = state

    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    print "Login"
    print login_session['state']
    print STATE
    return render_template('login.html', STATE=state)

# Facebook CONNECT - Get a current user's token and perfomr a login_session
@app.route('/fbconnect', methods=['POST'])
def fbconnect():	
	return "Ok, Facebook"

# Facebook DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/fbdisconnect')
def fbdisconnect():
    return "you have been logged out"

# CONNECT - Get a current user's token and perfomr a login_session
@app.route('/gconnect', methods=['POST'])
def gconnect():
	return "Here I connect to a Google OAuth Provider"

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    return "Ok, Google Connect is Over"

# Restaurant URLs

# JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	return "text"

# Show all restaurants menu items Json String
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	return "Show all restaurants menu items Json String"

# Show all restaurants Json String
@app.route('/restaurant/JSON')
def restaurantsJSON():
	return "Show all restaurants Json String"

# Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
	return "Show all restaurants"

# Create a new restaurant
@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
	return "Create a new restaurant"

# Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	return "Edit a restaurant"

# Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	return "Delete a restaurant"

# Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
	return "Show a restaurant menu"

# Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	return "Create a new menu item"

# Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	return "Edit a menu item"

# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	return "Delete a menu item"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
	return "Disconnect based on provider"


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.debug = True
    app.run(host='0.0.0.0', port=5000)
