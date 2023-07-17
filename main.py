#Book Club 2023

from flask import Flask, render_template, abort
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