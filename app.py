
# import libraries etc
import os

from cs50 import SQL
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# import helper files
from helpers import apology, login_required

# configure application
app = Flask(__name__)

# Configure session to use file system 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
db = SQL("sqlite:///easycomp.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#TO DO INDEX
@app.route("/")
def index():
    return apology("Not finished", 400)

#TO CREATE COMPETITON
@app.route("/create")
def create():
    return apology("Not finished", 400)

#TO DO MANAGE COMPETITON
@app.route("/manage")
def manage():
    return apology("Not finished", 400)

#TO DO ENTER COMPETITON
@app.route("/enter")
def enter():
    return apology("Not finished", 400)

# login
@app.route("/login", methods=["GET", "POST"])
def login():

    # forget user_id
    session.clear()

    # user reached via POST
    if request.method == "POST":

        # ensure username
        if not request.form.get("username"):
            return apology("username required", 403)
        
        # ensure password
        if not request.form.get("password"):
            return apology ("password required", 403)
        
        # query db for user
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # ensure username exist and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        # store user_id as session user_id
        session["user_id"] = rows[0]["id"]

        # redirect to front page
        return redirect("/")
    
    # user reached via GET
    else:
        return render_template("login.html")

#TO DO LOG OUT
@app.route("/logout")
def logout():
    return apology("Not finished", 400)

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    
    # if reached via POST
    if request.method == "POST":

        # check for username creation
        if not request.form.get("username"):
            return apology("username creation required", 400)
        
        # check for duplicate username
        rows = db.execute("SELECT * FROM USERS WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            return apology("username already taken", 400)
        
        # check for password creation
        elif not request.form.get("passsword"):
            return apology("password creation required", 400)
        
        # check for password match via confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        
        # hash password
        password = request.form.get("password")
        hash = generate_password_hash(password)

        # get values for db
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        DOB = request.form.get("dob")
        # Boolean values for use type, competitor and/or organizer
        if request.form.get("organizer"):
            organizer = int(1)
        else:
            organizer = int(0)
        if request.form.get("competitor"):
            competitor = int(1)
        else:
            competitor = int(0)
        # add new user to db
        rows = db.execute("INSERT INTO users (username, hash, firstname, lastname, DOB, organizer, competitor) VALUES (?,?,?,?,?,?,?)",
                           username, hash, firstname, lastname, DOB, organizer, competitor)
        
        # redirect to long
        return redirect("/")

    # if reached by get
    else:
        return render_template("register.html")


