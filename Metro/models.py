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

class metro_user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(12), unique = True, nullable=False)
	email = db.Column(db.String(30), unique = True, nullable=False)
	password = db.Column(db.String(128), nullable=False)
	_balance = db.Column(db.Integer,default = 50)
	chat_list = db.relationship('metro_chat', secondary=metro_association_table, backref=db.backref('chat_backref', lazy = 'dynamic'))
	chat_admin_list = db.relationship('metro_chat', secondary=metro_admin_association_table, backref=db.backref('chat_admin_backref', lazy = 'dynamic'))
	chat_owner_list = db.relationship('metro_chat', backref  = "chat_owner_backref")
	_session_id = db.Column(db.String(60), unique = True)
	theme = db.Column(db.String(30), nullable=False, default = "original")
	theme_list = db.Column(db.String(100), nullable=False, default = "original|")

class metro_chat(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	string_id = db.Column(db.String(20), unique = True, nullable=True)
	file_dir = db.Column(db.String(12), unique = True, nullable=True)
	title = db.Column(db.String(25), nullable=False)
	time_created = db.Column(db.String(12), nullable=False)
	owner_id = db.Column(db.Integer,db.ForeignKey('metro_user.id')) # not really usefull by itself

class metro_game(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	string_id = db.Column(db.String(20), unique = True, nullable=True)
	game_name = db.Column(db.String(25), nullable=False)
	started = db.Column(db.Boolean, nullable=False, default=False)
	user_list = db.relationship('metro_user', backref  = "games_list")
	owner_id = db.Column(db.Integer,db.ForeignKey('metro_user.id')) # not really usefull by itself

class metro_game_user(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(12), unique = True, nullable=False)
	x = db.Column(db.Integer, nullable=False)
	y = db.Column(db.Integer, nullable=False)
	width = db.Column(db.Integer, nullable=False)
	height = db.Column(db.Integer, nullable=False)
	place = db.Column(db.Integer, nullable=False) # What object is he in the game, e.g. 1,2,3,4...
	
	def check_collision(self,x,y,width,height):
		'''
		Param:
		x,y,width,height : Integer
		This functions calculates if the current object collides with another object
		returns true if it does, else false.
		'''
		if ( x >= self.x and x <= self.x + self.width ) or ( x + width >= self.x and x + width <= self.x + self.width):
			if ( y >= self.y and y <= self.y + self.height ) or ( y + height >= self.y and y + height <= self.y + self.height):
				return True
		return False

		




@login_manager.user_loader
def load_user(user_id):
	return metro_user.query.get(int(user_id))
