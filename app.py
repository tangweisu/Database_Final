import os

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
    return render_template('home.html')


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
    return render_template('home.html', AllProduct=AllProduct,username=username)


'''
CD Page
'''


@app.route('/CD/<string:username>')
def CDPage():
    cursor.execute("SELECT * FROM CD")
    CDdata = cursor.fetchall()

    CDlist = list()
    for i in CDdata:
        CDlist.append(i)
    return render_template('CDPage.html', CDlist=CDlist)


'''
Book Page
'''


@app.route('/Book/<string:username>')
def BookPage():
    cursor.execute("SELECT * FROM BOOK")
    BookData = cursor.fetchall()

    Blist = list()
    for i in BookData:
        Blist.append(i)
    return render_template('Bookpage.html', Blist=Blist)


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
        return redirect(url_for('home'))


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
                    return "Error password and email not match"
            else:
                return "Error user not found"
    else:
        return render_template("login.html")


'''
upload product page
'''


@app.route('/UploadProduct/<string:username>', methods=['GET', 'POST'])
def UploadProduct():
    if request.method == 'GET':
        return render_template("uploadproduct.html")
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
    username = username
    if request.method == 'GET':
        return render_template("productpage.html", productId=ProductId, productData=productData)
    else:
        add = request.form['add']
        if add == 'add':
            cursor.execute(
                'INSERT INTO Scart (ProducId,ProductName, ProductPrice, username) VALUES (%s,%s,%s,%s)',
                (productId, productName, productPrice, username))
            cnx.commit()
            session['ProductId'] = ProductId
            return redirect(url_for('product', ProductId=ProductId, username=username))


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

    ProductList = list()
    print(ProductContent)
    for i in ProductContent:
        ProductList.append(i)
    return render_template('UserSCart.html', username=username, ProductList=ProductList)


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
    return render_template('management_product.html', productdata=productdata)


@app.route('/management/user')
def management_user():
    cursor.execute("SELECT * FROM userdata")
    userdata = cursor.fetchall()
    return render_template('management_user.html', userdata=userdata)


if __name__ == '__main__':
    app.run(debug=True)
