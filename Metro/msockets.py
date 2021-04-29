# Flask Socket IO imports
from . import socketio
from flask_socketio import send, emit, join_room, leave_room, close_room, disconnect, rooms
# Flask imports
from flask import request
# Database models imports
from .models import db, metro_user, metro_chat
from .routes import session
# Flask-Login imports
import flask_login
#Import OS
import os
#Import time
from datetime import datetime,timedelta

# Socket IO connect handler
@socketio.on('connect')
def handle_connect():
	if flask_login.current_user.is_authenticated:
		print(f"{flask_login.current_user} : {flask_login.current_user.username} has connected with session id {request.sid}")
	flask_login.current_user._session_id = request.sid
	db.session.commit()
	session['chatID'] = "general"
	join_room(session['chatID'])
	
# Socket IO disconnect handler
@socketio.on('disconnect')
def handle_disconnect():
	if flask_login.current_user.is_authenticated:
		print(f"{flask_login.current_user} : {flask_login.current_user.username} has disconnected.")
		flask_login.current_user._session_id = None
		db.session.commit()
	# Change back to general chat after user disconnects
	leave_room(session['chatID'])

# Socket IO recive handler
@socketio.on("message")
def handle_message(msg):
	refined_msg = msg.split(" ")

	# Command Structure
	if refined_msg[0][0] == "/":
		# Whisper Messages:
		if refined_msg[0] == "/w":
			if len(refined_msg) >= 3:
				message = msg[len(refined_msg[0]) + len(refined_msg[1]) + 2:]
				recipient = metro_user.query.filter_by(username = refined_msg[1]).first()
				if recipient:
					if recipient != flask_login.current_user:
						if recipient._session_id:
							emit("private_message", f"{flask_login.current_user.username} : {message}", room=recipient._session_id)
							emit("private_message", f"To {recipient.username} : {message}", room=flask_login.current_user._session_id)
						else:
							emit('private_message', f"User : {recipient.username} is not online!")
					else:
						emit('private_message', f"Can't message yourself!")
				else:
					emit('private_message', f"User : {refined_msg[1]} does not exist!")
			else:
				emit('private_message', "Invalid /w format! Try: /w [user] [message]")
		
		# TTS Messages:
		elif refined_msg[0] == "/tts":
			message = msg[len(refined_msg[0])+ 1:]
			emit("announce_message", f"{flask_login.current_user.username} : {message}", room=session['chatID'])

		# Clean Chat:
		elif refined_msg[0] == "/clear" and session['chatID'] != "general":
			if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
				if flask_login.current_user in curr_chat.chat_backref:
					with open(f"Metro/{curr_chat.file_dir}/chat.data", "w") as metro_filehandler:
						metro_filehandler.write("This is the beginning of your conversation!" + '\r\n')
						emit("clean_message", "The chat has been cleaned!", room=session['chatID'])
				else:
					emit("message", "Invalid permissions!", room=flask_login.current_user._session_id)
		
		# Kick member:
		elif refined_msg[0] == "/kick" and session['chatID'] != "general":
			if len(refined_msg) >= 2:
				tokick_name = msg[len(refined_msg[0])+ 1:]
				if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref:
						if tokick := metro_user.query.filter_by(username = tokick_name ).first():
							if tokick != flask_login.current_user:
								if tokick != curr_chat.chat_backref[0]:
									if tokick in curr_chat.chat_backref:
										curr_chat.chat_backref.remove(tokick) # Remove user from the chat ref
										db.session.commit()
										leave_room(session['chatID'], tokick._session_id)
										kick_msg = f"{tokick.username}, has been kicked by  {flask_login.current_user.username}! Farewell."
										emit("message", kick_msg, room=session['chatID'])
										with open(f"Metro/{curr_chat.file_dir}/chat.data", "a+") as metro_filehandler:
											metro_filehandler.write(kick_msg + '\r\n')

										if tokick._session_id:
											emit("private_message", f"You have been kicked from {curr_chat.title}, join any station to continue.", room = tokick._session_id)
									else:
										emit("private_message", "Invalid User!")
								else:
									emit("private_message", "Can't kick the Owner!")
							else:
								emit("private_message", "Can't kick yourself!")
						else:
							emit("private_message", "Invalid User!")
				else:
					emit("private_message", "Invalid permissions!")
			else:
				emit('private_message', "Invalid /kick format! Try: /kick [user]")

		# Invalid Command:
		else:
			emit('private_message', f"Invalid Command {refined_msg[0]}")

	# Normal Messages:
	elif msg:
		if flask_login.current_user.is_authenticated:
			if "chatID" in session:
				if session['chatID'] == "general":
						emit("message", f"{flask_login.current_user.username} : {msg}", room=session['chatID'])
				else:
					if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
						if flask_login.current_user in curr_chat.chat_backref:
							curr_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
							formated_msg = f"{curr_time} | {flask_login.current_user.username} : {msg}"
							if os.path.exists(f"Metro/{curr_chat.file_dir}/chat.data"):
								with open(f"Metro/{curr_chat.file_dir}/chat.data", "a+") as metro_filehandler:
									metro_filehandler.write(formated_msg + '\r\n')
									emit("message", formated_msg, room=flask_login.current_user._session_id)
							else:
								with open(f"Metro/{curr_chat.file_dir}/chat.data", "x") as metro_filehandler:
									metro_filehandler.write("This is the beginning of your conversation!" + '\r\n')
									metro_filehandler.write(formated_msg + '\r\n')
									emit("message", formated_msg, room=flask_login.current_user._session_id)

