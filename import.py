
import csv
import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://ptlcnniendmqhv:c723cef7e366be21718bf9d7e85f1180b711f4cb88eda7543a083f065f5efce0@ec2-54-235-92-244.compute-1.amazonaws.com:5432/defjs12d5tolif")
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)

for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn, "title": title, "author": author, "year": year})
    # print(f"Added book {title} by {author} from {year} isbn code {isbn}.")
db.commit()
