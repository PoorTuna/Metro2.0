from flask_login import UserMixin
from . import db, login_manager

# User class & integration with login manager and data base
class metro_user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(12), unique = True, nullable=False)
	email = db.Column(db.String(30), unique = True, nullable=False)
	password = db.Column(db.String(128), nullable=False)
	balance = db.Column(db.Integer,default = 50)

# class metro_chat(db.Model):
# 	pass

@login_manager.user_loader
def load_user(user_id):
	return metro_user.query.get(int(user_id))
