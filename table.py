import os, requests

from werkzeug.security import check_password_hash, generate_password_hash
import csv


def table():
#    text = input()
#    rows = db.execute("SELECT * FROM books").fetchall()
#    for book in rows:
#        for element in book:
#            if text in element:
#                print(element)
    isbn = '0061120073'
    book = db.execute("SELECT * FROM users INNER JOIN reviews ON users.id=reviews.userid WHERE isbn=:isbn;", {"isbn": isbn}).fetchall()
    for b in book:
        print(b.username)

if __name__ == "__main__":
    table()

