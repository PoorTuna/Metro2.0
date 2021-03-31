from flask import Flask
# Time module
from datetime import timedelta
# Database module:
from flask_sqlalchemy import SQLAlchemy
# Flask Login Manager module:
from flask_login import LoginManager
# Flask IO:
from flask_socketio import SocketIO

# Eventlet message handler
import eventlet
eventlet.monkey_patch()

# App init and config:
app = Flask(__name__)
app.config['SECRET_KEY'] = "somethingverysecure"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///metro.db"
app.permanent_session_lifetime = timedelta(days = 3) # Define how long a permanent session last in the system.


#Flask SocketIO:
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

#SQLAlchemy FLASK:
db = SQLAlchemy(app)

#Flask login manager:
login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
	from . import routes
	db.create_all()