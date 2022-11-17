from app import app
from flask import request, redirect, url_for, render_template, session, json
import ibm_db
from sendGrid import mailto, checkstatus, getProductsBelowThValue


#Connect to DB
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=glr36049;PWD=dcAymdrrrHG3zGIs;","", "")

@app.route("/")
def root():
    return render_template("home.html", title="Home")


@app.route("/signin", methods=('POST', 'GET'))
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT username FROM users WHERE password = '{}' AND email = '{}'".format(password, email)
        stmt = ibm_db.exec_immediate(conn, sql)
        fetchUser = ibm_db.fetch_assoc(stmt)
        if fetchUser == False:
            error = "Incorrect Username/Password."

        if error is None:
            user = fetchUser["USERNAME"]
            session['loggedIn'] = True
            session['id'] = user
            session['email'] = email
            return redirect(url_for('.dashboard', username=user))
    return render_template('signin.html', error=error)


@app.route("/signup", methods=('POST', 'GET'))
def signup():
    error=None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        checkUser = "SELECT * FROM users WHERE username = '{}'".format(username)
        stmt = ibm_db.exec_immediate(conn, checkUser)
        findUser = ibm_db.fetch_assoc(stmt)
        if findUser == False:
            sql = "INSERT INTO users (email, username, password) VALUES ('{}', '{}', '{}');".format(email, username, password)
            ibm_db.exec_immediate(conn, sql)
            return render_template('home.html', title="Home", isRegistered=True)
        error="Username aldready exists."
    return render_template("signup.html", error=error)


@app.route("/<username>/dashboard", methods=('POST', 'GET'))
@app.route("/<username>", methods=('POST', 'GET'))
def dashboard(username):
    fetchPrices = "SELECT p.productname,up.unitprice,up.availablestock FROM products p,userproducts up WHERE p.productid=up.productid AND up.username='{}'".format(username)
    stmt = ibm_db.exec_immediate(conn, fetchPrices)
    productInfo = ibm_db.fetch_assoc(stmt)
    allproducts=[]
    product=[]
    price=[]
    overallValue=0
    while productInfo != False:
        allproducts.append(productInfo)
        product.append(productInfo['PRODUCTNAME'])
        price.append(productInfo['UNITPRICE']*productInfo['AVAILABLESTOCK'])
        overallValue=overallValue+(productInfo['UNITPRICE']*productInfo['AVAILABLESTOCK'])
        productInfo = ibm_db.fetch_assoc(stmt)
    
    fetchPrices = "SELECT * FROM threshold_value WHERE email='{}';".format(session['email'])
    stmt = ibm_db.exec_immediate(conn, fetchPrices)
    productInfo = ibm_db.fetch_assoc(stmt)
    if productInfo == False:
        productsBelowThValue = []
    else:
        productsBelowThValue = getProductsBelowThValue(conn, session['email'], username)

    if request.method=='POST':
        th_value = request.form['threshold']
        sql = "INSERT INTO threshold_value (email, th_value) VALUES ('{}', '{}');".format(session['email'], th_value)
        ibm_db.exec_immediate(conn, sql)   
        return redirect(url_for('.dashboard', username=username))
    return render_template("dashboard.html", username=username, success=True, products=allproducts, product=product, price=price, overallValue=overallValue, productsBelowThValue=productsBelowThValue)


@app.route("/<username>/manageProducts", methods=('POST', 'GET'))
def manageProducts(username):
    sql = "SELECT up.productid,p.productname,up.availablestock FROM products p, users u, userproducts up WHERE u.username=up.username AND p.productid=up.productid AND u.username='{}';".format(username)
    stmt = ibm_db.exec_immediate(conn, sql)
    getProducts = ibm_db.fetch_assoc(stmt)
    products = []
    while getProducts != False:
        products.append(getProducts)
        getProducts = ibm_db.fetch_assoc(stmt)
    return render_template("productsM.html", username=username, success=True, products=products)


@app.route("/<username>/manageProducts/edit=<pid>,action=<action>", methods=('POST', 'GET'))
def editProduct(username, pid, action):
    if request.method == 'POST':
        stock = int(request.form['newstock'])
        checkAvailable = "SELECT * FROM userproducts WHERE productid='{}' AND username='{}';".format(pid, username)
        statement = ibm_db.exec_immediate(conn, checkAvailable)
        productDetails = ibm_db.fetch_assoc(statement)
        available = productDetails['AVAILABLESTOCK']
        if action == "add":
            stock = available + stock
        else:
            stock = available - stock
            checkstatus(conn, session['email'], username)
        updateQuery = "UPDATE userproducts SET availablestock='{}' WHERE productid='{}' AND username='{}';".format(stock, pid, username)
        ibm_db.exec_immediate(conn, updateQuery)
    return redirect(url_for('.manageProducts', username=username))


@app.route("/<username>/manageProducts/delete=<pid>", methods=('POST', 'GET'))
def deleteProduct(username, pid):
    deleteQuery = "DELETE FROM userproducts WHERE productid='{}' AND username='{}';".format(pid, username)
    ibm_db.exec_immediate(conn, deleteQuery)
    return redirect(url_for('.manageProducts', username=username))


@app.route("/<username>/addProduct", methods=('POST', 'GET'))
def addProducts(username):
    error = None
    isValueSet = "SELECT * FROM threshold_value WHERE email='{}';".format(session['email'])
    statement = ibm_db.exec_immediate(conn, isValueSet)
    isSet = ibm_db.fetch_assoc(statement)
    if isSet == False:
        return render_template("productsM.html", username=username, alertUser=True)

    if request.method == 'POST':
        pid = request.form['pid']
        pname = request.form['pname']
        addstock = int(request.form['stock'])
        unitprice = int(request.form['unitprice']) 

        checkDuplicate = "SELECT * FROM products WHERE productid='{}' AND productname<>'{}';".format(pid, pname)
        statement = ibm_db.exec_immediate(conn, checkDuplicate)
        productDetails = ibm_db.fetch_assoc(statement)
        if productDetails != False:
            error = "Product ID is aldready assigned"
            return render_template("addProduct.html", username=username, success=True, error=error)

        checkAvailable = "SELECT * FROM userproducts WHERE productid='{}' AND username='{}';".format(pid, username)
        statement = ibm_db.exec_immediate(conn, checkAvailable)
        productDetails = ibm_db.fetch_assoc(statement)
        if productDetails == False:
            checkProduct = "SELECT * FROM products WHERE productid='{}';".format(pid)
            statement = ibm_db.exec_immediate(conn, checkProduct)
            productDetails = ibm_db.fetch_assoc(statement)
            if productDetails == False:
                addProduct = "INSERT INTO products(productid, productname) VALUES ('{}', '{}');".format(pid, pname)
                ibm_db.exec_immediate(conn, addProduct)

            updateStock = "INSERT INTO userproducts(productid, username, availablestock, unitprice) VALUES ('{}', '{}', '{}', '{}');".format(pid, username, addstock, unitprice)
            ibm_db.exec_immediate(conn, updateStock)

        else:
            addstock = addstock + productDetails['AVAILABLESTOCK']
            updateStock = "UPDATE userproducts SET availablestock='{}' WHERE productid='{}' AND username='{}';".format(addstock, pid, username)
            ibm_db.exec_immediate(conn, updateStock)
        return redirect(url_for('.manageProducts', username=username))
    return render_template("addProduct.html", username=username, success=True, error=error)


@app.route('/')
def logout():
   session.clear()
   return render_template('home.html')
