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
    login_session['provider'] = 'google'
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
    access_token = login_session['access_token']


    if DEBUG_ALL is True: 
        print "################################################################"
        print "DESCONECTANDO + x + x + x + x + x + x + x + x + x + x + x + x + "

    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        login_session['current_status'] = "disconnected"
        print "Current Status : "
        print login_session['current_status']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

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
    print "Start Query Restaurant"
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    print "Query"

    # Aqui eu escolhi verificar por meio do um email pelo fato de que somente o email e garantido de existir.
    if 'email' not in login_session:
        print "Public restaurant/"
        return render_template('publicrestaurants.html', restaurants=restaurants)
    else:
        print "restaurant/"

        for restaurn in restaurants:
			print restaurn.id
			print restaurn.name
			print restaurn.user_id

        return render_template('restaurants.html', restaurants=restaurants)  

# Create a new restaurant
@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():

    if DEBUG_ALL is True: 
        print "################################################################"
        print "CREATING A NEW RESTURANT"
           
    if 'username' not in login_session:
        return redirect('/login')
        if DEBUG_ALL is True: 
            print "Goshhh ... Im not Logged in"
            print "################################################################"
            
    if request.method == 'POST':
        if DEBUG_ALL is True: 
            print "****************************************************************"
            print "O Nome do Retaurant que sera criado:-------->"
            print request.form['name']
            print "Dados do usuario Current"
            print "USER ID -->>>> "
            print login_session['user_id']
            print "USER NAME -->>>> "
            print login_session['username']
            print "EMAIL -->>>> "
            print login_session['email']
            print "PICTURED -->>>> "
            print login_session['picture']
            print "################################################################"

        newRestaurant = Restaurant(name=request.form['name'], user_id = login_session['user_id'])
        print "New REst Query"
        session.add(newRestaurant)
        print "Session Added"
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        print "Flash"
        session.commit()
        print "Commit"
        return redirect(url_for('showRestaurants'))
    else:
        print "newRestaurant"
        return render_template('newRestaurant.html')

# Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):

    editedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if 'email' not in login_session:
        return redirect('/login')

    if editedRestaurant.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=editedRestaurant)


# Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):

    restaurantToDelete = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if 'email' not in login_session:
        return redirect('/login')

    if restaurantToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)

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

    current_user_id = getUserID(login_session['email'])

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

    if 'email' not in login_session or creator.id != current_user_id:
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

    if 'email' not in login_session:
        print "There is no one logged"
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        print "eu entrei"
        newItem = MenuItem(name=request.form['name'],
            description=request.form['description'], 
            price=request.form['price'], 
            course=request.form['course'],
            user_id=restaurant.user_id,
            restaurant_id=restaurant_id)
        session.add(newItem)
        print "eu tentei"
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):

    if 'username' not in login_session:
        return redirect('/login')

    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):

    if 'username' not in login_session:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()

    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


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
    	print "Ok Lets Try Loggin Out" 
        if login_session['provider'] == 'google':
        	print "Google Desconnected"
        	gdisconnect()
        	del login_session['gplus_id']
        	del login_session['credentials']

        if login_session['provider'] == 'facebook':
        	print "FaceBook Desconnected"
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
        print "Im Not Connected"
        return redirect(url_for('showRestaurants'))



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.debug = True
    app.run(host='0.0.0.0', port=5000)
