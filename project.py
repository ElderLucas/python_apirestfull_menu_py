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



####################### Carregando o Arquivo JSON ########################
# Eh importante lembrar que esse if serve para verificar se o arquivo 
# existe num current diretorio, o que se caso nao existir, o apache
# que esta rodando do "sever side" ira busca-lo em um lugar especifico
##########################################################################
if ((os.path.isfile('client_secrets.json'))== True):
	opened_file = open('client_secrets.json', 'r')
	print "Ok, Im in Local Side"
	jsonfile_path = 'client_secrets.json'
else:
	opened_file = open('/var/www/restaurant_py/client_secrets.json', 'r')
	print "Ohhh, Im in a Server Side"
	jsonfile_path = '/var/www/restaurant_py/client_secrets.json'

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
    # Validate state token
    print "Gconnect Part"
    if request.args.get('state') != login_session['state']:
        print "Invalido!!!"
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data
    print "Code Ok"

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(jsonfile_path, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print "Credential Ok"
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print "G Connect FlowExchangeError"
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['user_id'] = "x"

    login_session['current_status'] = "connected"
    print "We are connected"
    print login_session['current_status']

    user_id = getUserID(login_session['email'])

    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id
    else:
        #Nesse caso o Usuarios ja exixte porem so precisamos atribuir a sessao pois no ultmi gdisconnecte esse dado foi deletado.
        print "The user already existe"
        login_session['user_id'] = user_id

    if DEBUG_ALL is True: 
        print "################################################################"
        print "Agora estou conectador como :"
        print login_session['username']
        print login_session['picture']
        print login_session['email']
        print "The user ID: ---->" 
        print user_id
        print "################################################################"



    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

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

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    creator = getUserInfo(restaurant.user_id)
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    if 'username' not in login_session:
        print "Public restaurant/...... User Doesn't Exist"
        return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    else:
    	if 'email' in login_session:
    		print "Verify Email"
    		current_user_id = getUserID(login_session['email'])
    		if creator.id == current_user_id:
    			return render_template('menu.html', items=items, restaurant=restaurant, creator=creator)
    		else:
    			return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    	else:
    		print "Email Error... Is not the Same User"
    		return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)

    if DEBUG_ALL is True: 
        print "Restaurant: ---->"
        print restaurant.name
        print "Restaurant USER ID: ---->"
        print restaurant.user_id
        print "Criador desse Menu: ---->"
        print creator.id
        print creator.name
        print creator.email


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
