
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
app = Flask(_name_)

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

#TO CREATE COMPETITON

#TO DO MANAGE COMPETITON

#TO DO ENTER COMPETITON

#TO DO LOG IN

#TO DO LOG OUT

# Register
@app.route("/register", method=["GET", "POST"])
def register()
    
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

        # add new user to database
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        dob = request.form.get("dob")
        if request.form.get("organizer"):
            organizer = int(1)
        else:
            organizer = int(0)
        if request.form.get("competitor"):
            competitor = int(1)
        else:
            competitor = int(0)
        


