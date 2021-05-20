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
import string
import random

# GAME SECTION SOCKETS
# Socket IO connect handler
@socketio.on('connect_game')
def handle_connect(msg):
	if flask_login.current_user.is_authenticated:
		print(f"{flask_login.current_user} : {flask_login.current_user.username} has connected to the game chat with session id {request.sid}")
	flask_login.current_user._session_id = request.sid
	db.session.commit()
	session['chatID'] = "general_game"
	join_room(session['chatID'])
	
# Socket IO disconnect handler
@socketio.on('disconnect_game')
def handle_disconnect(msg):
	if flask_login.current_user.is_authenticated:
		print(f"{flask_login.current_user} : {flask_login.current_user.username} has disconnected from the game chat.")
		flask_login.current_user._session_id = None
		db.session.commit()
	# Change back to general chat after user disconnects
	leave_room(session['chatID'])

# Socket IO recive handler
@socketio.on("game_message")
def handle_game_message(msg):
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
				emit("announce_message", message, room=session['chatID'])
			else:
				emit('private_message', "Invalid /tts format! Try: /tts [message]")

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

		# Help Command:		
		elif len(refined_msg) == 1 and (refined_msg[0] == "/help" or refined_msg[0] == "/?"):
			permissions = "User: /help ; /? ; /tip ; /bal ; /balance ; /w ; /tts"
			emit("private_message", permissions)
			
		# Invalid Command:
		
		else:
			emit('private_message', f"Invalid Command {refined_msg[0]}, try /help!")

	# Regular Messages:
	elif msg:
		if flask_login.current_user.is_authenticated:
			if "chatID" in session:
					curr_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
					formated_msg = f"{curr_time} | {flask_login.current_user.username} : {msg}"
					emit("game_message", formated_msg, room=session['chatID'])


@socketio.on("game_choose")
def handle_game_choose(game):
	session['currgame'] = game
	letters = string.ascii_letters
	curr_game = metro_game(string_id = None, game_name=game, owner_id = flask_login.current_user.id)
	curr_game.string_id = ''.join(random.choice(letters) for i in range(10))
	curr_game.place =  + flask_login.current_user.id
	db.session.add(curr_game)
	db.session.commit()
	curr_game.place =  curr_game.curr_players + ":" + flask_login.current_user.id
	curr_game.string_id += str(curr_chat.id)
	db.session.commit()
	
@socketio.on("game_start")
def handle_game_started(msg):
	session['startedgame'] = True
	emit("game_start", "started" ,room=session['chatID'])

@socketio.on("game_exit")
def handle_game_started(msg):
	if curr_game := metro_game.query.filter_by(string_id = session['chatID']).first():
		session.pop('currgame', None) # Choose game
		session.pop('startedgame', None) # Start game
		if flask_login.current_user in curr_game.user_list:
			if flask_login.current_user.id == curr_game.owner_id:
				db.session.delete(curr_game)
			else:
				curr_game.user_list.remove(flask_login.current_user)
				emit("message", f"{flask_login.current_user.username} has left the game!" ,room=session['chatID'])
			db.session.commit()

@socketio.on("game_update")
def handle_game_update(cmd):
	if curr_game := metro_game.query.filter_by(string_id = session['chatID']).first():
		if flask_login.current_user in curr_game:
			emit("game_update", cmd, room= session['chatID'])
	


# Socket IO change chat handler
@socketio.on('join_private_game')
def recv_private_chatname(cid):
	if cid != "general_game":
		if curr_game := metro_game.query.filter_by(string_id = cid).first():
			if flask_login.current_user in curr_game.user_list:
				leave_room(session['chatID'])
				session['chatID'] = cid
				join_room(session['chatID'])

	elif cid == "general_game":
		leave_room(session['chatID'])
		session['chatID'] = "general_game"
		join_room(session['chatID'])
		emit("message", "This station is anonymous. No logs saved.", room=				flask_login.current_user._session_id)

	if session['chatID'] and session['chatID'] != "general_game":
		if curr_game := metro_game.query.filter_by(string_id=session['chatID']).first():
			if flask_login.current_user in curr_game.user_list:
				first_msg = "This is the beginning of your conversation!"
				emit("message", first_msg, room=flask_login.current_user._session_id)
				# Return members list:
				for member in curr_game.user_list:
					# Member state : Online / Offline based on their session id
					if member._session_id:
						member_state = "Online"
					else:
						member_state = "Offline"

					emit('join_private_info', member.username + "%seperatorXD" + member_state, room=flask_login.current_user._session_id)

@socketio.on('delete_private_game')
def delete_chat_handle(cid):
	if cid != "general_game":
		if curr_game := metro_game.query.filter_by(string_id = cid).first():
			if flask_login.current_user in curr_game.user_list:
				if flask_login.current_user.id == curr_game.owner_id:
					db.session.delete(curr_game)
					db.session.commit()
				else:
					emit("private_message", "Only the owner can deconstruct this station!")
