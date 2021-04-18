from flask import Flask, session
# Time module
from datetime import timedelta,datetime
# Database module:
from flask_sqlalchemy import SQLAlchemy
# Flask Login Manager module:
from flask_login import LoginManager
# Flask IO:
from flask_socketio import SocketIO
# Server side sessions flask
from flask_session import Session
# Eventlet message handler
import eventlet
eventlet.monkey_patch()

# App init and config:
app = Flask(__name__)
app.config['SECRET_KEY'] = "somethingverysecure"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///metro.db"
app.config['SESSION_TYPE'] = "sqlalchemy"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 3)
app.config['SESSION_PERMANENT'] = True

#SQLAlchemy FLASK:
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db

# Server side sessions:
Session(app)

#Flask SocketIO:
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*", manage_session=False)

#Flask login manager:
login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
	from . import routes
	db.create_all()
