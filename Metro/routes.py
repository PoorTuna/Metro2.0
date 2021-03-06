# Flask imports
from flask import redirect, url_for, render_template, request,session
# Database models imports
from .models import db, metro_user, metro_chat, login_manager, metro_post
# Password hashing import
import bcrypt
# Flask-Login imports
import flask_login
from flask_login import login_user, login_required, logout_user, current_user
# Import app in a way to prevent circular imports
from flask import current_app as app
# Chat ids random string imports
import random
import string
# Date and Time import
from datetime import datetime
# Email Validation:
import re
# Import SocketIO file
from .msockets import *
from .mfunctions import *

# Import OS
import os
# Import shutil for copying images
from shutil import copyfile

#This file contains custom routes handling for the Metro2.0 project

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return render_template("error/404.html")

@app.route("/", methods=['GET', 'POST'])
def index():
	if not flask_login.current_user.is_authenticated:
		if 'user' in session:
			if session_user := metro_user.query.get(int(session['user'])):
				login_user(session_user)
				session['bullets'] = session_user._balance
				session['colorPalette'] = session_user.theme

	if flask_login.current_user.is_authenticated:
		if 'bullets' not in session:
			session['bullets'] = flask_login.current_user._balance
		if 'colorPalette' not in session:
			session['colorPalette'] = flask_login.current_user.theme
		
		# Checks on whether the user posted a request
		if request.method == "POST":
			# Adding members form vars:
			chat_member = None
			# Creating chat form vars:
			chat_title = None
			# Changing chat attributes form vars:
			chat_img = None
			new_chat_title = None

			if "cchat_modal_title_name" in request.form:
				chat_title = request.form["cchat_modal_title_name"]
			if "amchat_modal_member_name" in request.form:
				chat_member = request.form["amchat_modal_member_name"]
			if "ddsettings_modal_title" in request.form:
				new_chat_title = request.form["ddsettings_modal_title"]
			if "ddsettings_modal_logo" in request.files:
				chat_img = request.files["ddsettings_modal_logo"]

			if chat_title:
				if len(chat_title) <= 25 and len(chat_title) > 0:
					#Strip chat_title from special characters:
					chat_title = re.sub('[<>:"/\|?@*$%^&*`~]', '', chat_title)
					print(chat_title)
					curr_time = (datetime.now() + timedelta(hours=3)).strftime("%d/%m/%y") 
					curr_chat = metro_chat(string_id = None, title=chat_title, time_created = curr_time)
					# Random string id generation
					letters = string.ascii_letters
					curr_chat.string_id = ''.join(random.choice(letters) for i in range(10)) # create random string for id as protection.
					db.session.add(curr_chat)
					db.session.commit()
					# Must be seperated to after the chat recieves id when commited firstly.
					curr_chat.string_id += str(curr_chat.id) # can only get the id after the first commit
					curr_chat.file_dir = f"static/assets/chats/{curr_chat.string_id}{curr_chat.title}/"
					curr_chat.chat_backref.append(flask_login.current_user) # Add user to the backref
					curr_chat.chat_owner_backref = flask_login.current_user # make the user the owner
					curr_chat.chat_admin_backref.append(flask_login.current_user) # Add user to the admin backref
					
					db.session.commit()
					# Create chat folder:
					os.makedirs(f"Metro/static/assets/chats/{curr_chat.string_id}{curr_chat.title}/")
					# Create default chat img
					copyfile(f"Metro/static/assets/images/logo/logo.png", f"Metro/{curr_chat.file_dir}/logo.png")

					return redirect(url_for("index"))

			if session['chatID'] and session['chatID'] != "general":
				if curr_chat := metro_chat.query.filter_by(string_id=session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref:
						#Get the chat data to the user.
						with open(f"Metro/{curr_chat.file_dir}/chat.data", "a+") as fd:
							chat_data = fd.readlines() 

						if chat_member:
							if requested_user := metro_user.query.filter_by(username=chat_member).first():
								if requested_user not in curr_chat.chat_backref:
									curr_chat.chat_backref.append(requested_user)
									db.session.commit()
									return redirect(url_for("index"))

						if new_chat_title:
							if len(new_chat_title) <= 25 and len(new_chat_title) > 0:
								#Strip chat_title from special characters:
								new_chat_title = re.sub('[<>:"/\|@?*$%^&*`~]', '', new_chat_title)
								curr_chat.title = new_chat_title
								os.rename(f"Metro/{curr_chat.file_dir}", f"Metro/static/assets/chats/{curr_chat.string_id}{new_chat_title}/")
								curr_chat.file_dir = f"static/assets/chats/{curr_chat.string_id}{new_chat_title}/"
								db.session.commit()
						
						if chat_img:
							if logoname := chat_img.filename:

								if "." + logoname.split(".")[1] in app.config['ALLOWED_EXTENSIONS']:
									if os.path.exists(f"Metro/{curr_chat.file_dir}/logo.png"):
										os.remove(f"Metro/{curr_chat.file_dir}/logo.png")
									chat_img.save(f"Metro/{curr_chat.file_dir}/logo.png")
									

						return redirect(url_for("index"))

		chats = []

		for m_chat in flask_login.current_user.chat_list:
				for m_user in m_chat.chat_backref:
					if m_user == flask_login.current_user:
						chats.append(m_chat)

		return render_template("index.html", chats = chats)
	return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if not flask_login.current_user.is_authenticated: # Prevent user from using login if already logged in
		try:
			if session['user']:
				flask_login.current_user = metro_user.query.get(int(session['user']))
				return redirect(url_for("index")) #User in session
		except:
			pass
		if request.method == 'POST':
			flask_login.logout_user() # overlooked protection 
			form_username = request.form["username"]
			form_password = request.form["password"]

			if form_username and form_password: #if the fields weren't empty go ahead and query the database

				# Check if input matches a user in the database:
				if logged_user := metro_user.query.filter_by(username = form_username).first(): # Check if the user tried to log using his username
					if bcrypt.checkpw(form_password.encode(), logged_user.password): # Check if the passwords match + decrypt the password with the password as the key
							login_user(logged_user) # log him with the flask_login module
							session['user'] = flask_login.current_user.id # set session parameters:
							session['bullets'] = flask_login.current_user._balance
							session['colorPalette'] = flask_login.current_user.theme

				if logged_user := metro_user.query.filter_by(email = form_username).first(): # Check if the user tried to log using his email
					if bcrypt.checkpw(form_password.encode(), logged_user.password):
							login_user(logged_user)
							session['user'] = flask_login.current_user.id # set session parameters:
							session['bullets'] = flask_login.current_user._balance
							session['colorPalette'] = flask_login.current_user.theme

				if flask_login.current_user.is_authenticated:
					return redirect(url_for("index")) #Login successful
				
				return render_template("login.html", err = "One of the credentials you've entered is incorrect!")

			return render_template("login.html", err = "Please fill the blank fields. nice try :)") #If the user penetrated front end protection -> Required
		return render_template("login.html", err = "")
	return redirect(url_for("index"))

@app.route("/register", methods=['GET', 'POST'])
def register():
	if not flask_login.current_user.is_authenticated: # Prevent user from using register if already logged in
		if request.method == "POST":
			regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$' # String to check if email is valid
			form_username = request.form["username"] # Get username from request
			form_password = request.form["password"] # Get password from request
			form_email = request.form["email"] # Get email from request
			if len(form_password) >= 8 and len(form_username) <= 12 and re.search(regex, form_email): # input validation conditions
				if metro_user.query.filter_by(username = form_username).first(): # find if theres a user with that name
					return render_template("register.html", err = "Username already exists.")
				elif metro_user.query.filter_by(email = form_email).first(): # find if theres a user with that email
					return render_template("register.html", err = "Email already exists.")
				
				hashed_password = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt()) # encrypt user password
				db.session.add(metro_user(username = form_username, password = hashed_password, email = form_email))
				db.session.commit()
				return redirect(url_for("login"))
			else:
				return render_template("register.html", err ="Invalid Input, Nice Try :)")

		return render_template("register.html")
	return redirect(url_for("index"))


