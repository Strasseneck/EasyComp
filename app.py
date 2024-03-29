
# import libraries etc
import os

from cs50 import SQL
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import math
import random
from tempfile import mkdtemp
from uuid import uuid4
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


## ROUTE FOR ALL USERS ##

# Index
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# Login
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

# Log out
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

        rows = db.execute("INSERT INTO users (username, hash, firstname, lastname) VALUES (?,?,?,?)",
                           username, hash, firstname, lastname)
        
        # redirect to log in
        return redirect("/")

    # if reached by get
    else:
        return render_template("register.html")

# Profile page
@app.route("/profile")
@login_required
def profile():

    # select user data
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    
    # get user data to display
    firstname = rows[0]["firstname"]
    lastname = rows[0]["lastname"]
    name = firstname + " " + lastname
    
    # select user's entered comps and divisions
    rows = db.execute("SELECT DISTINCT comp_name, name FROM divisions INNER JOIN competitors on competitors.division_id = divisions.id WHERE competitor_id = ?", session["user_id"])
    entered = rows

    # select users victories
    rows = db.execute("SELECT COUNT (*) FROM matchresults WHERE winner = ?", name)
    wins = rows[0]["COUNT (*)"]

    if wins == 0:
        submissionrate = 0
    
    else:
        # get submission victories
        submission = "submission"
        rows = db.execute("SELECT COUNT (*) FROM matchresults WHERE winner = ? AND method = ? ", name, submission)
        submissions = rows[0]["COUNT (*)"]
        # calculate submission rate
        submissionrate = (submissions / wins) * 100

    # select users medals
    rows = db.execute("SELECT COUNT (*) FROM competitionresults WHERE gold = ?", name)
    gold = rows[0]["COUNT (*)"]
    rows = db.execute("SELECT COUNT (*) FROM competitionresults WHERE silver = ?", name)
    silver = rows[0]["COUNT (*)"]

    # select users match results
    results = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name, winner, method FROM matchresults WHERE competitor1_name = ? OR competitor2_name = ?", name, name)

    # render template
    return render_template("profile.html", name=name, wins=wins, submissionrate=submissionrate, gold=gold, silver=silver, results=results, entered=entered)

# View Competitions
@app.route("/competitions", methods=["GET"]) 
@login_required
def competitions():
    
    # get all competitions
    competitions = db.execute("SELECT DISTINCT name, info, format FROM competitions")

    # render template
    return render_template("competitions.html", competitions=competitions)

