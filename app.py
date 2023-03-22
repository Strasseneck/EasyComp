
# import libraries etc
import os

from cs50 import SQL
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import math
from tempfile import mkdtemp
import random
from werkzeug.security import check_password_hash, generate_password_hash

# import helper files
from helpers import apology, login_required, nextpowerof2

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


# index
@app.route("/")
@login_required
def index():

    # select user data
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    
    # get user data to display
    username = rows[0]["username"]
    firstname = rows[0]["firstname"]
    lastname = rows[0]["lastname"]
    
    # select user's created competitions to display
    competitions = []
    rows = db.execute("SELECT * FROM competitions WHERE organizer_id = ?", session["user_id"])
    for i in range(len(rows)):
        competition = rows[i]["name"]
        competitions.append(competition)

    # select user's entered comps and divisions
    rows = db.execute("SELECT DISTINCT comp_name, name FROM divisions INNER JOIN competitors on competitors.division_id = divisions.id WHERE competitor_id = ?", session["user_id"])
    entered = rows

    # render template
    return render_template("index.html", username=username, firstname=firstname, lastname=lastname, competitions=competitions, entered=entered)
   

# create competition
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():

    # if reached via post
    if request.method == "POST":

        # check for compname
        if not request.form.get("compname"):
            return apology("competition name creation required", 400)
        
        # check for duplicate compname
        rows = db.execute("SELECT * FROM competitions WHERE name = ?", request.form.get("compname"))
        if len(rows) > 0:
            return apology("competition with same name already exists", 400)
        else:
            compname = request.form.get("compname")
        
        # get format 
        format = request.form["formatselect"]
        if format == 'singleround':
            format = 'Single Round Elimination'
        elif format == 'roundrobin':
            format = 'Round Robin'

        # add new competition to competitions db
        rows = db.execute("INSERT INTO competitions (name, format, organizer_id) VALUES (?,?,?)", compname, format, session["user_id"] )

        # get comp_id for divisions db
        rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name = ?", compname)
        comp_id = rows[0]["id"]

         # get belt classes
        beltclasses = request.form.getlist("beltdivision")
        
        # get weight classes
        weightclasses = request.form.getlist("weightclass")

        # iterate through lists and add to divisions database
        for i in range(len(beltclasses)):
            for j in range(len(weightclasses)):
                division = beltclasses[i] + weightclasses[j]
                division = division.replace("-"," ")
                rows = db.execute("INSERT INTO divisions (name, comp_id, comp_name) VALUES (?,?,?)", division, comp_id, compname)
        
        return redirect("/")
     # if reached by get
    else:
        return render_template("create-comp.html")

# view competition
@app.route("/view", methods=["GET"])
@login_required
def view():

    # get all competitions
    competitions = db.execute("SELECT DISTINCT name, format FROM competitions")

    # render template
    return render_template("view-comp.html", competitions=competitions)

