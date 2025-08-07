#Book Club 2023
#import relevant functions from packages
from io import BytesIO
from flask import Flask, render_template, request, send_file, Response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer,CHAR, Text, update, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database #import to check if database exists
from werkzeug.utils import secure_filename
import os

Base = declarative_base()
############################REVIEW CLASS###################################
#class to store reviews with review id, review and book with a foriegn key connecting to the book id
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

#######################BOOK CLASS##########################################
#book class to store title, author, genre, summary, and image and functions to set variable or get variable and a relationship to the reviews table
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

#This is a function to check the length of the string to ensure it is a valid input into a form
def string_length(min, max, string):
  if len(string) < min or len(string) > max:
    valid = False
  else:
    valid = True
  return(valid)
    
# basic route for home page
@app.route('/')
def root():
  return render_template("home.html", page_title='HOME')

############################ Display books #######################################

#Route to display all books in a list with title and image
@app.route('/all_books')
def all_books():
  #Create Session
  Session = sessionmaker(bind=engine)
  session = Session()
  #Query all books
  books = session.query(Book).order_by(Book.title).all()
  return render_template('all_books.html', page_title= 'all_books', query_books = books)

#Route creates a page for each individual book with its details and reviews for that book
@app.route('/books/<int:book_id>')
def book(book_id):
  #new session
  Session = sessionmaker(bind=engine)
  session =Session()
  #info for specific book
  book = session.query(Book).filter(Book.book_id == book_id).first()
  #reviews for book
  reviews = session.query(Review).filter(Review.book == book_id)
  return render_template('book.html', page_title= 'Book_Details', query_book = book, query_review = reviews)
  
#Route to add a book to database, validates input and redirects to an error page if it is invalid, finds the highest id number and adds one to assign to the new book
@app.route('/add_book',  methods=['POST', 'GET'])
def add_book():
  if request.method == "POST":
    #get info from add book form
    title = request.form.get("title")
    if string_length(1, 50, title) == False:
      message = "Invalid Title - title must be between 1 and 50 characters"
      return redirect(url_for('error_406', message = message))
    author = request.form.get("author")
    if string_length(3, 50, author) == False:
      message = "Invalid Author - author must be between 3 and 50 characters"
      return redirect(url_for('error_406', message = message))
    genre = request.form.get("genre")
    if string_length(2, 25, genre) == False:
      message = "Invalid Genre - genre must be between 2 and 25 characters"
      return redirect(url_for('error_406', message = message))
    summary = request.form.get("summary")
    if string_length(5, 500, summary) == False:
      message = "Invalid Summary - summary must be between 10 and 500 characters"
      return redirect(url_for('error_406', message = message))
    #get image from files
    image = request.files['image']
    url = secure_filename(image.filename)
    #save image 
    if len(url) == 0:
      print("No image supplied")
      url = None
    else:
      image.save(os.path.join('static/uploads', url))
    #new connection
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    max_id = session.query(func.max(Book.book_id)).scalar()
    if max_id == None:
      max_id = 0
    print("highest book id is: ", max_id)
    book_id = 1 + max_id
    #add book to database
    new_book = Book(book_id, title, author, genre, summary, url)
    session.add(new_book)
    session.commit()
    return redirect(url_for('book', book_id = book_id))
  message = None
  return render_template('add_book.html', page_title= 'Add_Book', message = message)

#Route to select a book to edit through combo box
@app.route('/edit_book', methods=['POST','GET'])
def edit_book():
  Session = sessionmaker(bind=engine)
  session = Session()
  books = session.query(Book).order_by(Book.title).all()
  if request.method == "POST":
    book_chosen = request.form.get("book")
    return redirect(url_for('update', ids = book_chosen))
  return render_template('edit_book.html', query_books = books, page_title='Edit a Book')

#route to individual edit form for each book
@app.route('/update/<ids>', methods=['POST', 'GET'])
def update(ids):
  print(ids)
  Base.metadata.create_all(bind=engine)
  Session = sessionmaker(bind=engine)
  session = Session()
  book_id = int(ids)
  book = session.query(Book).filter(Book.book_id == book_id).first()
  print(book.title)
  if request.method == 'POST':
    if request.form['edit_button'] =="Save":
      print("save button clicked")
      image = request.files['image']
      url = secure_filename(image.filename)
      #save image 
      if len(url) == 0:
        print("No image supplied")
        
      else:
        image.save(os.path.join('static/uploads', url))
        book.url = url
      book.title = request.form['title']
      if string_length(1, 50, book.title) == False:
        message = "Invalid Title - title must be between 1 and 50 characters"
        return redirect(url_for('error_406', message = message))
      book.author = request.form['author']
      if string_length(3, 50, book.author) == False:
        message = "Invalid Author - author must be between 3 and 50 characters"
        return redirect(url_for('error_406', message = message))
      book.genre = request.form['genre']
      if string_length(2, 25, book.genre) == False:
        message = "Invalid Genre - genre must be between 2 and 25 characters"
        return redirect(url_for('error_406', message = message))
      book.summary = request.form['summary']
      if string_length(10, 500, book.summary) == False:
        message = "Invalid Summary - summary must be between 10 and 500 characters"
        return redirect(url_for('error_406', message = message))
      session.commit()
      return redirect(url_for('book', book_id=book_id))
      
    elif request.form['edit_button'] =="Delete":
      print("book delete button has been pressed")
      session.delete(book)
      session.commit()
      print("book has been deleted")
      return redirect(url_for('all_books'))
      
    print("getting from update")
  return render_template('update.html', query_book = book, ids=book_id, page_title='UPDATE')
      
###########################  add Reviews #######################################
#route to add a review, book is selected from a combo box and relationship is created
@app.route('/add_review', methods=['POST', 'GET'])
def add_review():
  #new connection
  Session = sessionmaker(bind=engine)
  session = Session()
  #query all books
  books = session.query(Book).order_by(Book.title).all()
  if request.method == "POST":
    #get info from form
    book = request.form.get("book")
    review = request.form.get("review")
    if string_length(1, 100, review) == False:
      message = "Invalid Review - review must be between 1 and 100 characters"
      return redirect(url_for('error_406', message = message))
    #new connection
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    review_book = session.query(Book).filter(Book.book_id == book)
    #add review
    max_id = session.query(func.max(Review.review_id)).scalar()
    if max_id == None:
      max_id = 0
    print("highest review id is: ", max_id)
    review_id = 1 + max_id
    relationship = Review(review_id, review, book)
    print(relationship)
    session.add(relationship)
    #relationship
    review_book.reviews_written = relationship
    session.commit()
    return redirect(url_for('book', book_id=book ))
  return render_template('add_review.html', query_books=books, page_title='Add Review')

#Route for error page takes the message from the check_stringlength function
@app.route('/406/<message>')
def error_406(message):
  print(message)
  return render_template('406.html', message=message, page_title='Error 406')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)