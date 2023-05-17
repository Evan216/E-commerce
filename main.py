from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text, Table, MetaData, select, engine, and_
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# # Instantiate Flask object named app
app = Flask(__name__)

# # Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Hotdog724!@localhost/Final'

# Creates a connection to the database
connection = "mysql://root:Hotdog724!@localhost/Final"
engine = create_engine(connection, echo=True)
conn = engine.connect()
db = SQLAlchemy(app)

@app.route("/")
def index():
    shirts = db.session.execute("SELECT * FROM shirts ORDER BY onSalePrice")
    shirts = list(shirts)
    shirtsLen = len(shirts)
    # Initialize variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.session.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, image, price, id")
        shoppingCart = list(shoppingCart)  # Convert cursor result object to list
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        shirts = db.session.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")
        shirts = list(shirts)
        shirtsLen = len(shirts)
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ( "index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/buy/")
def buy():
    # Initialize shopping cart variables
    shoppingCart = []
    totItems, total = 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        # Select info of selected shirt from database
        goods = db.session.execute("SELECT * FROM shirts WHERE id = :id", {'id': id}).fetchone()
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        if goods["onSale"] == 1:
            price = goods["onSalePrice"]
        else:
            price = goods["price"]
        samplename = goods["samplename"]
        image = goods["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.session.execute("INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)", {'id': id, 'qty': qty, 'samplename': samplename, 'image': image, 'price': price, 'subTotal': subTotal})
        db.session.commit()  # Commit the transaction
        shoppingCart = db.session.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, image, price, id")
        shoppingCart = list(shoppingCart)
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Select all shirts for home page view
        shirts = db.session.execute("SELECT * FROM shirts ORDER BY samplename ASC")
        shirts = list(shirts)
        shirtsLen = len(shirts)
        # Go back to home page
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, session=session)

@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    shops = list(shoppingCart)
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        db.session.execute("DELETE FROM cart WHERE id = :id", params={"id": id})
        # Select info of selected shirt from database
        goods = db.session.execute("SELECT * FROM shirts WHERE id = :id", params={"id": id})
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        row = goods.fetchone()
        if(row["onSale"] == 1):
            price = row["onSalePrice"]
        else:
            price = row["price"]
        samplename = row["samplename"]
        image = row["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.session.execute("INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)", params={"id": id, "qty": qty, "samplename": samplename, "image": image, "price": price, "subTotal": subTotal})
        shoppingCart = db.session.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, image, price, id")

        shoppingCart = list(shoppingCart)
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Go back to cart page
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('typeClothes'):
        query = request.args.get('typeClothes')
        shirts = list(db.session.execute("SELECT * FROM shirts WHERE typeClothes = :query ORDER BY samplename ASC",
                                         {'query': query}))
    if request.args.get('sale'):
        query = request.args.get('sale')
        shirts = db.session.execute("SELECT * FROM shirts WHERE onSale = :query ORDER BY samplename ASC",
                                    {'query': query})
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shirts = db.session.execute("SELECT * FROM shirts WHERE id = :query ORDER BY samplename ASC", {'query': query})
    if request.args.get('kind'):
        query = request.args.get('kind')
        shirts = db.session.execute("SELECT * FROM shirts WHERE kind = :query ORDER BY samplename ASC",
                                    {'query': query})
    if request.args.get('price'):
        shirts = db.session.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")

    shoppingCart = db.session.execute(
        "SELECT samplename, MAX(image), SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, price, id")
    shops = list(shoppingCart) if shoppingCart is not None else []
    shopLen = len(shops)

    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Rebuild shopping cart
        shoppingCart = db.session.execute(
            "SELECT samplename, MAX(image), SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, price, id")
        shops = list(shoppingCart) if shoppingCart is not None else []
        shopLen = len(shops)
        for i in range(shopLen):
            total += shops[i]["SUM(subTotal)"]
            totItems += shops[i]["SUM(qty)"]
        # Render filtered view
        return render_template ("index.html", shoppingCart=shops, shirts=shirts, shopLen=shopLen, shirtsLen=len(shirts), total=total, totItems=totItems, display=display, session=session )
    # Render filtered view
    return render_template ( "index.html", shirts=shirts, shoppingCart=shops, shirtsLen=len(shirts), shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/checkout/")
def checkout():

    order = db.session.execute("SELECT * from cart")
    # Update purchase history of current customer
    for item in order:
        existing_purchase = db.session.execute("SELECT * FROM purchases WHERE uid=:uid AND shirt_id=:shirt_id AND samplename=:samplename AND image=:image",
                                                {"uid": session["uid"], "shirt_id": item["id"], "samplename": item["samplename"], "image": item["image"]}).fetchone()
        if existing_purchase:
            # If the purchase already exists, update the quantity
            db.session.execute("UPDATE purchases SET quantity=:quantity WHERE id=:id",
                                {"id": existing_purchase["id"], "quantity": existing_purchase["quantity"] + item["qty"]})
        else:
            # Otherwise, insert a new row
            db.session.execute(
                "INSERT INTO purchases (uid, shirt_id, samplename, image, quantity, cart_id) VALUES(:uid, :shirt_id, :samplename, :image, :quantity, :cart_id)",
                {"uid": session["uid"], "shirt_id": item["id"], "samplename": item["samplename"], "image": item["image"],
                 "quantity": item["qty"], "cart_id": item["cart_id"]})

    # Clear shopping cart
    db.session.execute("DELETE from cart")
    db.session.commit()
    shoppingCart = []
    shops = list(shoppingCart)
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Redirect to home page
    return redirect('/')





@app.route("/remove/", methods=["GET"])
def remove():
    # Get the id of shirt selected to be removed
    out = int(request.args.get("id"))
    # Remove shirt from shopping cart
    db.session.execute("DELETE from cart WHERE id=:id", {'id': out})
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = db.session.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, image, price, id")
    shoppingCart = list(shoppingCart)
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # Render log in page
    return render_template("new.html")


@app.route("/logged/", methods=["POST"])
def logged():
    # Get log in info from log in form
    user = request.form["username"].lower()
    pwd = request.form["password"]
    # Make sure form input is not blank and re-render log in page if blank
    if user == "" or pwd == "":
        return render_template("login.html")
    # Find out if info in form matches a record in user database
    query = text("SELECT * FROM users WHERE username = :user AND password = :pwd")
    rows = db.session.execute(query, {"user": user, "pwd": pwd})

    # If username and password match a record in database, set session variables
    count = 0
    for row in rows:
        count += 1
        session['user'] = user
        session['time'] = datetime.now()
        session['uid'] = row["id"]

    if count == 1:
        # Redirect to Home Page
        if 'user' in session:
            return redirect("/")
    else:
        # If username is not in the database return the log in page
        return render_template("login.html", msg="Wrong username or password.")


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shops = list(shoppingCart)
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all shirts ever bought by current user
    myShirts = db.session.execute("SELECT * FROM purchases WHERE uid=:uid", {"uid": session.get("uid", None)})
    shirts = list(myShirts)  # convert CursorResult object to list
    myShirtsLen = len(shirts)  # calculate length of list
    # Render table with shopping history of current user
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShirts=shirts, myShirtsLen=myShirtsLen)