# view registrations for competition
@app.route("/registrations/<competition>", methods=["GET"])
@login_required
def registrations(competition):

    #get id and name of competition
    rows = db.execute("SELECT DISTINCT id, name FROM competitions WHERE name LIKE ?", competition)
    comp_id = rows[0]["id"]
    compname = rows[0]["name"]
    
    divisions = {}
    divnames = []
    divids = []
    # get division name and id
    rows = db.execute("SELECT DISTINCT id, name FROM divisions INNER JOIN competitors on competitors.division_id = divisions.id WHERE competition_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        for j in range(len(rows)):
            competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
            competitors.append(competitor)
        # add values to divisions dict        
        divisions[divname] = competitors
    
    # check if brackets available
    matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
    if len(matches) > 0:
        return render_template("view-comp-registrations.html", compname=compname, divisions=divisions, divnames=divnames, matches=matches)
    else:
        return render_template("view-comp-registrations.html", compname=compname, divisions=divisions, divnames=divnames)

# manage competition
@app.route("/manage", methods = ["GET"])
@login_required
def manage():
    divisions = {}
    divnames = []
    divids = []
    # select competitons created by user
    competitions = db.execute("SELECT DISTINCT name, format FROM competitions WHERE organizer_id = ?", session["user_id"])

    comprows = db.execute("SELECT DISTINCT id FROM competitions WHERE organizer_id = ?", session["user_id"])
    for i in range(len(comprows)):
        compid = comprows[0]["id"]
        # get division name and id
        rows = db.execute("SELECT DISTINCT id, name FROM divisions INNER JOIN competitors on competitors.division_id = divisions.id WHERE competition_id = ?", compid)
        for i in range(len(rows)):
            divname = rows[i]["name"]
            divnames.append(divname)
            divid = rows[i]["id"] 
            divids.append(divid)
    
    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        for j in range(len(rows)):
            competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
            competitors.append(competitor)
        # add values to divisions dict        
        divisions[divname] = competitors

    #render template
    return render_template("manage-comp.html", divisions=divisions, competitions=competitions)

# start  competition
@app.route("/start/<competition>", methods=["GET", "POST"])
@login_required
def start(competition):
    compname = competition  
    #generate participants list
    #get id and name of competition
    rows = db.execute("SELECT DISTINCT id, name FROM competitions WHERE name LIKE ?", competition)
    comp_id = rows[0]["id"]
    divisions = {}
    divnames = []
    divids = []

    # check if brackets have already been generated
    matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
    if len(rows) > 0:
        return render_template("brackets.html", matches=matches, compname=compname)
    
    # get division name and id
    rows = db.execute("SELECT DISTINCT id, name FROM divisions INNER JOIN competitors on competitors.division_id = divisions.id WHERE competition_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        for j in range(len(rows)):
            competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
            competitors.append(competitor)
        # add values to divisions dict        
        divisions[divname] = competitors


    # master loop for each division
    for i in range(len(divisions)):
        participants = []
        # get number of participants for each division
        divname = divnames[i]
        participants = divisions[divname]
        totalmatches = len(participants)
        # find nearest power of 2 to determine byes
        powerof2 = nextpowerof2(totalmatches)
        byes = powerof2 - totalmatches
        matchesrd = int((totalmatches - byes) / 2)
        # schedule matches first round
        for i in range(matchesrd):
            competitor1 = random.choice(participants)
            participants.remove(competitor1)
            competitor2 = random.choice(participants)
            participants.remove(competitor2)
           # get competitor ids for matches table
            lastname1 = competitor1.split()
            lastname1 = lastname1[1]
            lastname2 = competitor2.split()
            lastname2 = lastname2[1]
            rows = db.execute("SELECT DISTINCT id FROM users WHERE lastname = ? OR lastname = ?", lastname1, lastname2)
            id1 = rows[0]["id"]
            id2 = rows[1]["id"]
            # get div_id
            rows = db.execute("SELECT DISTINCT id FROM divisions WHERE name = ? AND comp_id = ?", divname, comp_id)
            div_id = rows[0]["id"]
            # insert match into matches table
            db.execute("INSERT INTO matches (comp_id, div_id, div_name, competitor1_name, competitor2_name, competitor1_id, competitor2_id) VALUES (?,?,?,?,?,?,?)",
                        comp_id, div_id, divname, competitor1, competitor2, id1, id2) 

    matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
    return render_template("brackets.html", matches=matches, compname=compname)

# TO DO START MATCH
@app.route("/match/<id>", methods=["POST"])
@login_required
def match(id):
    # get match info
    rows = db.execute("SELECT DISTINCT competitor1_name, competitor2_name FROM matches WHERE id = ?", id)
    match = rows[0]

    return render_template("match.html", match=match)

    

# enter competition
@app.route("/enter", methods=["GET"])
@login_required
def enter():

    # get info about competitions available to enter
    competitions = db.execute("SELECT DISTINCT name, format FROM competitions")
    
    # render template enter comp
    return render_template("enter-comp.html", competitions=competitions)

@app.route("/divisions/<name>", methods=["GET"])
@login_required
def divisions(name):

    #get id and name of competition
    rows = db.execute("SELECT DISTINCT id, name FROM competitions WHERE name LIKE ?", name)
    comp_id = rows[0]["id"]
    compname = rows[0]["name"]
    
    # get division info
    divisions = []
    rows = db.execute("SELECT DISTINCT name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        division = rows[i]["name"]
        divisions.append(division)
    
    # render template
    return render_template("divisions.html", divisions=divisions, compname=compname)

@app.route("/divisions/enterdivision/<name>", methods=["GET"])
@login_required
def enterdivision(name):

    names = name.split(":")
    comp_name = names[0]
    division = names[1]
    
    # get id for competitor
    rows = db.execute("SELECT DISTINCT id FROM users WHERE id = ?", session["user_id"])
    competitor_id = rows[0]["id"]
    
    # get division id
    rows = db.execute("SELECT DISTINCT id, comp_id, comp_name FROM divisions WHERE name = ? AND comp_name = ?", division, comp_name)
    id = rows[0]["id"]

    # get comp id 
    comp_id = rows[0]["comp_id"]
    comp_name = rows[0]["comp_name"]

    # insert user into competitor table
    rows = db.execute("INSERT INTO competitors (competitor_id, competition_id, division_id) VALUES (?,?,?)",
                    competitor_id, comp_id, id)
    return redirect("/")

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

# log out
@app.route("/logout")
def logout():

    # forget user_id
    session.clear()

    # redirect to login
    return redirect("/")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    
    # if reached via POST
    if request.method == "POST":

        # check for username creation
        if not request.form.get("username"):
            return apology("username creation required", 400)
        
        # check for duplicate username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            return apology("username already taken", 400)
        
        # check for password creation
        elif not request.form.get("password"):
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
        # add new user to db
        rows = db.execute("INSERT INTO users (username, hash, firstname, lastname) VALUES (?,?,?,?)",
                           username, hash, firstname, lastname)
        
        # redirect to log in
        return redirect("/")

    # if reached by get
    else:
        return render_template("register.html")


