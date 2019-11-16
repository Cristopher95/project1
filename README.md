# Project 1

Web Programming with Python and JavaScript

The web application starts with the log-in form. If you do not have an account you can go to the link at the end of the form to create an account with a username and a password. The password is not saved in the database directly, its Sha256 is saved instead. While you are not logged you can still request a book information but you cannot make books reviews. Once you Login you can see a table with all the books stored in the database table books which were imported by the import.py application. You can search a book within this table by its isbn, title, author or year. You can click a book row to show a page with more information of that book like information gathered from Goodreads. At the end of this page you can find a form where you can write a comment and rate this book. Only one review and rating is allowed per user. You can also request information of a book to the application api which comes as a JSON object by get request with the isbn number as a parameter. ex. /api/books/0380795272 where 0380795272 is the book's isbn.

NOTE: In the import.py you should specify the Database url in the line 22
