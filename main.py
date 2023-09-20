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
  print(results.url)
  #reviews for book
  reviews = session.query(Review).filter(Review.book == book_id)
  return render_template('book.html', page_title= 'Book_Details', query_results = results, reviews = reviews)
  
##Route for adding books
@app.route('/add_book',  methods=['POST', 'GET'])
def add_book():
  if request.method == "POST":
    #get info from add book form
    title = request.form.get("title")
    if string_length(1, 50, title) == False:
      message = "Invalid Title"
      return redirect(url_for('error_406', message = message))
    author = request.form.get("author")
    if string_length(3, 25, author) == False:
      message = "Invalid Author"
      return redirect(url_for('error_406', message = message))
    genre = request.form.get("genre")
    if string_length(2, 15, genre) == False:
      message = "Invalid Genre"
      return redirect(url_for('error_406', message = message))
    summary = request.form.get("summary")
    if string_length(5, 100, summary) == False:
      message = "Invalid Summary"
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
    print("highest book id is: ", max_id)
    book_id = 1 + max_id
    #add book to database
    b = Book(book_id, title, author, genre, summary, url)
    session.add(b)
    session.commit()
    return redirect(url_for('all_books'))
  return render_template('add_book.html', page_title= 'Add_Book')

#edit book page
@app.route('/edit_book', methods=['POST','GET'])
def edit_book():
  Session = sessionmaker(bind=engine)
  session = Session()
  books = session.query(Book).all()
  if request.method == "POST":
    book_chosen = request.form.get("book")
    return redirect(url_for('update', ids = book_chosen))
  return render_template('edit_book.html', books=books, page_title='Edit a Book')

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
        url = None
      else:
        image.save(os.path.join('static/uploads', url))
      book.url = url
      book.title = request.form['title']
      book.author = request.form['author']
      book.genre = request.form['genre']
      book.summary = request.form['summary']
      session.commit()
      return redirect(url_for('book', book_id=book_id))
      
    elif request.form['edit_button'] =="Delete":
      print("book delete button has been pressed")
      session.delete(book)
      session.commit()
      print("book has been deleted")
      return redirect(url_for('all_books'))
      
    print("getting from update")
  return render_template('update.html', book=book, ids=book_id, page_title='UPDATE')
      
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
    if string_length(1, 100, review) == False:
      message = "Invalid Review"
      return redirect(url_for('error_406', message = message))
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

@app.route('/406/<message>')
def error_406(message):
  print(message)
  return render_template('406.html', message=message, page_title='Error 406')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)