#Book Club 2023

from io import BytesIO
from flask import Flask, render_template, request, send_file, Response
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR, Text, LargeBinary, update
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database #import to check if database exists
from werkzeug.utils import secure_filename
import os

Base = declarative_base()


############################REVIEW CLASS###################################
class Review(Base):
  __tablename__ = "reviews"
  review_id = Column("review_id", Integer, primary_key=True)
  review = Column("review", String)
  book = Column(Integer, ForeignKey("books.book_id"))

  def __init__(self, review_id, review, book):
    self.review_id = review_id
    self.review = review
    self.book = book

  def get_review_id(self):
    return self.review_id

  def get_review(self):
    return self.review

  def get_book(self):
    return self.book

  def set_review_id(self, review_id):
    self.review_id = review_id

  def set_review(self, review):
    self.review = review

  def set_book(self, book):
    self.book = book

#######################BOOK CLASS##########################################
class Book(Base):
  __tablename__ = "books"
  book_id = Column("book_id", Integer, primary_key=True)
  title = Column("title", String)
  author = Column("author", String)
  genre = Column("genre", String)
  summary = Column("summary", String)
  url = Column("imageURL", String(255))#images
  #one to many
  reviews_written = relationship('Review', foreign_keys=[Review.book], backref='book_of', lazy='dynamic')
  
  def __init__(self, book_id, title, author, genre, summary, url=None):
    self.book_id = book_id
    self.title = title
    self.author = author
    self.genre = genre
    self.summary = summary
    self.url = url
    
  def get_book_id(self):
    return self.book_id

  def get_title(self):
    return self.title

  def get_author(self):
    return self.author

  def get_genre(self):
    return self.genre

  def get_summary(self):
    return self.summary

  def get_url(self):
    return self.url

  def set_book_id(self, book_id):
    self.book_id = book_id

  def set_title(self, title):
    self.title = title

  def set_author(self, author):
    self.author = author

  def set_genre(self, genre):
    self.genre = genre

  def set_summary(self, summary):
    self.summary = summary

  def set_url(self, url):
    self.url = url
    
  def __repr__(self):
    return f"{self.book_id}, {self.title}, {self.author}, {self.genre},{self.summary}, {self.url} "
    
######################MEMBERS##############################################
class Members(Base):
  __tablename__ = "members"
  member_id = Column("member_id", Integer, primary_key=True)
  email = Column("email", String)
  password = Column("password", String)

  def __init__(self, email, password):
    self.email = email
    self.password = password

  def get_email(self):
    return self.email

  def set_email(self, email):
    self.email = email

  def set_password(self, password):
    self.password = password

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
  b1 = Book(1, "The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", "Romance", "The Seven Husbands of Evelyn Hugo tells the tale of the 79-year-old main character (Evelyn Hugo) and her life as an actress in the golden age of Hollywood", None)
  b2 = Book(2, "Fourth Wing", "Rebbeca Yarros", "Fantasy", "Fourth Wing is about a war college where some students become dragon riders and obtain magical powers.", None)

  session.add(b1)
  session.add(b2)
  session.commit()

app = Flask(__name__)
# basic route
@app.route('/')
def root():
    return render_template("home.html", page_title='HOME')
  
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
  return render_template('signup.html', page_title= 'SIGNUP')

##Display list of books
@app.route('/all_books')
def all_books():
  Session = sessionmaker(bind=engine)
  session = Session()
  books = session.query(Book).all()
  return render_template('all_books.html', page_title= 'all_books', query_results = books)

@app.route('/books/<int:book_id>')
def book(book_id):
  print(book_id)
  Session = sessionmaker(bind=engine)
  session =Session()
  results = session.query(Book).filter(Book.book_id == book_id).first()
  print(results)
  print(book)
  return render_template('book.html', page_title= 'Book_Details', query_results = results)
  
##Route for adding books
@app.route('/add_book',  methods=['POST', 'GET'])
def add_book():
  if request.method == "POST":
    book_id = request.form.get("book_id")
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    summary = request.form.get("summary")
    
    #for image
    image = request.files['image']
    url = secure_filename(image.filename)
    image.save(os.path.join('static/uploads', url))
    
    #connection
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    book_id = int(book_id)
    b = Book(book_id, title, author, genre, summary, url)
    session.add(b)
    session.commit()
  return render_template('add_book.html', page_title= 'Add_Book')

@app.route('/add_review', methods=['POST', 'GET'])
def add_review():
  Session = sessionmaker(bind=engine)
  session =Session()
  books = session.query(Book).all()
  if request.method == "POST":
    review_id = request.form.get("review_id")
    book = request.form.get("book")
    review = request.form.get("review")
    if book == None:
      print("error book not working")
    else:
      print(book)
    #connection
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    b = session.query(Book).filter(Book.book_id == book)
    print(b)
    review_id = int(review_id)
    r = Review(review_id, review, book)
    print(r)
    session.add(r)
    b.reviews_written = r
    session.commit()
  return render_template('add_review.html', books=books, page_title='Add Review')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)