@app.route("/support/")
def support():
	posts = metro_post.query.all() # query the database for each post
	return render_template("support/support.html", posts = posts)

@app.route("/support/create", methods=['GET', 'POST'])
@login_required
def support_create():
	error = ""
	if request.method == "POST":
		if 'title' in request.form and 'body' in request.form: # check if the data exists
			if len(request.form['title']) >= 3:
				if len(request.form['body']) >= 3:
					rand_str = ''.join(random.choice(string.ascii_letters) for i in range(10)) # random path for protection
					curr_time = (datetime.now() + timedelta(hours=3)).strftime("%d/%m/%Y, %H:%M")
					curr_post = metro_post(title = request.form['title'], author=flask_login.current_user.username, time_created = curr_time)
					curr_post.owner_id = flask_login.current_user.id
					db.session.add(curr_post)
					db.session.commit()
					curr_post.string_id = rand_str + str(curr_post.id) # change the string id //gets the id after added to the database
					db.session.commit()
					os.makedirs(f"Metro/static/assets/posts/{curr_post.string_id}{curr_post.title}/") # create the folder for the files
					with open(f"Metro/static/assets/posts/{curr_post.string_id}{curr_post.title}/post.data", "a+") as metro_filehandler:
						metro_filehandler.write(request.form['body'])
					return redirect(url_for("support_post", id = curr_post.string_id))
				else:
					error = "Incorrect parameter size!"
			else:
				error = "Incorrect parameter size!"
		else:
			error = "Missing one or more parameters!"
			
	return render_template("support/create.html", err = error)

