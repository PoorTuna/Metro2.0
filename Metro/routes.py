from flask import redirect, url_for, render_template, request,session, flash
from .models import db, metro_user, login_manager
import bcrypt
import flask_login
from flask_login import login_user, login_required, logout_user
from . import socketio
from flask_socketio import send, emit, join_room, leave_room, close_room, rooms, disconnect
from flask import current_app as app


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for("index"))

@app.route("/")
def index():
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

# @app.route("/createuser") # Temp
# def createtemp():
# 	temp_user = metro_user(username = "testname", password = "testpass", email = "test@gmail.com")
# 	db.session.add(temp_user)
# 	db.session.commit()
# 	return redirect(url_for("index"))

@app.route("/<name>")
def something(name):
	return render_template("error/404.html", url = name)

@socketio.on('connect')
def handle_connect():
	print("user has connected xd")

@socketio.on('disconnect')
def handle_disconnect():
	print("user has disconnected")

@socketio.on("message")
def handle_message(msg):
	msg = msg.split("SEPERATOR$%XD")
	room_id = msg[1]
	message_recvd = msg[0]
	print(room_id)
	if message_recvd:
		if flask_login.current_user.is_authenticated:
			send(f"{flask_login.current_user.username} : {message_recvd}", broadcast=True)
		else:
			send(f"Anonymous : {message_recvd}", broadcast=True)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)
