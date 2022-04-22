from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'team3'
UPLOAD_FOLDER = 'static/uploads'
UPLOAD_SELLER = 'static/selleruploads'
UPLOAD_FEATURED = 'static/featureditem'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_SELLER'] = UPLOAD_SELLER
app.config['UPLOAD_FEATURED'] = UPLOAD_FEATURED


def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = ?", (session['email'],))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId,))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)


@app.route("/")
def home():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products limit 4 offset 3')
        itemData = cur.fetchall()

        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,
                           categoryData=categoryData)


@app.route("/displayCategory")
def displayCategory():
    loggedIn, firstName, noOfItems = getLoginDetails()
    categoryId = request.args.get("categoryId")
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?",
            (categoryId,))
        data = cur.fetchall()
    conn.close()
    categoryName = data[0][4]
    data = parse(data)
    return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, categoryName=categoryName)


@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect("/")
    else:
        return render_template('login.html', error='')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect("/")
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)


@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?',
                    (productId,))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems)
'''
@app.route("/featuredDescription")
def productDescription1():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                'SELECT productId,Seller_name, Product_name, price1, image1, stock1 FROM featured1 WHERE productId = ?',
                (productId,))
            productData = cur.fetchone()
            msg="Success"
            print(msg)

        except:
            conn.rollback()
            msg="Not successfull"
            print(msg)

    conn.close()
    return render_template("productDescriptionfeaature.html", data=productData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems)
'''
def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Parse form data
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                    hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode,
                    city, state, country, phone))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)


@app.route("/registerationForm")
def registrationForm():
    return render_template("registration.html")


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect("/")


@app.route("/add")
def admin():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)


@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        # Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    '''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''',
                    (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return "Product Added successfully <br><a href='/add'>Add more items</a><br><a href='/'>Go back to home page</a>"


@app.route("/remove")
def remove():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)


@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId,))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect("/")


@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?",
            (session['email'],))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems)





@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'],))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg = "Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")


@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'],))
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect("/")

'''
@app.route("/faddToCart")
def addToCart1():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'],))
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO fkart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect("/")
'''
@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute(
            "SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?",
            (userId,))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products=products, totalPrice=totalPrice, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems)


@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect("/")


@app.route('/account/profile/profiledelete')
def prof():
    return "<a href='/account/profile/profiledelete/sure'>Do u still want to delete your profile</a>"

@app.route('/account/profile/profiledelete/sure')
def prof1():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']

    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
            userid = cur.fetchone()[0]

            cur.execute('DELETE FROM users WHERE userId = ?', (userid,))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return "Your profile is successfully deleted"




# Admin
@app.route('/Alogin', methods=["GET"])
def Admin1():
    return render_template("LoginAdmin.html")


@app.route('/Adminlogin', methods=["POST"])
def admin12():
    name = request.form["aid"]
    password = request.form["pass"]

    if name == "admin" and password == 'adminrock123':
        return render_template("Admin.html")
    else:
        return "login failed"


@app.route('/addseller',methods=["GET"])
def addsel():
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("add_seller.html",loggedIn=loggedIn,firstName=firstName,noOfItems=noOfItems)


@app.route("/addseller1", methods=["GET", "POST"])
def addItem1():
    if request.method == "POST":
        Sellerid = request.form['addseller']

        # Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            file1 = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], file1))
        imagename = file1
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''select name1,price1,description1,image1,stock1,categoryId from seller2 where sId=?''',(Sellerid,))
                r=cur.fetchone()
                name=r[0]
                price=r[1]
                description = r[2]
                stock=r[4]
                categoryId=r[5]
                cur.execute(
                    '''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''',
                    (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return "Product Added successfully"



@app.route('/Viewcomplain')
def view1():

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT users.userId, users.firstName,users.lastName ,complaint2.userId,complaint2.C_ID,complaint2.description,complaint2.orderId,complaint2.feedback from users,complaint2  where users.userId = complaint2.userId")
        rows = cur.fetchall()


    return render_template("view1.html", rows=rows)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS





"""
@app.route("/addf", methods=["GET"])
def admin123():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add1.html', categories=categories)


@app.route("/addItemf", methods=["POST"])
def addItem42():
    if request.method == "POST":
        name = request.form['name']
        namepro = request.form['namep']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        # Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filenam = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FEATURED'], filenam))
        imagename = filenam
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    '''INSERT INTO featured1 (Seller_name,Product_name, price1, description1, image1, stock1, categoryId) VALUES (?, ?, ? , ?, ?, ?, ?)''',
                    (name, namepro, price, description, imagename, stock, categoryId))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return "Product Added successfully"

"""
# seller
@app.route("/seller1", methods=["GET", "POST"])
def seller1():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('seller.html', categories=categories)


@app.route("/sellerop1", methods=["POST"])
def seller2():
    if request.method == "POST":
        seller_name1 = request.form['sname']
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        # Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filena = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_SELLER'], filena))
        imagename = filena
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    '''INSERT INTO seller2(seller_name,name1, price1, description1, image1, stock1, categoryId) VALUES (?, ?, ?, ?, ?, ?,?)''',
                    (seller_name1, name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return "Product Added successfully"


# complain
@app.route("/account/profile/complain1", methods=["GET", "POST"])
def com1():
    if 'email' not in session:
        return redirect('/')
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("complain.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/account/profile/complain1/comsuccess",methods=["POST"])
def com12():
    if request.method == "POST":
        order_id = request.form['orderid1']
        descripiton = request.form['DESCRIPTION']
        feedback = request.form['FEEDBACK']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'],))
        userid = cur.fetchone()[0]
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                t=(userid, order_id, descripiton, feedback)
                cur.execute('''INSERT INTO complaint2(userId,orderId,description, feedback)  VALUES(? , ?, ?, ?)''',t)
                conn.commit()
                msg = "added successfully"
            except:
                msg = "error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return "Your complain is registered with us, Sit back and relax"


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

#checkout

@app.route('/checkout')
def checkpoint():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        try:
            cur.execute("INSERT INTO order_ack1 (userId) VALUES (?)", (userId,))
            conn.commit()

            msg = "Order placed successfully"
            cur.execute("select * from order_ack1 ")
            k=cur.fetchall()
            cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
            userId = cur.fetchone()[0]
            cur.execute(
                "SELECT products.productId, products.name, products.price, products.stock FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?",
                (userId,))
            products = cur.fetchall()
            totalPrice = 0
            name=''
            for row in products:
                totalPrice += row[2]
            for r in products:
                name+=row[1]
            print(msg)
            cur.execute("delete from kart where userId=?", (userId,))
            conn.commit()
            stock = 0
            for row in products:
                stock = row[3]-1
                cur.execute("UPDATE products SET stock = ? WHERE productId =?", (stock, row[0]))
            conn.commit()
        except:
            conn.rollback()
            msg = "Error occured"
            print(msg)
    conn.close()
    return render_template("ack.html", k=k,msg=msg, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,totalPrice=totalPrice ,name=name,stock=stock)



if __name__ == '__main__':
    app.run(debug=True)
