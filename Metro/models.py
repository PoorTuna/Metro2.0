# Flask-Login incorporation import + Flask-SQLALCHEMY database reference
from flask_login import UserMixin
from . import db, login_manager
#This file contains models and login structure for the Metro2.0 project

# User class & integration with login manager and data base
metro_association_table = db.Table('user_chats',
db.Column('user_id', db.Integer, db.ForeignKey('metro_user.id')),
db.Column('chat_id', db.String(20), db.ForeignKey('metro_chat.string_id'))
)
metro_admin_association_table = db.Table('user_admin_chats',
db.Column('user_id', db.Integer, db.ForeignKey('metro_user.id')),
db.Column('chat_id', db.String(20), db.ForeignKey('metro_chat.string_id'))
)

metro_game_association_table = db.Table('user_game',
db.Column('user_id', db.Integer, db.ForeignKey('metro_user.id')),
db.Column('game_id', db.String(20), db.ForeignKey('metro_game.string_id'))
)

class metro_user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True) # User ID
	username = db.Column(db.String(12), unique = True, nullable=False) # User Nickname
	email = db.Column(db.String(30), unique = True, nullable=False) # User Email Address
	password = db.Column(db.String(128), nullable=False) # User Password
	_balance = db.Column(db.Integer,default = 50) # User amount of money / balance
	chat_list = db.relationship('metro_chat', secondary=metro_association_table, backref=db.backref('chat_backref', lazy = 'dynamic')) # User list of chats relationship
	chat_admin_list = db.relationship('metro_chat', secondary=metro_admin_association_table, backref=db.backref('chat_admin_backref', lazy = 'dynamic')) # User list of chats he is an admin in relationship
	chat_owner_list = db.relationship('metro_chat', backref  = "chat_owner_backref") # User list of chats he is an owner in relationship 
	_session_id = db.Column(db.String(60), unique = True) # User session id when he connects to the sockets
	theme = db.Column(db.String(30), nullable=False, default = "original") # The current theme he is using
	theme_list = db.Column(db.String(100), nullable=False, default = "original|") # The list of owned themes
	game_list = db.relationship('metro_game', secondary=metro_game_association_table, backref=db.backref('user_list', lazy = 'dynamic')) # User game list.

class metro_chat(db.Model):
	id = db.Column(db.Integer, primary_key = True) # Chat ID
	string_id = db.Column(db.String(20), unique = True, nullable=True) # Chat StringID (for protection)
	file_dir = db.Column(db.String(12), unique = True, nullable=True) # Chat FileDir
	title = db.Column(db.String(25), nullable=False) # The chats name
	time_created = db.Column(db.String(12), nullable=False) # The time when it was created
	owner_id = db.Column(db.Integer,db.ForeignKey('metro_user.id')) # not really usefull by itself

class metro_game(db.Model):
	id = db.Column(db.Integer, primary_key = True) # Game ID
	string_id = db.Column(db.String(20), unique = True, nullable=True) # Game StringID (for protection)
	game_name = db.Column(db.String(25), nullable=False) # Game type / name
	owner_id = db.Column(db.Integer, nullable=True) # not really usefull by itself
	curr_players = db.Column(db.Integer,default = 1) # Amount of current players in the lobby / NOT USED AS OF NOW
	max_players = db.Column(db.Integer,default = 1) # Amount of required players to start a game

class metro_post(db.Model):
	id = db.Column(db.Integer, primary_key = True) # Post ID
	string_id = db.Column(db.String(20), unique = True, nullable=True) # Game StringID (for protection) 
	title = db.Column(db.String(25), nullable=False) # Post Name / Title
	time_created = db.Column(db.String(12), nullable=False) # The time when it was created
	author = db.Column(db.String(12), nullable=False) # The creator's name
	owner_id = db.Column(db.Integer, nullable=True) # The creator's ID

@login_manager.user_loader
def load_user(user_id): # loads the user in the session
	return metro_user.query.get(int(user_id))

