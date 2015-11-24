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

# Connect to Database and create database session
engine = create_engine('mysql://root:oigalera8458@localhost/restaurant')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

DEBUG_ALL = True

app_path = os.getcwd()

os.chdir(app_path)


if ((os.path.isfile('client_secrets.json'))== True):
	opened_file = open('client_secrets.json', 'r')
else:
	opened_file = open('/var/www/restaurant_py/client_secrets.json', 'r')

CLIENT_ID = json.loads(opened_file.read())['web']['client_id']

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
    #if DEBUG_ALL is True: 
    #    print "################################################################"
    #    print "SHOWING ALL RESTAURANT"
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    print "Query"

    if 'username' not in login_session:
        print "Public restaurant/"
        return render_template('publicrestaurants.html', restaurants=restaurants)
    else:
        print "restaurant/"
        return render_template('restaurants.html', restaurants=restaurants)  

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

    if DEBUG_ALL is True: 
        print "################################################################"
        print "SHOWING ALL MENU ITEMS"

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    creator = getUserInfo(restaurant.user_id)
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    if 'email' not in login_session:
    	current_user_id = getUserID(login_session['email'])
    else:
    	return "Restaurant Menu Error"

    if DEBUG_ALL is True: 
        print "Restaurant: ---->"
        print restaurant.name
        print "Restaurant USER ID: ---->"
        print restaurant.user_id
        print "Criador desse Menu: ---->"
        print creator.id
        print creator.name
        print creator.email
        print "################################################################"

    if 'username' not in login_session or creator.id != current_user_id:
        print "Public restaurant/"
        return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    else:
        print "Ok, im a owner of this menu item"     
        if DEBUG_ALL is True: 
            print "################################################################"
            print "My Current User id...."
            print current_user_id
            print "Email of User Owner of this :"
            print login_session['email']
            print "################################################################"

        return render_template('menu.html', items=items, restaurant=restaurant, creator=creator)


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


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        print "getUserID OK"
        print user.id
        return user.id
        
    except:
        print "getUserID NONE"
        return None


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showRestaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showRestaurants'))



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.debug = True
    app.run(host='0.0.0.0', port=5000)
