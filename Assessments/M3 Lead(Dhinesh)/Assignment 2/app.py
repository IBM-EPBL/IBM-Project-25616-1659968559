from flask import Flask, render_template, url_for, request, flash
import ibm_db  
  
app = Flask(__name__)
app.secret_key = "121212"

"""
Create Table 'Users' in IBM Cloud DB2 using following SQL query:
---------------------------------------------------------------------------
CREATE TABLE USERS(
	id INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),
	email VARCHAR(30) NOT NULL,
	username VARCHAR(20) NOT NULL,
	rollno VARCHAR(10) NOT NULL,
	password VARCHAR(30) NOT NULL,
	PRIMARY KEY(id)
);
"""

def connectDB():
    #Enter your IBM DB2 credentials here
    conn=ibm_db.connect("DATABASE=;HOSTNAME=;PORT=;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=;PWD=;","","")
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
        sql = "SELECT username FROM users WHERE password = '{0}' AND email = '{1}'".format(password, email)
        stmt = ibm_db.exec_immediate(userDB, sql)
        findUser = ibm_db.fetch_assoc(stmt)

        if findUser == False:
            error = "Incorrect Username/Password."
        
        while findUser != False:
            success = "Hey " + findUser["USERNAME"]
            findUser = ibm_db.fetch_assoc(stmt)

        if error is None:
            return render_template('home.html', title="Home", success=success)
        flash(error)

    return render_template('signin.html', title='Sign In', error=error)

@app.route("/signup", methods=('POST', 'GET'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        rollno = request.form['rollno']
        
        userDB = connectDB()
        sql = "INSERT INTO users (email, username, rollno, password) VALUES ('{0}', '{1}', '{2}', '{3}');".format(email, username, rollno, password)
        ibm_db.exec_immediate(userDB, sql)
        return render_template('home.html', title="Home", success="Registration Successful")

    return render_template("signup.html", title="Sign Up")

if __name__ == '__main__':
    app.run(debug=True)