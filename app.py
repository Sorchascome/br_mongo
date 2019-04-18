import os, requests
from string import ascii_letters, digits

from flask import Flask, session, g, request, redirect, url_for, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from bson import ObjectId
from pymongo import MongoClient

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app)

# Set up database
client = MongoClient("mongodb+srv://defaultuser:YSstl2ep5qA1471x@brcluster-bzf8f.mongodb.net/test?retryWrites=true")
db = client.brdb
col = db.brcollection
booklist = db.bookcollection
breviews = db.userreviews

# Login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":
        userinput = request.form.get("search")  
        getbooks = booklist.find({})

        foundbooks =[]
        found = False
        noitems = False

        if not userinput:
           noitems = True

        for book in getbooks:
            for attr, value in book.items():
                if attr != '_id':
                    if userinput.lower() in value.lower():
                        found = True
                if found == True:
                    foundbooks.append(book)
                    found = False

        if len(foundbooks) == 0:
            noitems = True

        return render_template("index.html", books=foundbooks, noitems=noitems)

    else:
        return render_template("index.html")

@app.route("/api/<isbn>", methods=["GET", "POST"])
@login_required
def bookinfo(isbn):

    if request.method == "GET": 
        book = booklist.find_one({ "isbn": isbn })
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "7d2VjvXPfeZHdRnLbplw", "isbns": isbn}).json()
        rating = res["books"][0]["average_rating"]
        scorelist = breviews.find_one({ "isbn": isbn })
        if scorelist != None:
            scores = scorelist["rating"].split()
            print(scores)
        else:
            scores = 0
        user_review_list = breviews.find_one( { "isbn": isbn, "id": session["user_id"] })
        if user_review_list != None:
            user_review = user_review_list["rating"]
        else:
            user_review = None
        reviews = breviews.find( { "isbn": isbn })
        check_reviews = True
        reviewed = True
        userscore = 0
        count = 0
        
        if reviews == None:
            check_reviews = False
       
        if not scores:
            userscore = "No score yet."
        else:
            for score in scores:
                userscore += float(score)
                count += 1
            userscore = userscore/count

        if user_review != None:
            reviewed = False

        if book == None:
            return error("No such book.")

        return render_template("book.html", title=book["title"], author=book["author"], isbn=book["isbn"], year=book["year"], rating=rating, userscore=userscore, reviews=reviews, reviewed=reviewed, check_reviews=check_reviews)

    else:
        username = col.find_one({ "_id": ObjectId(session["user_id"]) })["username"]
        posted = breviews.find_one({ "username": username, "isbn": isbn })
        print(posted)
        book = booklist.find_one({ "isbn": isbn })
        review = request.form.get("review")
        rating = request.form.get("rating")
        if posted != None:
            return error("You have already submitted a review for this book.")

        else:
            breviews.insert_one({ "username": username, "isbn": book["isbn"], "rating": rating, "review": review })   
            return success("You have succesfully posted a review.")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        finduser = col.find_one({ "username": username })
        userid = finduser["_id"]
        rows = finduser["username"]
        gethash = finduser["password"]

        # Check if credentials are in db
        if username == rows and check_password_hash(gethash, password):
            session["user_id"] = userid
            return redirect("/")
        
        else:
            return error("Invalid credentials.")

    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        hash = generate_password_hash(password)

        # Invalid register input handler

        if len(username) > 10 or len(username) < 4:
            return error("Invalid username. Length of a username should be between 4 and 10 symbols.") 

        if len(password) > 10 or len(password) < 4:
            return error("Invalid password. Length of a password should be between 4 and 10 symbols.")             

        if password != repassword:
            return error("Passwords do not match.")

        for ch in username:
            if ch not in ascii_letters and ch not in digits:
                return error("Invalid username. Please use only letters and/or digits.")

        # Proceed with registration
        user = {
            "username": username,
            "password": hash
        }
        if col.find_one({ "username": username }) == None:
            col.insert_one(user)
            return success('You were sucessfully registered! You may now login to your account.')
        else:
            return error("Username already exists.")

    else:   
        return render_template("register.html")

# Hangle errors
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

def error(message):
    return render_template("error.html", message=message)

def success(message):
    return render_template("success.html", message=message)

if __name__ == "__main__":
    app.run()  