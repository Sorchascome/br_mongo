import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

engine = create_engine(os.getenv("DATABASE"))
db = scoped_session(sessionmaker(bind=engine))


def create():
    #db.execute("DROP TABLE books;")
    #db.execute("CREATE TABLE books (isbn text, title text, author text, year text);")
    db.execute("CREATE TABLE reviews (userid int, isbn text, rating numeric, review text);")

    db.commit()

if __name__ == "__main__":
    create()



