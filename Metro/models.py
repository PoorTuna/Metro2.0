from flask_login import UserMixin
from . import db, login_manager

# User class & integration with login manager and data base
metro_association_table = db.Table('user_chats',
db.Column('user_id', db.Integer, db.ForeignKey('metro_user.id')),
db.Column('chat_id', db.String(20), db.ForeignKey('metro_chat.string_id'))
)
class metro_user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(12), unique = True, nullable=False)
	email = db.Column(db.String(30), unique = True, nullable=False)
	password = db.Column(db.String(128), nullable=False)
	balance = db.Column(db.Integer,default = 50)
	chat_list = db.relationship('metro_chat', secondary=metro_association_table, backref=db.backref('chat_backref', lazy = 'dynamic'))
	_session_id = db.Column(db.String(60), unique = True)

class metro_chat(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	string_id = db.Column(db.String(20), unique = True, nullable=False, default = "")
	file_dir = db.Column(db.String(12), unique = True, nullable=False)
	title = db.Column(db.String(12), unique = True, nullable=False)
	time_created = db.Column(db.String(12), nullable=False)
	# users
	# admins
	# banned_users


@login_manager.user_loader
def load_user(user_id):
	return metro_user.query.get(int(user_id))
