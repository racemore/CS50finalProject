import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///weebtube.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    shows = db.execute("SELECT title, image_url, genre, episodes, rating FROM anime ORDER BY rating DESC LIMIT 10")
    return render_template("top_ten.html", shows=shows)


@app.route("/rate", methods=["GET", "POST"])
@login_required
def rate():
    if request.method == "GET":
        return render_template("rate.html")

    # check for invalid inputs
    user_rating = int(request.form.get("rate"))
    title = request.form.get("title").lower()
    comment = request.form.get("comment")

    # check if title exists (case insensitive)
    check_title = db.execute("SELECT title, id FROM anime WHERE LOWER(title) = ? OR LOWER(title_english) = ?", title, title)
    if not check_title:
        flash("Invalid title. Please try again.",'warning')
        return render_template("rate.html")

    # check user rating
    if user_rating < 0:
        flash("Invalid rating. Please try again.",'warning')
        return render_template("rate.html")

    title_id = check_title[0]["id"]

    # update user rating if already rated before
    rated = db.execute("SELECT rating FROM ratings WHERE anime_id = ? AND user_id=?", title_id, session["user_id"])
    if not rated:
        db.execute("INSERT INTO ratings (user_id, anime_id, rating, comment) VALUES (?, ?, ?, ?)",
               session["user_id"], title_id, user_rating, comment)
    else:
        db.execute("UPDATE ratings SET rating=?, comment=?, time=CURRENT_TIMESTAMP WHERE anime_id=? AND user_id=?", user_rating, comment, title_id, session["user_id"])

    latest_rating = db.execute("SELECT ROUND(AVG(rating),2) FROM ratings WHERE anime_id=?", title_id)
    db.execute("UPDATE anime SET rating = ? WHERE id=?", latest_rating[0]["ROUND(AVG(rating),2)"], title_id)
    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    show_history = db.execute("SELECT anime.title, ratings.rating, ratings.comment, ratings.time FROM ratings JOIN anime ON anime.id = ratings.anime_id WHERE user_id = ? ORDER BY time DESC", session["user_id"])

    return render_template("history.html", show_history=show_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Username Required", 'danger')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Password Required", 'danger')
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username or password", 'danger')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form I changed this from / to /login
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # When requested POST, enter username, password, and password confirmation
    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        bday = request.form.get("bday")

        if not username:
            flash("Username Required", 'danger')
            return render_template("register.html")
        elif not request.form.get("confirmation"):
            flash("Password Required", 'danger')
            return render_template("register.html")
        elif not request.form.get("confirmation"):
            flash("Passwords do not match", 'danger')
            return render_template("register.html")
        elif "@gmail.com" not in email:
            flash("Enter a valid email ending in @gmail.com", 'danger')
            return render_template("register.html")
        elif not bday:
            flash("Enter a valid birthday", 'danger')
            return render_template("register.html")

        # Check to see if the username already exists in the weebtube database
        check = db.execute("SELECT * FROM users WHERE username = ?", username)
        if str(username) in str(check):
            flash("Username already exists", 'warning')
            return render_template("register.html")
        # Check if the passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match", 'warning')
            return render_template("register.html")

        # Insert username and the hashed password into the database
        hash_password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash, pfp_url, email, bday, gender, bio) VALUES(?, ?, '', ?, ?, '', '')", username, hash_password, email, bday)

        # Go to the home page to log in
        return redirect("/")

    else:
        # When requested GET, display registration form
        return render_template("register.html")


@app.route("/new_password", methods=["GET", "POST"])
def new_password():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        # Query database for username
        if not username:
            flash("Username Required", 'danger')
            return render_template("new_password.html")

        rows = db.execute("SELECT username, hash FROM users WHERE username = ?", username)

        # Ensure username and old password exists
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            flash("Invalid username and/or password", 'danger')
            return render_template("new_password.html")

        # Check if the NEW passwords match
        if request.form.get("new_password") != request.form.get("confirm"):
            flash("New passwords do not match", 'warning')
            return render_template("new_password.html")

        # Update the hashed password in the database
        hash_password = generate_password_hash(request.form.get("new_password"))
        db.execute("UPDATE users SET hash = ? WHERE username = ?", hash_password, username)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking the Change Password button)
    else:
        return render_template("new_password.html")
