#Book Club 2023
#import relevant functions from packages
from io import BytesIO
from flask import Flask, render_template, request, send_file, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR, Text, update, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database #import to check if database exists
from werkzeug.utils import secure_filename
import os

def connection():
  Session = sessionmaker(bind=engine)
  session = Session()

Base = declarative_base()
############################REVIEW CLASS###################################
#class to store reviews
class Review(Base):
  __tablename__ = "reviews"
  review_id = Column("review_id", Integer, primary_key=True)
  review = Column("review", String)
  #connect to books table
  book = Column(Integer, ForeignKey("books.book_id"))

  def __init__(self, review_id, review, book):
    self.review_id = review_id
    self.review = review
    self.book = book

  #get methods
  def get_review_id(self):
    return self.review_id

  def get_review(self):
    return self.review

  def get_book(self):
    return self.book

  #set methods
  def set_review_id(self, review_id):
    self.review_id = review_id

  def set_review(self, review):
    self.review = review

  def set_book(self, book):
    self.book = book

#######################BOOK CLASS##########################################
#book class to store title, author, genre, summary, and image
class Book(Base):
  __tablename__ = "books"
  book_id = Column("book_id", Integer, primary_key=True)
  title = Column("title", String)
  author = Column("author", String)
  genre = Column("genre", String)
  summary = Column("summary", String)
  #Store image by url
  url = Column("imageURL", String(255))
  #one to many relationship - one book to many reviews
  reviews_written = relationship('Review', foreign_keys=[Review.book], backref='book_of', lazy='dynamic')
  
  def __init__(self, book_id, title, author, genre, summary, url=None):
    self.book_id = book_id
    self.title = title
    self.author = author
    self.genre = genre
    self.summary = summary
    self.url = url
  #get methods  
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
  #set methods
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
    
  #return all book info  
  def __repr__(self):
    return f"{self.book_id}, {self.title}, {self.author}, {self.genre},{self.summary}, {self.url} "
    
######################MEMBERS##############################################
#class for members table used for login
class Members(Base):
  __tablename__ = "members"
  member_id = Column("member_id", Integer, primary_key=True)
  email = Column("email", String)
  password = Column("password", String)

  def __init__(self, email, password):
    self.email = email
    self.password = password

#get and set methods
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
  #add books
  b1 = Book(1, "The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", "Romance", "The Seven Husbands of Evelyn Hugo tells the tale of the 79-year-old main character (Evelyn Hugo) and her life as an actress in the golden age of Hollywood", None)
  session.add(b1)
  session.commit()

app = Flask(__name__)

def string_length(min, max, string):
  if len(string) < min or len(string) > max:
    valid = False
  else:
    valid = True
  return(valid)
    
# basic route
@app.route('/')
def root():
    return render_template("home.html", page_title='HOME')
  
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
  return render_template('signup.html', page_title= 'SIGNUP')

############################ Display books #######################################
#Books displayed with title and image
@app.route('/all_books')
def all_books():
  #Create Session
  Session = sessionmaker(bind=engine)
  session = Session()
  #Query all books
  books = session.query(Book).all()
  return render_template('all_books.html', page_title= 'all_books', query_results = books)

@app.route('/books/<int:book_id>')
def book(book_id):
  #new session
  Session = sessionmaker(bind=engine)
  session =Session()
  #info for specific book
  results = session.query(Book).filter(Book.book_id == book_id).first()
  #reviews for book
  reviews = session.query(Review).filter(Review.book == book_id)
  return render_template('book.html', page_title= 'Book_Details', query_results = results, reviews = reviews)
  
##Route for adding books
@app.route('/add_book',  methods=['POST', 'GET'])
def add_book():
  if request.method == "POST":
    #get info from add book form
    title = request.form.get("title")
    author = request.form.get("author")
    genre = request.form.get("genre")
    summary = request.form.get("summary")
    #get image from files
    image = request.files['image']
    url = secure_filename(image.filename)
    #save image 
    if len(url) == 0:
      print("No image supplied")
    else:
      image.save(os.path.join('static/uploads', url))
    #new connection
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    max_id = session.query(func.max(Book.book_id)).scalar()
    print("highest book id is: ", max_id)
    book_id = 1 + max_id
    #add book to database
    if len(url) == 0:
      b = Book(book_id, title, author, genre, summary, None)
    else:
      b = Book(book_id, title, author, genre, summary, url)
    session.add(b)
    session.commit()
  return render_template('add_book.html', page_title= 'Add_Book')

###########################  add Reviews #######################################
#route to add a review
@app.route('/add_review', methods=['POST', 'GET'])
def add_review():
  #new connection
  Session = sessionmaker(bind=engine)
  session = Session()
  #query all books
  books = session.query(Book).all()
  if request.method == "POST":
    #get info from form
    book = request.form.get("book")
    review = request.form.get("review")
    #new connection
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    b = session.query(Book).filter(Book.book_id == book)
    #add review
    max_id = session.query(func.max(Review.review_id)).scalar()
    print("highest review id is: ", max_id)
    review_id = 1 + max_id
    r = Review(review_id, review, book)
    print(r)
    session.add(r)
    #relationship
    b.reviews_written = r
    session.commit()
    return redirect(url_for('book', book_id=book ))
  return render_template('add_review.html', books=books, page_title='Add Review')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)