@app.route("/logout/")
def logout():
    # clear shopping cart
    db.session.execute("DELETE from cart")
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register/", methods=["POST"])
def registration():
    # Get info from form
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]

    # See if username already in the database
    rows = db.session.execute("SELECT * FROM users WHERE username = :username", {"username": username})

    # If username already exists, alert user
    if rows.fetchone() is not None:
        return render_template("new.html", msg="Username already exists!")

    # If new user, upload his/her info into the users database
    try:
        db.session.execute(
            "INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
            {"username": username, "password": password, "fname": fname, "lname": lname, "email": email})
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return render_template("new.html", msg="Error occurred while registering user.")

    # Render login template
    return render_template("login.html")

@app.route("/cart/")
def cart():
    if 'user' in session:
        # Clear shopping cart variables
        totItems, total, display = 0, 0, 0
        # Grab info currently in database
        shoppingCart = db.session.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename, image, price, id")
        # Get variable values
        shops = list(shoppingCart)
        shopLen = len(shops)
        for i in range(shopLen):
            total += shops[i]["SUM(subTotal)"]
            totItems += shops[i]["SUM(qty)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shops, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


class reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)


@app.route('/reviews/', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        rating = request.form['rating']
        description = request.form['description']
        # Add the review to the database
        review = reviews(rating=rating, description=description)
        db.session.add(review)
        db.session.commit()
        flash('Thank you for submitting a review!')
        return redirect(url_for('reviews'))
    else:
        # Get the desired rating filter (if any)
        rating_filter = request.args.get('rating')
        # Retrieve the reviews from the database
        if rating_filter is not None:
            # Filter the reviews by rating
            reviews = reviews.query.filter_by(rating=rating_filter).all()
        else:
            # Retrieve all reviews
            reviews = reviews.query.all()
        return render_template('reviews.html', reviews=reviews, rating_filter=rating_filter)

@app.route('/viewchats/')
def viewchats():
    user_id = session.get('id')

    query = text("SELECT c.chat_id, c.sender_id, c.recipient_id, c.text, u.username AS sender_username "
                 "FROM finalchats c "
                 "INNER JOIN users u ON c.sender_id = u.id "
                 "WHERE c.sender_id = :user_id OR c.recipient_id = :user_id")
    params = {"user_id": user_id}
    result = conn.execute(query, params)
    messages = []
    for row in result:
        messages.append(row)
    return render_template('chats.html', messages=messages)


@app.route('/send_message/', methods=['POST'])
def send_message():
    sender_id = session.get('id')
    recipient_id = request.form['recipient_id']
    message_text = request.form['text']
    chat_id = f"chat_{sender_id}_{recipient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    query = text(
        "INSERT INTO finalchats (chat_id, sender_id, recipient_id, text)"
        " VALUES (:chat_id, :sender_id, :recipient_id, :text)")
    params = {"chat_id": chat_id, "sender_id": sender_id, "recipient_id": recipient_id, "text": message_text}
    conn.execute(query, params)
    conn.commit()

    flash("Message sent successfully!")
    return redirect(url_for('viewchats'))

@app.route('/account/', methods=["GET"])
def account():
    id = session['id']
    user = User.query.get(id)
    query = text("SELECT username, fname, lname, email FROM users WHERE id = :id")
    result = db.session.execute(query, {"id": id}).fetchone()
    if result is not None:
        username, fname, lname, email = result
    else:
        # handle the case when the user is not found
        # for example, redirect to the login page
        return redirect(url_for('login'))
    return render_template('account.html', user=user, username=username, fname=fname, lname=lname, email=email)





if __name__ == '__main__':
    app.run(debug=True)