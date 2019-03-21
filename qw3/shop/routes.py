import os
from flask import render_template, url_for, request, redirect, flash, session
from shop import app, db
from shop.models import Author, Book, User
from shop.forms import RegistrationForm, LoginForm, SortingForm, ReviewForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST']) 
def home():
    books = Book.query.all()
    form = SortingForm()
    if form.validate_on_submit():
        if form.dropdown.data == "AZ":
            books = Book.query.order_by(Book.title.asc()).all()
        if form.dropdown.data == "ZA":
            books = Book.query.order_by(Book.title.desc()).all()
        if form.dropdown.data == "LowtoHigh":
            books = Book.query.order_by(Book.price.asc()).all()
        if form.dropdown.data == "HightoLow":
            books = Book.query.order_by(Book.price.desc()).all()            
    return render_template('home.html', books=books, title='The Nerf Store', form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    if form.validate_on_submit():
        if form.review.data != "":
            update_this = book.query.filter_by(id=book_id).first()
            review = form.review.data
            update_this.review = review
            db.session.commit()
            flash('Your review has been submitted. ')

    return render_template('book.html', book=book, form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created.  You can now log in.')
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('You are now logged in.')
            return redirect(url_for('home'))
        flash('Invalid username or password.')

        return render_template('login.html', form=form)

    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(book_id)

    flash("The book is added to your shopping cart!")
    return redirect("/cart")


@app.route("/cart", methods=['GET', 'POST'])
def cart_display():
    if "cart" not in session:
        flash('There is nothing in your cart.')
        return render_template("cart.html", display_cart = {}, total = 0)
    else:
        items = session["cart"]
        cart = {}

        total_price = 0
        total_quantity = 0
        for item in items:
            book = Book.query.get_or_404(item)

            total_price += book.price
            if book.id in cart:
                cart[book.id]["quantity"] += 1
            else:
                cart[book.id] = {"quantity":1, "title": book.title, "price":book.price}
            total_quantity = sum(item['quantity'] for item in cart.values())


        return render_template("cart.html", title='Your Shopping Cart', display_cart = cart, total = total_price, total_quantity = total_quantity)

    return render_template('cart.html')

@app.route("/delete_book/<int:book_id>", methods=['GET', 'POST'])
def delete_book(book_id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].remove(book_id)

    flash("The book has been removed from your shopping cart!")

    session.modified = True

    return redirect("/cart")

@app.route("/add_to_wishlist/<int:book_id>")
def add_to_wishlist(book_id):
    if "wishlist" not in session:
        session["wishlist"] = []

    session["wishlist"].append(book_id)

    flash("The book is added to your Wsishlist!")
    return redirect("/wishlist")    

@app.route("/wishlist", methods=['GET', 'POST'])
def wishlist_display():
    if "wishlist" not in session:
        flash('There is nothing in your wishlist.')
        return render_template("wishlist.html", display_wishlist = {}, total = 0)
    else:
        items = session["wishlist"]
        wishlist = {}

        total_price = 0
        total_quantity = 0
        for item in items:
            book = Book.query.get_or_404(item)

            total_price += book.price
            if book.id in wishlist:
                wishlist[book.id]["quantity"] += 1
            else:
                wishlist[book.id] = {"quantity":1, "title": book.title, "price":book.price}
            total_quantity = sum(item['quantity'] for item in wishlist.values())


        return render_template("wishlist.html", title='Your wishlist', display_wishlist = wishlist, total = total_price, total_quantity = total_quantity)

    return render_template('wishlist.html')    



@app.route("/delete_book_wish/<int:book_id>", methods=['GET', 'POST'])
def delete_book_wish(book_id):
    if "wishlist" not in session:
        session["wishlist"] = []

    session["wishlist"].remove(book_id)

    flash("The item has been removed from your Wishlist!")

    session.modified = True

    return redirect("/wishlist")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html", title="Checkout")




