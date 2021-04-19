# Flask imports
from flask import redirect, url_for, render_template, request,session
# Database models imports
from .models import db, metro_user, metro_chat, login_manager
# Password hashing import
import bcrypt
# Flask-Login imports
import flask_login
from flask_login import login_user, login_required, logout_user
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
# Import OS
import os

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return render_template("error/404.html")

@app.route("/", methods=['GET', 'POST'])
def index():
	if flask_login.current_user.is_authenticated:

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
			
			print(request.files)
			if "ddsettings_modal_logo" in request.files:
				chat_img = request.files["ddsettings_modal_logo"]

			if chat_title:
				if len(chat_title) <= 25 and len(chat_title) > 0:
					curr_time = datetime.now().strftime("%d/%m/%y") 
					curr_chat = metro_chat(string_id = None, title=chat_title, time_created = curr_time)
					# Random string id generation
					letters = string.ascii_letters
					curr_chat.string_id = ''.join(random.choice(letters) for i in range(10))
					db.session.add(curr_chat)
					db.session.commit()
					# Must be seperated to after the chat recieves id when commited firstly.
					curr_chat.string_id += str(curr_chat.id)
					curr_chat.file_dir = f"static/assets/chats/{curr_chat.string_id}{curr_chat.title}/"
					curr_chat.chat_backref.append(flask_login.current_user) # Add user to the backref
					db.session.commit()
					# Create chat folder:
					os.makedirs(f"Metro/static/assets/chats/{curr_chat.string_id}{curr_chat.title}/")
					return redirect(url_for("index"))

			if session['chatID'] and session['chatID'] != "general":
				if curr_chat := metro_chat.query.filter_by(string_id=session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref:
						if chat_member:
							if requested_user := metro_user.query.filter_by(username=chat_member).first():
								if requested_user not in curr_chat.chat_backref:
									curr_chat.chat_backref.append(requested_user)
									db.session.commit()
									return redirect(url_for("index"))

						if new_chat_title:
							if len(new_chat_title) <= 25 and len(new_chat_title) > 0:
								curr_chat.title = new_chat_title
								os.rename(f"Metro/{curr_chat.file_dir}", f"Metro/static/assets/chats/{curr_chat.string_id}{new_chat_title}/")
								curr_chat.file_dir = f"static/assets/chats/{curr_chat.string_id}{new_chat_title}/"
								db.session.commit()
						
						if chat_img:
							if logoname := chat_img.filename:
								print(chat_img.filename)
								if logoname.split(".")[1] in ALLOWED_EXTENSIONS:
									if os.path.exists(f"Metro/{curr_chat.file_dir}/logo.png"):
										os.remove(f"Metro/{curr_chat.file_dir}/logo.png")
									chat_img.save(f"Metro/{curr_chat.file_dir}/logo.png")
									

						return redirect(url_for("index"))

		chats = []
		chat_data = None

		for m_chat in flask_login.current_user.chat_list:
				for m_user in m_chat.chat_backref:
					if m_user == flask_login.current_user:
						chats.append(m_chat)

		# if 'chatID' in session:
		# 	if session['chatID'] != "general":
		# 		if current_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
		# 			with open(current_chat.file_dir, "a+") as fd:
		# 				chat_data = fd.readlines() 
		# else:
		# 	chat_data = ""

		return render_template("index.html", chats = chats, chat_data = chat_data)
	return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if not flask_login.current_user.is_authenticated:
		try:
			if session['user']:
				flask_login.current_user = metro_user.query.get(int(session['user']))
				return redirect(url_for("index")) #User in session
		except:
			pass
		if request.method == 'POST':
			flask_login.logout_user() # ??? from future oren 
			form_username = request.form["username"]
			form_password = request.form["password"]

			if form_username and form_password: #if the fields weren't empty go ahead and query the database

				# Check if input matches a user in the database:
				if logged_user := metro_user.query.filter_by(username = form_username).first():
					if bcrypt.checkpw(form_password.encode(), logged_user.password):
							login_user(logged_user)
							session['user'] = flask_login.current_user.id

				if logged_user := metro_user.query.filter_by(email = form_username).first(): 
					if bcrypt.checkpw(form_password.encode(), logged_user.password):
							login_user(logged_user)
							session['user'] = flask_login.current_user.id
					

				if flask_login.current_user.is_authenticated:
					return redirect(url_for("index")) #Login successful
				
				return render_template("login.html", err = "One of the credentials you've entered is incorrect!")

			return render_template("login.html", err = "Please fill the blank fields. nice try :)") #If the user penetrated front end protection -> Required
		return render_template("login.html", err = "")
	return redirect(url_for("index"))

@app.route("/register", methods=['GET', 'POST'])
def register():
	# DONT FORGET TO VALIDATE USER AND PASSWORD LENGTH BEFORE -> MAX 12 CHAR FOR USER UNLIMITED PASS?
	if not flask_login.current_user.is_authenticated:
		if request.method == "POST":
			regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
			form_username = request.form["username"]
			form_password = request.form["password"]
			form_email = request.form["email"]
			if len(form_password) >= 8 and len(form_username) <= 12 and re.search(regex, form_email):
				if metro_user.query.filter_by(username = form_username).first():
					return render_template("register.html", err = "Username already exists.")
				elif metro_user.query.filter_by(email = form_email).first():
					return render_template("register.html", err = "Email already exists.")
				
				hashed_password = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt())
				db.session.add(metro_user(username = form_username, password = hashed_password, email = form_email))
				db.session.commit()
				return redirect(url_for("login"))
			else:
				return render_template("register.html", err ="Invalid Input, Nice Try :)")

		return render_template("register.html")
	return redirect(url_for("index"))

@app.route("/features")
def features():
	return render_template("features.html")

@app.route("/support")
@login_required
def support():
	return render_template("support.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	session.pop('user', None)
	return redirect(url_for("index"))

# TEMP
@app.route("/create_chat/<num>")
@login_required
def create_chat(num):
	#Check if the chat already exists, if not create new one.
	if not metro_chat.query.filter_by(title = num).first():
		curr_time = datetime.now().strftime("%d/%m/%y") 
		curr_chat = metro_chat(string_id = f"random{num}", title=num, file_dir = f"{num}.data", time_created = curr_time)
		letters = string.ascii_letters
		curr_chat.string_id = ''.join(random.choice(letters) for i in range(10))
		db.session.add(curr_chat)
		db.session.commit()
		# Must be seperated to after the chat recieves id when commited firstly.
		curr_chat.string_id += str(curr_chat.id)
		db.session.commit()

	#Gets the created chat and checks if the user already exists in the chat list, if not adds him
	curr_chat = metro_chat.query.filter_by(title=num).first()
	if curr_chat:
		print(curr_chat.chat_backref)
		print(type(curr_chat.chat_backref))
		if flask_login.current_user not in curr_chat.chat_backref:
			curr_chat.chat_backref.append(flask_login.current_user)
			db.session.commit()
		else:
			print("user already exists in the chat!")
	return redirect(url_for("index"))

# TEMP
@app.route("/show_chat")
@login_required
def show_chat():
	for chat in flask_login.current_user.chat_list: # access to related users from chat
		print(chat.title)
		print("-----")
		for user in chat.chat_backref:
			print(user.username)
		print("--END--")
		print("   ")
		#print(flask_login.current_user.chat_list[0]) access to related chats from user
	return redirect(url_for("index"))

@app.route("/<name>")
@app.errorhandler(404)
def something(name):
	return render_template("error/404.html", url = name)