@app.route("/support/post/<id>")
def support_post(id):
	if curr_post := metro_post.query.filter_by(string_id = id).first(): # get the post object from the db
		if os.path.exists(f"Metro/static/assets/posts/{curr_post.string_id}{curr_post.title}/post.data"): # prevent crashing if folder doesn't exist
			with open(f"Metro/static/assets/posts/{curr_post.string_id}{curr_post.title}/post.data", "a+") as metro_fd:
				metro_fd.seek(0) # a+ goes to the end of the file, revert to position 0.
				body = metro_fd.readlines()
		else:
			body = "post is unavailable!"
	else:
		curr_post = ""
		body = "post not found!"

	return render_template("support/post.html", post = curr_post, body = body)


@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/logout")
@login_required
def logout():
	flask_login.current_user._session_id = None
	logout_user()
	session.pop('user', None)
	session.pop('bullets', None)
	session.pop('colorPalette', None)
	session.pop('currgame', None) # Choose game
	session.pop('startedgame', None) # Start game
	
	return redirect(url_for("index"))

@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
	if not flask_login.current_user.is_authenticated: # prevent logged user from accessing this page
		try:
			if session['user']:
				flask_login.current_user = metro_user.query.get(int(session['user']))
				session.pop('forgotEmail', None)
				session.pop('enteredCODE', None)
				session.pop('forgotCODE', None)
				return redirect(url_for("index")) #User in session
		except:
			pass

		err_code = ""
		if request.method == 'POST':
			
			if 'forgotCODE' not in session and "email" in request.form: # before the user has entered the email / first phase

				# The email request section
				form_email = request.form["email"] # form email
				if email_user := metro_user.query.filter_by(email = form_email).first(): # check if the user exists by the email
					session['forgotCODE'] = ''.join(random.choice(string.ascii_letters) for i in range(10)) # Random str for code
					session['forgotEmail'] = email_user.email
					try:
						metro_send_mail(email_user, session['forgotCODE']) # send mail
						#session['forgotCODE'] = bcrypt.hashpw(session['forgotCODE'], bcrypt.gensalt())
					except:
						print("Email System Error")

				else:
					err_code = "Invalid Email!"

			elif 'enteredCODE' not in session or session['enteredCODE'] != session['forgotCODE']: # after the user has entered the email / second phase / enter the code section
				# The code entering section
				form_code = request.form["entercode"] # form code
				if form_code:
					if len(form_code) == 10: # check if the length matches the supposed length
						session['enteredCODE'] = form_code
						if session['enteredCODE'] == session['forgotCODE']:
							err_code = "Success! Redirecting..."
						else:
							err_code = "Invalid Code!"
					else:
						session['enteredCODE'] = False
						err_code = "Invalid Code Format!"
			
			elif session['enteredCODE'] == session['forgotCODE']: # the last phase, the user has entered the correct code -> send him to the password changing section

				# The password changing section
				form_password = request.form["password"] # form password
				form_confirm_password = request.form["confirmpassword"] # form password confirmation
				if form_password and form_confirm_password: # check if theres data
					if form_password == form_confirm_password:
						if len(form_password) >= 8:
							if 'forgotEmail' in session: # protection
								if email_user := metro_user.query.filter_by(email = session['forgotEmail']).first():
									hashed_password = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt()) # encrypt new password
									email_user.password = hashed_password # change password
									db.session.commit()
									# Session cleanup just in case:
									session.pop('forgotEmail', None)
									session.pop('enteredCODE', None)
									session.pop('forgotCODE', None)
									return redirect(url_for("login"))
						else:
							err_code = "Passwords are too short!"
					else:
						err_code = "Passwords do not match!"

		return render_template("forgot.html", err = err_code)

	return redirect(url_for("index"))

