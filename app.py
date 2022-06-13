import os
import random

import bcrypt
import mysql.connector
from flask import Flask, render_template, request, session, redirect, url_for


config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'FinalProject',
    'raise_on_warnings': True,
    'buffered': True,
}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor(dictionary=True)

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)

'''
DashBoard
'''


@app.route('/')
def index():
    cursor.execute("SELECT * FROM product")
    data = cursor.fetchall()
    AllProduct = list()

    for i in data:
        AllProduct.append(i)
    return render_template('loadhome.html', AllProduct=AllProduct)


'''
Show all the product
'''


@app.route('/home/<string:username>')
def home(username):
    cursor.execute("SELECT * FROM product")
    data = cursor.fetchall()
    AllProduct = list()

    for i in data:
        AllProduct.append(i)
    return render_template('home.html', AllProduct=AllProduct, username=username)


'''
CD Page
'''


@app.route('/CD/<string:username>')
def CDPage(username):
    cursor.execute("SELECT * FROM CD")
    CDdata = cursor.fetchall()

    CDlist = list()
    for i in CDdata:
        CDlist.append(i)
    return render_template('CDPage.html', CDlist=CDlist, username=username)


'''
Book Page
'''


@app.route('/Book/<string:username>')
def BookPage(username):
    cursor.execute("SELECT * FROM BOOK")
    BookData = cursor.fetchall()

    Blist = list()
    for i in BookData:
        Blist.append(i)
    return render_template('Bookpage.html', Blist=Blist, username=username)


'''
resister page
'''


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor.execute("INSERT INTO userdata (username, password) VALUES (%s,%s)", (username, hash_password,))
        cnx.commit()
        session['username'] = request.form['username']
        return redirect(url_for('home', username=username))


