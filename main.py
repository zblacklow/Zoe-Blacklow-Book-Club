#Book Club 2023

from flask import Flask, render_template, abort
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists

Base = declarative_base()

##BOOK CLASS
class Book(Base):
  __tablename__ = "books"
  book_id = Column("book_id", Integer, primary_key=True)
  title = Column("title", String)
  author = Column("author", String)
  genre = Column("genre", String)
  summary = Column("summary", String)


  def __init__(self, book_id, title, author, genre, summary):
    self.book_id = book_id
    self.title = title
    self.author = author
    self.genre = genre
    self.summary = summary

  def get_book_id():
    return self.book_id

  def get_title():
    return self.title

  def get_author():
    return self.author

  def get_genre():
    return self.genre

  def get_summary():
    return self.summary

  def set_book_id():
    self.book_id = book_id

  def set_title():
    self.title = title

  def set_author():
    self.author = author

  def set_genre():
    self.genre = genre

  def set_summary():
    self.summary = summary


##REVIEW CLASS
class Review(Base):
  __tablename__ = "reviews"
  review_id = Column("review_id", Integer, primary_key=True)
  review = Column("review", String)
  book = Column(Integer, ForeignKey("books.book_id"))

  def __init__(self, review_id, review, book):
    self.review_id = review_id
    self.review = review
    self.book = book

  def get_review_id():
    return self.review_id

  def get_review():
    return self.review

  def get_book():
    return self.book

  def set_review_id():
    self.review_id = review_id

  def set_review():
    self.review = review

  def set_book():
    self.book = book

#DataBase
db_url = "sqlite:///mydb.db" 
engine = create_engine(db_url, echo=True)
#Check if database already exists
if database_exists(db_url):
  print("data base exists - carry on and do stuff")
#if not create it
else:
  Base.metadata.create_all(bind=engine)
  Session = sessionmaker(bind=engine)
  session = Session()


app = Flask(__name__)
# basic route
@app.route('/')
def root():
    return render_template("home.html", page_title='HOME')
  
@app.route('/members')
def members():
  return render_template('members.html', page_title= 'MEMBERs')

@app.route('/all_books')
def all_books():
  return render_template('all_books.html', page_title= 'all_books')
  
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)