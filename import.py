import os
import csv
from pymongo import MongoClient

engine = MongoClient("mongodb+srv://defaultuser:kJZZXlhU41KmBmD6@brcluster-bzf8f.mongodb.net/test?retryWrites=true")  # mongodb host uri
db = engine.brdb
cl = db.brcollection
bookcl = db.bookcollection


def importcsv():
    f = open("books.csv", "r", encoding="utf-8")
    books = csv.DictReader(f)
    header= [ "isbn", "title", "author", "year" ]

    for each in books:
        row = {}
        for field in header:
            row[field] = each[field]

        bookcl.insert_one(row)

    booklist = bookcl.find()
    for book in booklist:
        print(book)

if __name__ == "__main__":
    importcsv()