'''
login page
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        if username == 'root':
            return render_template('management.html')
        else:
            cursor.execute("SELECT * FROM userdata WHERE username=%s", (username,))
            user = cursor.fetchone()

            if len(user) > 0:
                if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                    if user["password"] == 'root':
                        session['username'] = user['username']
                        return render_template("management.html")
                    elif bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                        session['username'] = user['username']
                        return redirect(url_for('home', username=username))
                else:
                    return render_template("login.html")
            else:
                return render_template("login.html")
    else:
        return render_template("login.html")


'''
upload product page
'''


@app.route('/UploadProduct/<string:username>', methods=['GET', 'POST'])
def UploadProduct(username):
    if request.method == 'GET':
        print('ok')
        return render_template("uploadproduct.html", username=username)
    else:
        ProductType = request.form['product']
        if ProductType == 'cd':
            ProductName = request.form['productname']
            price = request.form['price']
            description = request.form['description']
            username = request.form['username']

            cursor.execute(
                'INSERT INTO CD (ProductName,Price, Description, username) VALUES (%s,%s,%s,%s)',
                (ProductName, price, description, username))
            cnx.commit()

            cursor.execute(
                'INSERT INTO product (ProductName,Price, Description, username) VALUES (%s,%s,%s,%s)',
                (ProductName, price, description, username))
            cnx.commit()

            session['productname'] = ProductName
            session['username'] = username
            return redirect(url_for('profile', username=username))

        elif ProductType == 'book':
            ProductName = request.form['productname']
            price = request.form['price']
            description = request.form['description']
            username = request.form['username']
            cursor.execute(
                'INSERT INTO BOOK (ProductName,Price, Description, username) VALUES (%s,%s,%s,%s)',
                (ProductName, price, description, username))
            cnx.commit()
            cursor.execute(
                'INSERT INTO product (ProductName,Price, Description,username) VALUES (%s,%s,%s,%s)',
                (ProductName, price, description, username))
            cnx.commit()

            session['productname'] = ProductName
            session['username'] = username
            return redirect(url_for('profile', username=username))
        else:
            msg = 'Upload Fail'
            return redirect(url_for('profile', username=username, msg=msg))


'''
product page
'''


@app.route('/<string:username>/products/<int:ProductId>', methods=['GET', 'POST'])
def product(username, ProductId):
    cursor.execute('SELECT * FROM product WHERE ProductId=%s', (ProductId,))
    productData = cursor.fetchone()
    productName = productData['ProductName']
    productId = productData['ProductId']
    productPrice = productData['Price']
    description = productData['Description']
    owner = productData['username']
    username = username

    if request.method == 'GET':
        return render_template("productpage.html", productName=productName, productId=ProductId,
                               productPrice=productPrice, description=description, owner=owner)
    else:
        add = request.form['add']
        if add == 'add':
            cursor.execute(
                'INSERT INTO Scart (ProducId,ProductName, ProductPrice, username) VALUES (%s,%s,%s,%s)',
                (productId, productName, productPrice, username))
            cnx.commit()
            session['ProductId'] = ProductId
            return redirect(url_for('product', username=username, ProductId=ProductId))


'''
edit product
'''


@app.route('/EditProduct/<string:username>/<int:productId>', methods=['POST', 'GET'])
def EditProduct(username, productId):
    cursor.execute('SELECT * FROM product WHERE ProductId=%s', (productId,))
    productData = cursor.fetchone()
    print(productData)
    productName = productData['ProductName']
    print(productName)
    productId = productData['ProductId']
    productPrice = productData['Price']
    description = productData['Description']
    username = username
    if request.method == 'POST':
        print('here')
        Nproductname = request.form['productname']
        Nprice = request.form['price']
        Ndescription = request.form['description']
        print(here)
        if Nproductname != productName or NproductDname != '':
            cursor.execute('UPDATE product SET ProductName=%s WHERE ProductId=%s', (Nproductname, productId,))
            cnx.commit()
        if Nprice != productPrice or Nprice != '':
            cursor.execute('UPDATE product SET Price=%s WHERE ProductId=%s', (Nprice, productId,))
            cnx.commit()
        if Ndescription != description or Ndescription != '':
            cursor.execute('UPDATE product SET Description=%s WHERE ProductId=%s', (Ndescription, productId,))
            cnx.commit()
        session['username'] = username
        return redirect(url_for('profile', username=username))
    else:
        session['productId'] = productId
        return render_template('EditProduct.html', productId=productId)


'''
user profile
'''


@app.route('/profile/<string:username>')
def profile(username):
    cursor.execute('SELECT * FROM product WHERE username=%s', (username,))
    content = cursor.fetchall()

    Plist = list()
    for i in content:
        Plist.append(i)

    session['username'] = username
    return render_template('profile.html', Plist=Plist, username=username)


@app.route('/shoppingCart/<string:username>')
def ShoppingCart(username):
    cursor.execute('SELECT * FROM Scart WHERE username=%s', (username,))
    ProductContent = cursor.fetchall()
    i = 0
    sum = 0
    while i < len(ProductContent):
        sum = sum + int(ProductContent[i]['ProductPrice'])
        i += 1

    ProductList = list()
    for i in ProductContent:
        ProductList.append(i)
    return render_template('UserSCart.html', username=username, ProductList=ProductList, totalPrice=sum)


@app.route('/payment/<string:username>')
def payment(username):
    cursor.execute('SELECT * FROM Scart WHERE username=%s', (username,))
    ProductContent = cursor.fetchall()
    i = 0
    sum = 0
    while i < len(ProductContent):
        sum = sum + int(ProductContent[i]['ProductPrice'])
        i += 1

    ProductList = list()
    for i in ProductContent:
        ProductList.append(i)
    return render_template('payment.html', username=username, ProductList=ProductList, totalPrice=sum)


'''
root user management
'''


@app.route('/management')
def management():
    return render_template('management.html')


@app.route('/management/product')
def management_product():
    cursor.execute("SELECT * FROM product")
    productdata = cursor.fetchall()

    plist = list()
    for i in productdata:
        plist.append(i)
    return render_template('management_product.html', plist=plist)
    '''
     btn = request.form['del']
    if btn == 'del':
        cursor.execute(
                'DELETE FROM product WHERE ProductId=%s',
                (productId, productName, productPrice, username))
        cnx.commit()
        session['ProductId'] = ProductId
       
    '''


@app.route('/management/user')
def management_user():
    cursor.execute("SELECT * FROM userdata")
    userdata = cursor.fetchall()
    ulist = list()
    for i in userdata:
        ulist.append(i)
    return render_template('management_user.html', ulist=ulist)


if __name__ == '__main__':
    app.run(debug=True)
