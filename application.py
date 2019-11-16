import os
import sys

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import hashlib

import requests

def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

user_id = 0
book_isbn = ""

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    global user_id
    user_id = 0
    #users = db.execute("SELECT * FROM users").fetchall()
    #return render_template("users.html", users = users)
    message = ""
    return render_template("index.html", message = message)

@app.route("/1")
def switch_form():
    #users = db.execute("SELECT * FROM users").fetchall()
    #return render_template("users.html", users = users)
    sign_up = True
    return render_template("index.html", sign_up = sign_up, message = "")

@app.route("/mainPage", methods=["POST"])
def sign_in():
    """ sign_in """
    global user_id

    users = db.execute("SELECT * FROM users").fetchall()

    #Make sure user exists
    for user in users:
        if user_id == user.id:
            books = db.execute("SELECT * FROM books").fetchall()
            print(user_id)
            return render_template("mainPage.html", books=books)

    # Get form information
    pre_password = request.form.get("psw")
    password = encrypt_string(pre_password)
    username = request.form.get("username")

    users = db.execute("SELECT * FROM users").fetchall()

    #Make sure user exists
    for user in users:
        if username == user.username:
            if password == user.password:
                user_id = user.id
                books = db.execute("SELECT * FROM books").fetchall()
                return render_template("mainPage.html", books=books)
                #return render_template("mainPage.html")
            else:
                return render_template("index.html", message = "rInvalid username or password")
    return render_template("index.html", message = "rInvalid username or password")
    #if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
    #    return()
    #return render_template("index.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    """ sign_un """

    # Get form information
    pre_password = request.form.get("psw")
    password = encrypt_string(pre_password)
    username = request.form.get("username")

    users = db.execute("SELECT * FROM users").fetchall()

    #Make sure user exists
    for user in users:
        if username == user.username:
            return render_template("index.html", sign_up = sign_up, message = "rUsername already taken, please use another username")
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
    db.commit()
    return render_template("index.html", message = "gAccount successfully created")
    #if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
    #    return()
    #return render_template("index.html")

@app.route("/books/<string:book_id>")
def show_book(book_id):
    goodreads_average = 0
    goodreads_number = 0
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "RGLfDq6J2IPGVM9nxw9uiQ", "isbns": book_id})
    if(res is not None):
        json_parsed = res.json().get("books")
        work_ratings_count = json_parsed[0].get("work_ratings_count")
        average_rating = json_parsed[0].get("average_rating")
    else:
        work_ratings_count = 0
        work_ratings_count = 0
    # book = db.execute("SELECT * FROM books").fetchall()
    # return render_template("mainPage.html", books=books)

    mrating = ""
    mreview = ""
    book = db.execute("SELECT * FROM books WHERE isbn = :book_id",
                            {"book_id": book_id}).fetchone()

    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :book_id",
                            {"book_id": book_id}).fetchall()
    # book = db.execute("SELECT * FROM books WHERE isbn = '1416949658'").fetchall()

    rating = db.execute("SELECT * FROM rankings WHERE isbn = :book_id",
                            {"book_id": book_id}).fetchone()

    global book_isbn
    book_isbn = book.isbn

    if rating is None:
        mrating = "Not yet rated"
    return render_template("book.html", book=book, reviews = reviews, rating = rating, mrating = mrating, mreview = mreview , message ="", work_ratings_count = work_ratings_count, average_rating = average_rating)

@app.route("/books/posted", methods=["POST"])
def post_review():
    """ post review """
    lusers = []
    users = db.execute("SELECT * FROM users").fetchall()

    # Get form information
    freview = request.form.get("review")
    frating = request.form.get("rate")

    mrating = ""
    mreview = ""

    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchall()

    reviews_user_id = db.execute("SELECT * FROM reviews WHERE user_id = :user_id",
                            {"user_id": user_id}).fetchone()

    book = db.execute("SELECT * FROM books WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()

    rating = db.execute("SELECT * FROM rankings WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()

    goodreads_average = 0
    goodreads_number = 0
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "RGLfDq6J2IPGVM9nxw9uiQ", "isbns": book_isbn})
    if(res is not None):
        json_parsed = res.json().get("books")
        work_ratings_count = json_parsed[0].get("work_ratings_count")
        average_rating = json_parsed[0].get("average_rating")
    else:
        work_ratings_count = 0
        work_ratings_count = 0

    #Make sure user exists
    for user in users:
        lusers.append(user.id)

    if(user_id not in lusers):
        return render_template("book.html", book=book, reviews = reviews, rating = rating, mrating = mrating, mreview = mreview, message = "rYou are not sign in. You cannot make books reviews", work_ratings_count = work_ratings_count, average_rating = average_rating)
    if reviews_user_id is not None:
        if(user_id == reviews_user_id.user_id):
            return render_template("book.html", book=book, reviews = reviews, rating = rating, mrating = mrating, mreview = mreview, message = "rYou have already reviewed this book", work_ratings_count = work_ratings_count, average_rating = average_rating)

    db.execute("INSERT INTO reviews (isbn,review,user_id) VALUES (:isbn,:review,:user_id)", {"isbn": book_isbn,"review": freview, "user_id": user_id})
    db.commit()

    book = db.execute("SELECT * FROM books WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()

    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchall()

    rating = db.execute("SELECT * FROM rankings WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()

    if rating is None:
        db.execute("INSERT INTO rankings (isbn, ranking) VALUES (:isbn,:rating)", {"isbn": book_isbn,"rating": frating})
        db.commit()
    else:
        new_rating = (float(rating.ranking) + float(frating))/2
        db.execute("UPDATE rankings SET ranking= :rating WHERE isbn=:isbn", {"isbn": book_isbn,"rating": new_rating})
        db.commit()

    rating = db.execute("SELECT * FROM rankings WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()

    return render_template("book.html", book=book, reviews = reviews, rating = rating, mrating = mrating, mreview = mreview, message="", work_ratings_count = work_ratings_count, average_rating = average_rating)

@app.route("/api/books/<string:book_id>")
def flight_api(book_id):
    """Return details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid book_isbn"}), 404

    rating = db.execute("SELECT * FROM rankings WHERE isbn = :book_id",
                            {"book_id": book_isbn}).fetchone()
    if rating is None:
        rating_num = "Not yet rated"
        review_count = "Not yet rated"
    else:
        rating_num = rating.ranking
        reviews = db.execute("SELECT * FROM reviews WHERE isbn = :book_id",
                                {"book_id": book_id}).fetchall()
        review_count = len(reviews)
    # Get book information.
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": review_count,
            "average_score": rating_num
        })
