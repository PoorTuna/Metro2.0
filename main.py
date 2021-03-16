# Flask module:
from flask import Flask, redirect, url_for, render_template, request,session, flash
# Time module
from datetime import timedelta
# Database module:
from flask_sqlalchemy import SQLAlchemy
# Flask Login Manager module:
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import flask_login
# Password hashing module:
import bcrypt 

# App init and config:
app = Flask(__name__)
app.config['SECRET_KEY'] = "somethingverysecure"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///metro.db"
app.permanent_session_lifetime = timedelta(days = 3) # Define how long a permanent session last in the system.

#SQLAlchemy FLASK:
db = SQLAlchemy(app)

#Flask login manager:
login_manager = LoginManager()
login_manager.init_app(app)

# User class & integration with login manager and data base
class metro_user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(12), unique = True, nullable=False)
	email = db.Column(db.String(30), unique = True, nullable=False)
	password = db.Column(db.String(128), nullable=False)
	balance = db.Column(db.Integer,default = 50)


@login_manager.user_loader
def load_user(user_id):
	return metro_user.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for("index"))

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if not flask_login.current_user.is_authenticated:
		if request.method == 'POST':
			flask_login.logout_user()
			form_username = request.form["username"]
			form_password = request.form["password"]

			if form_username and form_password: #if the fields weren't empty go ahead and query the database

				# Check if input matches a user in the database:
				if logged_user := metro_user.query.filter_by(username = form_username).first():
					if bcrypt.checkpw(form_password.encode(), logged_user.password):
							login_user(logged_user)

				if logged_user := metro_user.query.filter_by(email = form_username).first(): 
					if bcrypt.checkpw(form_password.encode(), logged_user.password):
							login_user(logged_user)
					

				if flask_login.current_user.is_authenticated:
					return render_template("login.html", err = "Login successful redirecting...") #Login successful
				
				return render_template("login.html", err = "One of the credentials you've entered is incorrect!")

			return render_template("login.html", err = "Please fill the blank fields. nice try :)") #If the user penetrated front end protection -> Required
		return render_template("login.html", err = "")
	return redirect(url_for("index"))


@app.route("/register", methods=['GET', 'POST'])
def register():
	# DONT FORGET TO VALIDATE USER AND PASSWORD LENGTH BEFORE -> MAX 12 CHAR FOR USER UNLIMITED PASS?
	if not flask_login.current_user.is_authenticated:
		if request.method == "POST":
			form_username = request.form["username"]
			form_password = request.form["password"]
			form_email = request.form["email"]
			if metro_user.query.filter_by(username = form_username).first():
				return render_template("register.html", err = "Username already exists.")
			elif metro_user.query.filter_by(email = form_email).first():
				return render_template("register.html", err = "Email already exists.")
			
			hashed_password = bcrypt.hashpw(form_password.encode(), bcrypt.gensalt())
			db.session.add(metro_user(username = form_username, password = hashed_password, email = form_email))
			db.session.commit()
			return redirect(url_for("login"))

		return render_template("register.html")
	return redirect(url_for("index"))
	

@app.route("/features")
def features():
	return render_template("features.html")

@app.route("/support")
@login_required
def support():
	return render_template("support.html")


@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))

@app.route("/createuser") # Temp
def createtemp():
	temp_user = metro_user(username = "testname", password = "testpass", email = "test@gmail.com")
	db.session.add(temp_user)
	db.session.commit()
	return redirect(url_for("index"))

@app.route("/<name>")
def something(name):
	return render_template("error/404.html", url = name)

# @app.errorhandler(404)
# def error404(error):
# 	return render_template("error/404.html", err = error)


if __name__ == "__main__":
	db.create_all()
	app.run(host='0.0.0.0', port=27030, debug=True)