# Competition page
@app.route("/competition/<name>", methods=["GET"])
@login_required
def competition(name):

    # get comp_id
    rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name = ?", name)
    comp_id = rows[0]["id"]

    # get comp info
    rows = db.execute("SELECT DISTINCT info FROM competitions WHERE id = ?", comp_id)
    info = rows[0]["info"]

    # get registrations count

    # division objects
    registrations = 0 
    divisions = {}
    divnames = []
    divids = []

    # get division names and ids
    rows = db.execute("SELECT DISTINCT id, name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)
        divisions[divname] = []

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        if len(rows) != 0:
            for j in range(len(rows)):
                competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
                registrations += 1
             

    # render template
    return render_template("competition.html", info=info, name=name, registrations=registrations)

## ROUTES FOR ORGANIZERS ##

# Create competition as organizer
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

        # getinfo
        info = request.form.get("compinfo")
        
        # get format 
        format = request.form["format-select"]
        if format == 'singleroundko':
            format = 'Single Round Elimination'
        elif format == 'roundrobin':
            format = 'Round Robin'

        # add new competition to competitions db
        rows = db.execute("INSERT INTO competitions (name, info, format, organizer_id) VALUES (?,?,?,?)", compname, info, format, session["user_id"] )

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

# Organizer panel 
@app.route("/organizerpanel", methods = ["GET"])
@login_required
def organizerpanel():
    # get user's competitions
    competitions = db.execute("SELECT DISTINCT name, info, format FROM competitions WHERE organizer_id = ?", session["user_id"])
    
    return render_template("organizerpanel.html", competitions=competitions)

# Your competition page
@app.route("/yourcompetition/<name>", methods=["GET"])
@login_required
def yourcompetition(name):

    # get comp_id
    rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name = ?", name)
    comp_id = rows[0]["id"]

    # get comp info
    rows = db.execute("SELECT DISTINCT info FROM competitions WHERE id = ?", comp_id)
    info = rows[0]["info"]

    # get registrations count

    # division objects
    registrations = 0 
    divisions = {}
    divnames = []
    divids = []

    # get division names and ids
    rows = db.execute("SELECT DISTINCT id, name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)
        divisions[divname] = []

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        if len(rows) != 0:
            for j in range(len(rows)):
                competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
                registrations += 1

    # render template
    return render_template("yourcompetition.html", info=info, name=name, registrations=registrations)

# Your competition registrations
@app.route("/yourcompregistrations/<name>")
@login_required
def yourcompregistrations(name):

    # get comp_id
    rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name = ?", name)
    comp_id = rows[0]["id"]

    # division objects 
    divisions = {}
    divnames = []
    divids = []
    registrations = 0

    # get division names and ids
    rows = db.execute("SELECT DISTINCT id, name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)
        divisions[divname] = []

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        if len(rows) != 0:
            for j in range(len(rows)):
                competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
                registrations += 1
                competitors.append(competitor)
            # add values to divisions dict        
            divisions[divname] = competitors
        
    # render template
    return render_template("yourcompregistrations.html", divisions=divisions, name=name, registrations=registrations)

# Your competition brackets / results
@app.route("/yourcompbrackets/<name>", methods=["GET"])
@login_required
def yourcompbrackets(name):

    # get id and name of competition
    rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name LIKE ?", name)
    comp_id = rows[0]["id"]

    # get registrations count

    # division objects
    registrations = 0 
    divisions = {}
    divnames = []
    divids = []

    # get division names and ids
    rows = db.execute("SELECT DISTINCT id, name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)
        divisions[divname] = []

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        if len(rows) != 0:
            for j in range(len(rows)):
                competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
                registrations += 1
    
    # get brackets
    matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
    
    # get results
    results = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name, winner, method FROM matchresults WHERE comp_id = ?", comp_id)
    medallists = db.execute("SELECT DISTINCT div_name, gold, silver FROM competitionresults WHERE comp_id = ?", comp_id)

    return render_template("yourcompbrackets.html", matches=matches, name=name, results=results, medallists=medallists, registrations=registrations)


# Generate brackets if not already generated
@app.route("/generatebrackets/<name>", methods=["GET", "POST"])
@login_required
def generatebrackets(name):
    
    #get id and name of competition
    rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name = ?", name)
    comp_id = rows[0]["id"]
    divisions = {}
    divnames = []
    divids = []

    # check if brackets have already been generated
    count = db.execute("SELECT COUNT(*) FROM matches WHERE comp_id = ?", comp_id)
    count = count[0]["COUNT(*)"]
    count = int(count)

    if count != 0:
        # get brackets
        matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
        return render_template("yourcompbrackets.html", matches=matches, name=name)


    else:
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
               
                # get div_id
                rows = db.execute("SELECT DISTINCT id FROM divisions WHERE name = ? AND comp_id = ?", divname, comp_id)
                div_id = rows[0]["id"]

                # generate unique match id 
                match_id = str(uuid4())
                

                # insert match into matches table
                db.execute("INSERT INTO matches (id, comp_id, div_id, div_name, competitor1_name, competitor2_name) VALUES (?,?,?,?,?,?)",
                            match_id, comp_id, div_id, divname, competitor1, competitor2) 
                       
        # get brackets
        matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
        return render_template("yourcompbrackets.html", matches=matches, name=name)
       
    
# Start match as organizer
@app.route("/match/<id>", methods=["POST"])
@login_required
def match(id):

    # get match info
    rows = db.execute("SELECT DISTINCT div_name, competitor1_name, competitor2_name FROM matches WHERE id = ?", id)
    match = rows[0]

    # determine match length based on division
    division = rows[0]['div_name']
    division = division.split()
    division = division[0]
    if division == "White":
        displaymins = "05:00"
        realmins = 4
    elif division == "Blue":
        displaymins = "06:00"
        realmins = 5
    elif division == "Purple":
        displaymins = "07:00"
        realmins = 6
    elif division == "Brown":
        displaymins = "08:00"
        realmins = 7
    elif division == "Black":
        displaymins = "10:00"
        realmins = 9

    return render_template("match.html", match=match, id=id, realmins=realmins, displaymins=displaymins)

# End match as organizer
@app.route("/endmatch/<id>", methods=["POST"])   
@login_required
def endmatch(id):

    # get match info
    info = db.execute("SELECT * FROM matches WHERE id = ?", id)
    div_id = info[0]["div_id"]
    divname = info[0]["div_name"]
    competitor1 = info[0]["competitor1_name"]
    competitor2 = info[0]["competitor2_name"]
    comp_id = info[0]["comp_id"]

    # get compname
    rows = db.execute("SELECT DISTINCT name FROM competitions WHERE id = ?", comp_id)
    compname = rows[0]["name"]

    # get winner
    winner = request.form.get("winner-select")

   # update table
    if winner == "1":
        winner = competitor1 
        loser = competitor2

    elif winner == "2":
        winner = competitor2
        loser = competitor1

    method = request.form.get("victory-method")

    # add match to matchresults table
    db.execute("INSERT INTO matchresults (id, comp_id, div_name, competitor1_name, competitor2_name, winner, method) VALUES (?,?,?,?,?,?,?)",
                            id, comp_id, divname, competitor1, competitor2 , winner, method) 
    
    # remove match from matches
    db.execute("DELETE FROM matches WHERE id = ?", id)
    
    # get winner and loser id by splitting name
    winnername = winner.split()
    winnerfirstname = winnername[0]
    winnerlastname = winnername[1]
    rows = db.execute("SELECT DISTINCT id FROM users WHERE firstname = ? AND lastname = ?", winnerfirstname, winnerlastname)
    winnerid = rows[0]["id"]

    losername = loser.split()
    loserfirstname = losername[0]
    loserlastname = losername[1]
    rows = db.execute("SELECT DISTINCT id FROM users WHERE firstname = ? AND lastname = ?", loserfirstname, loserlastname)
    loserid = rows[0]["id"]

    # remove losers from competitors
    db.execute("DELETE FROM competitors WHERE competitor_id = ? AND division_id = ?", loserid, div_id)

    # check for gold medallist aka end of division
    count = db.execute("SELECT COUNT (*) FROM competitors WHERE division_id = ?", div_id)
    count = count[0]["COUNT (*)"]
    count = int(count)
    
    if count == 1:
        gold = winner
        goldid = winnerid
        silver = loser
        silverid = loserid
        
        # add results to final results table
        db.execute("INSERT INTO competitionresults (comp_id, comp_name, div_name, gold, gold_id, silver, silver_id) VALUES (?,?,?,?,?,?,?)", comp_id, compname, divname, gold, goldid, silver, silverid)
        
        # get results
        results = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name, winner, method FROM matchresults WHERE comp_id = ?", comp_id)
        medallists = db.execute("SELECT DISTINCT div_name, gold, silver FROM competitionresults WHERE comp_id = ?", comp_id)

        # delete winner from competitors
        db.execute("DELETE FROM competitors WHERE competitor_id = ? AND division_id = ?", winnerid, div_id)

        # delete division from divisions
        db.execute("DELETE FROM divisions WHERE id = ?", div_id)

        # get matches
        matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
        name = compname 

        # render template
        return render_template("yourcompbrackets.html", matches=matches, medallists=medallists, results=results, name=name) 
    
    else:
    
        # get compname
        rows = db.execute("SELECT DISTINCT name FROM competitions WHERE id = ?", comp_id)
        compname = rows[0]["name"]
    
        # get matches
        matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)

        name = compname 
        # get results
        results = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name, winner, method FROM matchresults WHERE comp_id = ?", comp_id)
        return render_template("yourcompbrackets.html", matches=matches, results=results, name=name)


# End competition as organizer
@app.route("/end/<name>", methods=["GET", "POST"])
@login_required
def end(name):

    # define the info
    info = "This competition has already taken place."

    # update info in competitons
    db.execute("UPDATE competitions SET info = ? WHERE name = ?", info, name)

    # render template
    return redirect("/organizerpanel")


## ROUTES FOR COMPETITORS ##

# view divisions and registrations as competitor
@app.route("/registrations/<name>")
@login_required
def registrations(name):

    # get comp_id and info
    rows = db.execute("SELECT DISTINCT id, info FROM competitions WHERE name = ?", name)
    comp_id = rows[0]["id"]
    
    # check if competitition is finished
    info = rows[0]["info"]
    if info == "This competition has already taken place":
        return render_template("registrationsfinished.html", name=name)

    # division objects 
    divisions = {}
    divnames = []
    divids = []
    registrations = 0

    # get division names and ids
    rows = db.execute("SELECT DISTINCT id, name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)
        divisions[divname] = []

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        if len(rows) != 0:
            for j in range(len(rows)):
                competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
                registrations += 1
                competitors.append(competitor)
            # add values to divisions dict        
            divisions[divname] = competitors
        
    # render template
    return render_template("registrations.html", divisions=divisions, name=name, registrations=registrations)

# view brackets / results  as competitor
@app.route("/brackets/<name>", methods=["GET"])
@login_required
def brackets(name):

    #get id and name of competition
    rows = db.execute("SELECT DISTINCT id FROM competitions WHERE name LIKE ?", name)
    comp_id = rows[0]["id"]

    # get registrations count

    # division objects
    registrations = 0 
    divisions = {}
    divnames = []
    divids = []

    # get division names and ids
    rows = db.execute("SELECT DISTINCT id, name FROM divisions WHERE comp_id = ?", comp_id)
    for i in range(len(rows)):
        divname = rows[i]["name"]
        divnames.append(divname)
        divid = rows[i]["id"] 
        divids.append(divid)
        divisions[divname] = []

    # get competitors names for each division
    for i in range(len(divids)):
        competitors = []
        divid = divids[i] 
        divname = divnames[i]
        rows = db.execute("SELECT DISTINCT firstname, lastname FROM users INNER JOIN competitors on competitors.competitor_id = users.id WHERE division_id = ?", divid)
        if len(rows) != 0:
            for j in range(len(rows)):
                competitor = (rows[j]["firstname"] + " " + rows[j]["lastname"])
                registrations += 1
    
    # get results
    results = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name, winner, method FROM matchresults WHERE comp_id = ?", comp_id)
    medallists = db.execute("SELECT DISTINCT div_name, gold, silver FROM competitionresults WHERE comp_id = ?", comp_id)

    # get brackets
    matches = db.execute("SELECT DISTINCT id, div_name, competitor1_name, competitor2_name FROM matches WHERE comp_id = ?", comp_id)
    return render_template("brackets.html", matches=matches, name=name, registrations=registrations, results=results, medallists=medallists)

# enter division as competitor
@app.route("/enterdivision/<name>", methods=["GET"])
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



