
# Flask Socket IO imports
from . import socketio
from flask_socketio import send, emit, join_room, leave_room, close_room, disconnect, rooms
# Flask imports
from flask import request,session
# Database models imports
from .models import db, metro_user, metro_chat
# Flask-Login imports
import flask_login

# Socket IO connect handler
@socketio.on('connect')
def handle_connect():
	print(f"{flask_login.current_user} : {flask_login.current_user.username} has connected with session id {request.sid}")
	flask_login.current_user._session_id = request.sid
	db.session.commit()
	try:
		if session['chat_id']:
			if curr_chat := metro_chat.query.filter_by(_session_id=session['chat_id']).first():
				emit('last_title', curr_chat.title)
				join_room(session['chat_id'])
			
			else:
				emit('last_title', 'general')
				session['chat_id'] = 'general'
				join_room(session['chat_id'])
	except:
		emit('last_title', 'general')
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

# Socket IO recive handler
@socketio.on("message")
def handle_message(msg):
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

#@socketio.on('create_chat')
#def recv_chat_details(chat):
#	chat = chat.split("%$#seprtxd")
	