# Socket IO change chat handler
@socketio.on('join_private')
def recv_private_chatname(cid):
	if cid != "general":
		if curr_chat := metro_chat.query.filter_by(string_id = cid).first():
			if flask_login.current_user in curr_chat.chat_backref:
				leave_room(session['chatID'])
				session['chatID'] = cid
				join_room(session['chatID'])

	elif cid == "general":
		leave_room(session['chatID'])
		session['chatID'] = "general"
		join_room(session['chatID'])
		emit("message", "This station is anonymous. No logs saved.", room=				flask_login.current_user._session_id)

	if session['chatID'] and session['chatID'] != "general":
		if curr_chat := metro_chat.query.filter_by(string_id=session['chatID']).first():
			if flask_login.current_user in curr_chat.chat_backref:
				#Get the chat data to the user.
				if os.path.exists(f"Metro/{curr_chat.file_dir}/chat.data"):
					with open(f"Metro/{curr_chat.file_dir}/chat.data", "a+") as metro_filehandler:
						metro_filehandler.seek(0)
						chat_data = metro_filehandler.readlines()
						for line in chat_data:
							emit("message", line, room=flask_login.current_user._session_id)
				else:
					with open(f"Metro/{curr_chat.file_dir}/chat.data", "x") as metro_filehandler:
						first_msg = "This is the beginning of your conversation!"
						metro_filehandler.write(first_msg + '\r\n')
						emit("message", first_msg, room=				flask_login.current_user._session_id)
				# Return members list:
				for member in curr_chat.chat_backref:
					# Member state : Online / Offline based on their session id
					if member._session_id:
						member_state = "Online"
					else:
						member_state = "Offline"

					emit('join_private_info', member.username + "%seperatorXD" + member_state, room=flask_login.current_user._session_id)
				emit('join_private_info_date_author', f'created by {curr_chat.chat_backref[0].username} on the {curr_chat.time_created}', room=flask_login.current_user._session_id)
@socketio.on('delete_private')
def delete_chat_handle(cid):
	if cid != "general":
		if curr_chat := metro_chat.query.filter_by(string_id = cid).first():
			if flask_login.current_user in curr_chat.chat_backref:
				if os.path.exists(f"Metro/{curr_chat.file_dir}"):
					for metro_file in os.listdir(f"Metro/{curr_chat.file_dir}"):
						os.remove(f"Metro/{curr_chat.file_dir}/{metro_file}")
		
					os.rmdir(f"Metro/{curr_chat.file_dir}")
				db.session.delete(curr_chat)
				db.session.commit()
	