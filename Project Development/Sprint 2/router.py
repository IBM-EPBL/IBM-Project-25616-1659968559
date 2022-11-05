from app import app
from flask import request, redirect, url_for, jsonify, render_template, flash
import ibm_db


def connectDB():
    ##Enter your credentials
    conn=None
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
        sql = "SELECT username FROM users WHERE password = '{0}' AND email = '{1}'".format(
            password, email)
        stmt = ibm_db.exec_immediate(userDB, sql)
        findUser = ibm_db.fetch_assoc(stmt)
        if findUser == False:
            error = "Incorrect Username/Password."

        while findUser != False:
            user = findUser["USERNAME"]
            break

        if error is None:
            return redirect(url_for('.dashboard', username=user))

    return render_template('signin.html', title='Sign In', error=error)


@app.route("/signup", methods=('POST', 'GET'))
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        userDB = connectDB()
        uname = "SELECT * FROM users WHERE username = '{0}'".format(username)
        stmt = ibm_db.exec_immediate(userDB, uname)
        findUser = ibm_db.fetch_assoc(stmt)
        if findUser == False:
            sql = "INSERT INTO users (email, username, password) VALUES ('{0}', '{1}', '{2}');".format(
                email, username, password)
            ibm_db.exec_immediate(userDB, sql)
            return render_template('home.html', title="Home", success="Registration Successful")
        error = "Username aldready exists."
    return render_template("signup.html", title="Sign Up", error=error)


@app.route("/<username>/dashboard")
@app.route("/<username>")
def dashboard(username):
    return render_template("dashboard.html", username=username, success=True)


@app.route("/<username>/manageProducts", methods=('POST', 'GET'))
def manageProducts(username):
    userDB = connectDB()
    sql = "SELECT up.productid,p.productname,up.availablestock FROM products p, users u, userproducts up WHERE u.username=up.username AND p.productid=up.productid AND u.username='{0}';".format(
        username)
    stmt = ibm_db.exec_immediate(userDB, sql)
    getProducts = ibm_db.fetch_assoc(stmt)
    products = []
    while getProducts != False:
        products.append(getProducts)
        getProducts = ibm_db.fetch_assoc(stmt)
    return render_template("productsM.html", username=username, success=True, products=products)


@app.route("/<username>/manageProducts/data-edit=<pid>", methods=('POST', 'GET'))
def editProduct(username, pid):
    if request.method == 'POST':
        userDB = connectDB()
        stock = request.form['newstock']
        updateQuery = "UPDATE userproducts SET availablestock='{0}' WHERE productid='{1}' AND username='{2}';".format(
            stock, pid, username)
        ibm_db.exec_immediate(userDB, updateQuery)
        return redirect(url_for('.manageProducts', username=username))
    return redirect(url_for('.manageProducts', username=username))


@app.route("/<username>/manageProducts/data-delete=<pid>", methods=('POST', 'GET'))
def deleteProduct(username, pid):
    userDB = connectDB()
    deleteQuery = "DELETE FROM userproducts WHERE productid='{0}' AND username='{1}';".format(
        pid, username)
    ibm_db.exec_immediate(userDB, deleteQuery)
    return redirect(url_for('.manageProducts', username=username))


@app.route("/<username>/addProduct", methods=('POST', 'GET'))
def addProducts(username):
    userDB = connectDB()
    error = None
    if request.method == 'POST':
        pid = request.form['pid']
        pname = request.form['pname']
        addstock = int(request.form['stock'])

        checkDuplicate = "SELECT * FROM products WHERE productid='{0}' AND productname<>'{1}';".format(
            pid, pname)
        statement = ibm_db.exec_immediate(userDB, checkDuplicate)
        productDetails = ibm_db.fetch_assoc(statement)
        if productDetails != False:
            error = "Product ID is aldready assigned"
            return render_template("addProduct.html", username=username, success=True, error=error)

        checkAvailable = "SELECT * FROM userproducts WHERE productid='{0}' AND username='{1}';".format(
            pid, username)
        statement = ibm_db.exec_immediate(userDB, checkAvailable)
        productDetails = ibm_db.fetch_assoc(statement)
        if productDetails == False:
            checkProduct = "SELECT * FROM products WHERE productid='{0}';".format(pid)
            statement = ibm_db.exec_immediate(userDB, checkProduct)
            productDetails = ibm_db.fetch_assoc(statement)
            if productDetails == False:
                addProduct = "INSERT INTO products(productid, productname) VALUES ('{0}', '{1}');".format(
                pid, pname)
                ibm_db.exec_immediate(userDB, addProduct)
            
            updateStock = "INSERT INTO userproducts(productid, username, availablestock) VALUES ('{0}', '{1}', '{2}');".format(
                pid, username, addstock)
            ibm_db.exec_immediate(userDB, updateStock)
        else:
            while productDetails != False:
                available = productDetails['AVAILABLESTOCK']
                productDetails = ibm_db.fetch_assoc(statement)
            addstock = addstock+available
            updateStock = "UPDATE userproducts SET availablestock='{0}' WHERE productid='{1}' AND username='{2}';".format(
                addstock, pid, username)
            ibm_db.exec_immediate(userDB, updateStock)
        return redirect(url_for('.manageProducts', username=username))
    return render_template("addProduct.html", username=username, success=True, error=error)


'''@app.route("/<username>/manageLocations")
    def manageLocations(username):
    return render_template("locationsM.html", username=username, success=True)'''
