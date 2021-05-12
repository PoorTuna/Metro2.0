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

#This file contains socket handling and communications for the Metro2.0 project

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
			if len(refined_msg) >= 2:
				message = msg[len(refined_msg[0])+ 1:]
				curr_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
				message = f"{curr_time} | {flask_login.current_user.username} : {message}"
				if session['chatID'] != "general":
					if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
						with open(f"Metro/{curr_chat.file_dir}/chat.data", "a+") as metro_filehandler:
							metro_filehandler.write(message + '\r\n')

				emit("announce_message", message, room=session['chatID'])
			else:
				emit('private_message', "Invalid /tts format! Try: /tts [message]")
		

		# Clean Chat:
		elif refined_msg[0] == "/clear" and session['chatID'] != "general":
			if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
				if flask_login.current_user in curr_chat.chat_backref:
					if flask_login.current_user == curr_chat.chat_owner_backref:
						with open(f"Metro/{curr_chat.file_dir}/chat.data", "w") as metro_filehandler:
							metro_filehandler.write("This is the beginning of your conversation!" + '\r\n')
							emit("clean_message", "The chat has been cleaned!", room=session['chatID'])
					else:
						emit("private_message", "Only the owner can clean the station log!")
				else:
					emit("private_message", "Insufficient permissions!")
		
		# Kick member:
		elif refined_msg[0] == "/kick" and session['chatID'] != "general":
			if len(refined_msg) >= 2:
				tokick_name = msg[len(refined_msg[0])+ 1:]
				if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref:
						if flask_login.current_user in curr_chat.chat_admin_backref:
							if tokick := metro_user.query.filter_by(username = tokick_name ).first():
								if tokick != flask_login.current_user:
									if tokick != curr_chat.chat_owner_backref:
										if tokick in curr_chat.chat_backref:
											curr_chat.chat_backref.remove(tokick) # Remove user from the chat ref
											curr_chat.chat_admin_backref.remove(tokick) # Remove user from the admin chat ref

											db.session.commit()
											leave_room(session['chatID'], tokick._session_id)
											kick_msg = f"{tokick.username}, has been expelled from the station by {flask_login.current_user.username}! Farewell."
											emit("message", kick_msg, room=session['chatID'])
											with open(f"Metro/{curr_chat.file_dir}/chat.data", "a+") as metro_filehandler:
												metro_filehandler.write(kick_msg + '\r\n')

											if tokick._session_id:
												emit("private_message", f"You have been expelled from {curr_chat.title}, join any station to continue.", room = tokick._session_id)
										else:
											emit("private_message", "Invalid User!")
									else:
										emit("private_message", "Can't kick the Owner!")
								else:
									emit("private_message", "Can't kick yourself!")
							else:
								emit("private_message", "Invalid User!")
						else:
							emit("private_message", "Insufficient permissions!")
			else:
				emit('private_message', "Invalid /kick format! Try: /kick [user]")
		
		# Op member
		elif refined_msg[0] == "/op" and session['chatID'] != "general":
			if len(refined_msg) >= 2:
				toop_name = msg[len(refined_msg[0])+ 1:]
				if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref: # check if the current user in chat
						if flask_login.current_user in curr_chat.chat_admin_backref: # check if current user is an admin
							if toop := metro_user.query.filter_by(username = toop_name ).first(): # check if the member exists
								if toop in curr_chat.chat_backref: # check if the member is in the chat
									if toop not in curr_chat.chat_admin_backref:
										if toop == curr_chat.chat_owner_backref: # check if the member is
											emit('private_message', "Owner is already OP!")
										else:
											#OP HERE
											curr_chat.chat_admin_backref.append(toop)
											db.session.commit()
											emit('private_message', f"{toop.username} has been added to the administration!")
											if toop._session_id:
												emit('private_message', f"you have been added to the administration by {flask_login.current_user.username}!", room =toop._session_id)
											
									else:
										emit('private_message', f"{toop.username} is already OP!")
								else:
									emit("private_message", "Invalid User!")
							else:
								emit("private_message", "Invalid User!")
						else:
							emit("private_message", "Insufficient permissions!")
			else:
				emit('private_message', "Invalid /op format! Try: /op [user]")

		# Deop member
		elif refined_msg[0] == "/deop" and session['chatID'] != "general":
			if len(refined_msg) >= 2:
				todeop_name = msg[len(refined_msg[0])+ 1:]
				if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref: # check if the current user in chat
						if flask_login.current_user in curr_chat.chat_admin_backref: # check if current user is an admin
							if todeop := metro_user.query.filter_by(username = todeop_name ).first(): # check if the member exists
								if todeop in curr_chat.chat_backref: # check if the member is in the chat
									if todeop in curr_chat.chat_admin_backref:
										if todeop == curr_chat.chat_owner_backref: # check if the member is
											emit('private_message', "Can't de-op the Owner ")
										else:
											#DEOP HERE
											curr_chat.chat_admin_backref.remove(todeop)
											db.session.commit()
											emit('private_message', f"{todeop.username} has been expelled from the administration by {flask_login.current_user.username}!")
									else:
										emit('private_message', f"{todeop.username} is not OP!")

								else:
									emit("private_message", "Invalid User!")
							else:
								emit("private_message", "Invalid User!")
						else:
							emit("private_message", "Insufficient permissions!")
			else:
				emit('private_message', "Invalid /deop format! Try: /deop [user]")
		
		# Balance Command:
		elif refined_msg[0] == "/bal" or refined_msg[0] == "/balance":
			emit("private_message", f"You have {flask_login.current_user._balance} bullets")

		# Tip user in room Command:
		elif refined_msg[0] == "/tip":
			if len(refined_msg) >= 3:
				tip_amount = msg[len(refined_msg[0]) + len(refined_msg[1]) + 2:]
				if tip_amount.isnumeric(): # check if the amount contains numbers only
					if tip_recipient := metro_user.query.filter_by(username=refined_msg[1]).first():
						if tip_recipient != flask_login.current_user:
							if tip_recipient._session_id:
								if flask_login.current_user._balance >= int(tip_amount) + 50: # base safety amount
									flask_login.current_user._balance -= int(tip_amount)
									tip_recipient._balance += int(tip_amount)
									db.session.commit()
									emit('private_message', f"You tipped {tip_amount} bullets to {tip_recipient.username}!")

									emit('private_message', f"{flask_login.current_user.username} tipped {tip_amount} bullets to you!", room=tip_recipient._session_id)

								else:
									emit('private_message', "Insufficient bullets!")
							else:
								emit('private_message', "User is Offline!")
						else:
							emit('private_message', "Can't tip yourself!")
					else:
						emit('private_message', "Invalid user!")

				else:
					emit('private_message', "Invalid amount!")

			else:
				emit('private_message', "Invalid /tip format! Try: /tip [user] [amount]")
		# Show online admins Command:		
		elif len(refined_msg) == 1 and refined_msg[0] == "/admins" and session['chatID'] != "general":
			if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first(): # check if the chat exists.
				if flask_login.current_user in curr_chat.chat_backref: # check if user is in the chat list
					admins = "Online Admins : "
					for admin in curr_chat.chat_admin_backref:
						if admin._session_id:
							admins += admin.username + " | "

					emit("private_message", admins)
		
		# Show online members Command:	
		elif len(refined_msg) == 1 and refined_msg[0] == "/members" and session['chatID'] != "general":
			if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first(): # check if the chat exists.
				if flask_login.current_user in curr_chat.chat_backref: # check if user is in the chat list
					members = "Online Members : "
					for member in curr_chat.chat_backref:
						if member._session_id:
							members += member.username + " | "

					emit("private_message", members)
				
		# Help Command:		
		elif len(refined_msg) == 1 and (refined_msg[0] == "/help" or refined_msg[0] == "/?"):
			if session['chatID'] != "general":
				if curr_chat := metro_chat.query.filter_by(string_id = session['chatID']).first():
					if flask_login.current_user in curr_chat.chat_backref:
						permissions = "User: /help ; /? ; /members ; /admins ; /tip ; /bal ; /balance ; /w ; /tts"
						if flask_login.current_user in curr_chat.chat_admin_backref:
							permissions += " | Administrator: /op ; /deop ; /kick"
							if flask_login.current_user == curr_chat.chat_owner_backref:
								permissions += " | Owner: /clear"

						emit("private_message", permissions)
						
			elif session['chatID'] == "general":
				permissions = "User: /help ; /? ; /tip ; /bal ; /balance ; /w ; /tts"
				emit("private_message", permissions)
			
		# Invalid Command:
		
		else:
			emit('private_message', f"Invalid Command {refined_msg[0]}, try /help!")

	# Regular Messages:
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
						emit("message", first_msg, room=flask_login.current_user._session_id)
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
				if flask_login.current_user == curr_chat.chat_owner_backref:
					if os.path.exists(f"Metro/{curr_chat.file_dir}"):
						for metro_file in os.listdir(f"Metro/{curr_chat.file_dir}"):
							os.remove(f"Metro/{curr_chat.file_dir}/{metro_file}")
			
						os.rmdir(f"Metro/{curr_chat.file_dir}")
					db.session.delete(curr_chat)
					db.session.commit()
				else:
					emit("private_message", "Only the owner can deconstruct this station!")

# Scrapped for now
@socketio.on('send_voice')
def handle_voice(voice):
	emit("recv_voice", voice,  broadcast = True)

# Store route:
@socketio.on('buy_palette')
def handle_voice(palette):
	if palette not in flask_login.current_user.theme_list:
		if flask_login.current_user._balance >= 25:
			flask_login.current_user._balance -= 25
			session['bullets'] = flask_login.current_user._balance
			flask_login.current_user.theme_list += palette + "|"
			db.session.commit()
			emit("buy_palette", "Successful Purchase!")
		else:
			emit("buy_palette", "Insufficient Funds!")
	else:
		emit("buy_palette", "You already own this palette!")