@app.route("/profile")
@login_required
def profile():
	data = []
	chat_list = []
	admin_list = []
	owner_list = []
	curr_user = flask_login.current_user
	# Insert Name :
	data.append(["Nickname:", curr_user.username]) 
	# Insert Email :
	data.append(["Email:", curr_user.email])
	# Insert Balance :
	data.append(["Balance:", curr_user._balance])
	# Insert Chat List :
	for chat in curr_user.chat_list:
		chat_list.append(chat.title)
	data.append(["Stations:", chat_list])
	# Insert Admin Chat List :
	for chat in curr_user.chat_admin_list:
		admin_list.append(chat.title)
	data.append(["Stations you Manage:", admin_list])
	# Insert Owner Chat List :
	for chat in curr_user.chat_owner_list:
		owner_list.append(chat.title)
	data.append(["Stations you Own:", owner_list])

	return render_template("user/profile.html", data = data)

@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
	logged_user = flask_login.current_user
	if request.method == "POST":
		# Color Palette Section
		if 'palette_option' in request.form:
			if request.form['palette_option']:
				palettes_option = request.form['palette_option']
				if palettes_option in logged_user.theme_list:
					logged_user.theme = palettes_option
					session['colorPalette'] = logged_user.theme
			
		# Password Changing Section
		if 'password' in request.form and 'repeat_password' in request.form:
			if request.form['password'] == request.form['repeat_password']:
				if len(request.form['password']) >= 8:
					if bcrypt.checkpw(request.form['password'].encode(), logged_user.password):
						hashed_password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
						logged_user.password = hashed_password
		
		db.session.commit() # global for all changes
		return redirect(url_for("index"))


	color_palettes = logged_user.theme_list.split('|')
	color_palettes.remove("")
	return render_template("user/settings.html", palettes = color_palettes, email = logged_user.email, name = logged_user.username)

@app.route("/store")
@login_required
def store():
	return render_template("store.html", palette_list = flask_login.current_user.theme_list.split('|'))

@app.route("/game")
@login_required
def game():
	return render_template("game.html")


@app.route("/gimmemoneyplzmatethanks")
@login_required
def money():
	flask_login.current_user._balance += 100
	db.session.commit()
	session['bullets'] = flask_login.current_user._balance
	return redirect(url_for("index"))


@app.route("/<name>")
@app.errorhandler(404)
def something(name):
	return render_template("error/404.html", url = name)


@app.route("/test")
@login_required
def test_game():
	return render_template("actualgame.html")
	