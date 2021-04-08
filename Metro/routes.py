# Flask imports
from flask import redirect, url_for, render_template, request,session, flash
# Database models imports
from .models import db, metro_user, metro_chat, metro_association_table, login_manager
# Password hashing import
import bcrypt
# Flask-Login imports
import flask_login
from flask_login import login_user, login_required, logout_user
# Flask Socket IO imports
from . import socketio
from flask_socketio import send, emit, join_room, leave_room, close_room, rooms, disconnect, rooms
# Import app in a way to prevent circular imports
from flask import current_app as app
# Chat ids random string imports
import random
import string
# Date and Time import
from datetime import datetime

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for("index"))

@app.route("/")
def index():
	if flask_login.current_user.is_authenticated:
		#Checks on whether the user is in the chat
		chats = []
		for item in flask_login.current_user.chat_list:
				for user in item.chat_backref:
					if user == flask_login.current_user:
						chats.append(item) 

		return render_template("index.html", chats = chats)
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
			flask_login.logout_user()
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
			form_username = request.form["username"]
			form_password = request.form["password"]
			form_email = request.form["email"]
			if metro_user.query.filter_by(username = form_username).first():
				return render_template("register.html", err = "Username already exists.")
			elif metro_user.query.filter_by(email = form_email).first():
				return render_template("register.html", err = "Email already exists.")
			
			hashed_password = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt())
			db.session.add(metro_user(username = form_username, password = hashed_password, email = form_email))
			db.session.commit()
			return redirect(url_for("login"))

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

#TEMP
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

#TEMP
@app.route("/show_chat/<num>")
@login_required
def show_chat(num):
	curr_chat = metro_chat.query.filter_by(title=num).first()
	if curr_chat:
		for user in curr_chat.chat_backref: # access to related users from chat
			print(user.username)
		print(curr_chat.string_id)
		print(curr_chat.time_created)
		print(curr_chat.title)
		#print(flask_login.current_user.chat_list[0]) access to related chats from user
	return redirect(url_for("index"))

@app.route("/<name>")
@app.errorhandler(404)
def something(name):
	return render_template("error/404.html", url = name)

# Socket IO connect handler
@socketio.on('connect')
def handle_connect():
	print(f"{flask_login.current_user} : {flask_login.current_user.username} has connected with session id {request.sid}")
	flask_login.current_user._session_id = request.sid
	db.session.commit()
	session['chat_id'] = 'general'
	join_room(session['chat_id'])

# Socket IO disconnect handler
@socketio.on('disconnect')
def handle_disconnect():
	print(f"{flask_login.current_user} : {flask_login.current_user.username} has disconnected.")
	flask_login.current_user._session_id = None
	db.session.commit()
	# Change back to general chat after user disconnects
	leave_room(session['chat_id'])
	session['chat_id'] = "general"
	join_room(session['chat_id'])
			
# Socket IO recive handler
@socketio.on("message")
def handle_message(msg):
	print("dxd")
	refined_msg = msg.split(" ")

	# Command Structure
	if refined_msg[0][0] == "/":
		# Whisper System
		if len(refined_msg) >= 3:
			
			if refined_msg[0] == "/w":
				message = msg[len(refined_msg[0]) + len(refined_msg[1]) + 2:]

				recipient = metro_user.query.filter_by(username = refined_msg[1]).first()
				if recipient:
					if recipient._session_id:
						emit("private_message", f"{flask_login.current_user.username} : {message}", room=recipient._session_id)
						emit("private_message", f"To {recipient.username} : {message}", room=flask_login.current_user._session_id)
					else:
						emit('private_message', f"User : {recipient.username} is not online!")
				else:
					emit('private_message', f"User : {refined_msg[1]} does not exist!")
		else:
			emit('private_message', f"Invalid Command {refined_msg[0]}")

	# Normal Messages:
	elif msg:
		if flask_login.current_user.is_authenticated:
			emit("message", f"{flask_login.current_user.username} : {msg}", room=session['chat_id'])
		else:
			emit("message", f"Anonymous : {msg}", room=session['chat_id'])

# Socket IO change chat handler
@socketio.on('join_private')
def recv_private_chatname(cid):
	if cid != "general":
		if curr_chat := metro_chat.query.filter_by(string_id = cid).first():
			if flask_login.current_user in curr_chat.chat_backref:
				leave_room(session['chat_id'])
				session['chat_id'] = cid
				join_room(session['chat_id'])

	else:
		leave_room(session['chat_id'])
		session['chat_id'] = "general"
		join_room(session['chat_id'])
			