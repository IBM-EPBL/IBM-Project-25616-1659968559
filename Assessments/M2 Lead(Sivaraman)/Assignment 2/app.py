from flask import Flask, render_template, url_for, request, flash
import sqlite3  
  
app = Flask(__name__)
app.secret_key = "121212"

def connectDB():
    conn = sqlite3.connect('users.db')  
    #Create a user table with email, username, rollno, password
    create_table = """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        username TEXT NOT NULL,
        rollno TEXT NOT NULL,
        password TEXT NOT NULL
    );
    """
    conn.executescript(create_table)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def root():
    return render_template("home.html", title="Home")

@app.route("/signin", methods=('POST', 'GET'))
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        userDB = connectDB()
        findUser = userDB.execute(
            'SELECT username FROM users WHERE password = ? AND email = ?', (password, email)
        ).fetchone()
        
        if findUser is None:
            error = "Incorrect Username/Password."
  
        if error is None:
            return render_template('home.html', title="Home", success="Login Successful")
        flash(error)
        userDB.close()

    return render_template('signin.html', title='Sign In', error=error)

@app.route("/signup", methods=('POST', 'GET'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        rollno = request.form['username']
        
        db = connectDB()
        curr = db.cursor()
        
        curr.execute(
            'INSERT INTO users (email, username, rollno, password) VALUES (?, ?, ?, ?);', (email, username, rollno, password)
        )
        db.commit()
        curr.close()
        db.close()
        return render_template('home.html', title="Home", success="Registration Successful")

    return render_template("signup.html", title="Sign Up")

if __name__ == '__main__':
    app.run(debug=True)