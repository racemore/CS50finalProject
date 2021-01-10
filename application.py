# Expanded upon some code from WEEK 9 CS50 FINANCE

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, standard_date, html_datetime
from datetime import date, datetime
from pytz import timezone

from flask_mail import Mail, Message
from password_generator import PasswordGenerator

# Configure application
app = Flask(__name__)

# Configure gmail services ** FROM WEEK 9 NOTES **
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
mail = Mail(app)

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

# Configure WeebTube Library to use SQLite database
db = SQL("sqlite:///weebtube.db")

# Number of favorites a user can have
MAX_FAVORITES = 20

# List of genders a user can choose from
GENDERS = ['Male', 'Female', 'Non-Binary', 'Agender', 'Prefer not to say']

# Today's date
CURRENT_DATE = date.today()

# Source: https://stackoverflow.com/questions/11710469/how-to-get-python-to-display-current-time-eastern
EST_CURRENT_DATETIME = html_datetime(datetime.now(timezone('US/Eastern')))


@app.route("/remove-messages", methods=["GET", "POST"])
@login_required
def removeMessages():
    """Remove message sent to logged in user"""

    # User's id
    user_id = session.get("user_id")

    if request.method == "GET":

        return redirect("/inbox")

    if request.method == "POST":

        # Update database so that the deletion is reflected
        db.execute("UPDATE messages SET deleted_recipient = 1 WHERE id = ?", request.form.get("delete"))

        flash("Message deleted!", 'success')

        return redirect("/inbox")


@app.route("/sent-messages", methods=["GET", "POST"])
@login_required
def sentMessages():
    """Sent messages by logged in user"""

    # User's id
    user_id = session.get("user_id")

    if request.method == "GET":

        # Messages that user has sent + hasn't deleted
        messages = db.execute("""SELECT users.username, users.pfp_url, messages.message, messages.id, messages.subject, messages.date
                              FROM users JOIN messages ON users.id=messages.recipient
                              WHERE messages.sender=? AND messages.deleted_sender = 0 ORDER BY date DESC""", user_id)

        return render_template("sent_messages.html", messages=messages)

    if request.method == "POST":

        # Update database so that the deletion is reflected
        db.execute("UPDATE messages SET deleted_sender = 1 WHERE id = ?", request.form.get("delete"))

        flash("Message deleted!", 'success')

        return redirect("/sent-messages")


@app.route("/compose-message", methods=["GET", "POST"])
@login_required
def composeMessage():
    """Compose message"""

    # User's id
    user_id = session.get("user_id")

    if request.method == "GET":

        # Retrieve user's friends + information about each
        friends = db.execute("""SELECT id, username FROM users
                              WHERE id IN (SELECT friend_id FROM friends WHERE user_id = ? AND pending = 0)
                              ORDER BY LOWER(username) ASC""", user_id)

        return render_template("compose_message.html", friends=friends)

    if request.method == "POST":

        # ID of friend the user sent message to
        friend_id = request.form.get("friend")

        friend_info = db.execute("""SELECT username FROM users
                                 JOIN friends ON friends.friend_id = users.id
                                 WHERE friends.user_id=? AND friends.friend_id=? AND pending=0""",
                                 user_id, friend_id)

        # Check if valid friend (username) entered
        if not friend_info:
            flash("Please enter a valid friend", 'warning')
            return redirect("/compose-message")

        # Insert new message into database
        db.execute("""INSERT INTO messages (sender, recipient, subject, message)
                   VALUES(?, ?, ?, ?)""",
                   user_id, friend_id, request.form.get("subject"), request.form.get("msg"))

        flash("Sent message to " + friend_info[0]['username'] + "!", 'success')
        return redirect("/inbox")


@app.route("/inbox")
@login_required
def inbox():
    """User inbox"""

    # User's id
    user_id = session.get("user_id")

    # List of users who have requested to become friends
    friend_requests = db.execute("""SELECT users.username, users.pfp_url, users.id, friends.friend_date
                                 FROM users JOIN friends ON users.id = friends.user_id
                                 WHERE friends.friend_id = ? AND friends.pending = 1
                                 ORDER BY friends.friend_date DESC""", user_id)

    # List of pending watch party requests
    watch_party_requests = db.execute("""SELECT users.username, watchparty.host, watchparty.watching, watchparty.date_created, watchparty.message,
                                 watchparty.date, watchparty.time, users.pfp_url, watchparty.id
                                 FROM users JOIN participants ON users.id = participants.participant JOIN watchparty ON participants.party_id = watchparty.id
                                 WHERE participants.participant = ? AND participants.pending = 1
                                 ORDER BY watchparty.date_created DESC""", user_id)

    # Update information corresponding to each watch party
    for event in watch_party_requests:
        host_info = db.execute("SELECT username, pfp_url FROM users WHERE id = ?", event["host"])[0]
        event["date"] = standard_date(event["date"])
        event["host"] = host_info["username"]
        event["pfp_url"] = host_info["pfp_url"]

    # Messages to the user
    messages = db.execute("""SELECT users.username, users.pfp_url, messages.message, messages.id, messages.subject, messages.date
                              FROM users JOIN messages ON users.id=messages.sender
                              WHERE messages.recipient=? AND messages.deleted_recipient = 0 ORDER BY date DESC""", user_id)

    return render_template("inbox.html", friend_requests=friend_requests, watch_party_requests=watch_party_requests, messages=messages)


@app.route("/friend-requests", methods=["GET", "POST"])
@login_required
def friendRequests():
    """Answer friend requests"""

    # User's id
    user_id = session.get("user_id")
    if request.method == "GET":

        # User reached route via GET
        return redirect("/inbox#friend_req")

    if request.method == "POST":

        # Retrieve id of user who sent request
        requester_id = request.form.get("request")

        # Username of requester
        requester_name = db.execute("SELECT username FROM users WHERE id = ?", requester_id)[0]['username']

        # Check if user declined request; delete request from database
        if request.form.get("response") == "decline":
            db.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", requester_id, user_id)

            flash("Request declined", 'success')
            return redirect("/inbox")

        # Update database to reflect that the two users are now friends
        db.execute("UPDATE friends SET pending = 0, friend_date = ? WHERE user_id = ? AND friend_id = ?",
                   datetime.now(), requester_id, user_id)
        db.execute("INSERT INTO friends (user_id, friend_id, pending) VALUES(?, ?, 0)", user_id, requester_id)

        flash("You are now friends with " + requester_name + "!", 'success')
        return redirect("/inbox")


@app.route("/remove-friend", methods=["GET", "POST"])
@login_required
def removeFriend():
    """Remove friend"""

    # User ID
    user_id = session.get("user_id")

    if request.method == "GET":

        return redirect("/friends")

    if request.method == "POST":

        # ID/name of friend to remove
        friend_id = request.form.get("remove_friend")
        friend_name = db.execute("SELECT username FROM users WHERE id = ?", friend_id)[0]['username']

        # Delete corresponding entry from friends table
        db.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", user_id, friend_id)
        db.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", friend_id, user_id)

        flash("You are no longer friends with " + friend_name + "!", 'success')

        return redirect("/friends")


@app.route("/friends", methods=["GET", "POST"])
@login_required
def friends():
    """Display friend list and add friends"""

    user_id = session.get("user_id")
    if request.method == "GET":

        # List of friends
        friends = db.execute("""SELECT users.username, users.pfp_url, users.id, friends.friend_date
                             FROM users JOIN friends ON users.id = friends.user_id
                             WHERE friends.friend_id = ? AND friends.pending = 0
                             ORDER BY friends.friend_date DESC""", user_id)

        # Reformat Date
        for friend in friends:
            friend['friend_date'] = standard_date(friend['friend_date'].split(" ")[0])

        # Number of incoming friend requests
        requests = db.execute("SELECT COUNT(user_id) FROM friends WHERE friend_id = ? AND pending = 1",
                              user_id)[0]['COUNT(user_id)']

        return render_template("friends.html", friends=friends, requests=requests)

    if request.method == "POST":

        # List of friends
        friend = db.execute("SELECT id, username FROM users WHERE LOWER(username) = ?", request.form.get("friend").lower())

        # Alert if user input does not exist
        if not friend:
            flash("User does not exist", 'warning')
            return redirect("/friends")

        friend_id = friend[0]['id']

        # Alert if user input is the logged in user
        if user_id == friend_id:
            flash("Cannot add yourself", 'warning')
            return redirect("/friends")

        # Store info about input user if they have sent a request
        incoming_request = db.execute(
            "SELECT user_id, pending FROM friends WHERE user_id = ? AND friend_id = ?", friend_id, user_id)

        # Alert if user needs to respond to request from the input user
        if incoming_request and incoming_request[0]['pending']:
            flash("Respond to " + friend[0]['username'] + "'s friend request", 'warning')
            return redirect("/friend-requests")

        # Store info about input user if already a friend/sent a request already
        potential_friend = db.execute("SELECT pending FROM friends WHERE user_id = ? AND friend_id = ?", user_id, friend_id)

        # Alert if friends already or the user sent a request already and has not received a response
        if potential_friend:
            if potential_friend[0]['pending']:
                flash("Request to " + friend[0]['username'] + " still pending", 'warning')
                return redirect("/friends")
            flash("You are already friends with " + friend[0]['username'] + "!", 'warning')
            return redirect("/friends")

        # Add info about friend request into database
        db.execute("INSERT INTO friends (user_id, friend_id) VALUES(?, ?)", user_id, friend[0]['id'])

        flash("Friend request sent to " + friend[0]['username'] + "!", 'success')

        return redirect("/friends")


@app.route("/user-history")
@login_required
def userHistory():
    """Redirect to logged in user's rating history"""

    # Logged in user's username
    username = db.execute("SELECT username FROM users WHERE id=?", session.get("user_id"))[0]['username']

    # User-reached route via GET
    return redirect("/history/" + username)


@app.route("/history/<username>", methods=["GET", "POST"])
@login_required
def history(username):
    """Show history of user's ratings"""

    # ID of user logged in
    loggedInUser = session.get("user_id")

    if request.method == "GET":
        # Get list containing dict with user_id
        users_list = db.execute("SELECT id FROM users WHERE username=?", username)

        # Check if username in database. If not, return 404 error page
        if not users_list:
            return render_template("404.html")

        # Dict containing info about user
        user_info = users_list[0]

        # Store whether username belongs to the user logged in
        isLoggedInUser = False

        # Check if username belongs to user logged in
        if user_info['id'] == loggedInUser:
            isLoggedInUser = True

        user_id = user_info['id']

        show_history = db.execute(
            "SELECT anime.title, ratings.anime_id, ratings.rating, ratings.comment, ratings.time FROM ratings JOIN anime ON anime.id = ratings.anime_id WHERE user_id = ? ORDER BY time DESC", user_id)

        # User-reached route via GET
        return render_template("history.html", show_history=show_history, isLoggedInUser=isLoggedInUser, username=username)

    if request.method == "POST":

        anime_id = request.form.get("delete")

        # Delete entry in ratings corresponding to user_id and anime_id
        db.execute("DELETE FROM ratings WHERE user_id=? AND anime_id=?", loggedInUser, anime_id)

        # Update site-wide rating for title
        latest_rating = db.execute("SELECT ROUND(AVG(rating),2) FROM ratings WHERE anime_id=?", anime_id)
        db.execute("UPDATE anime SET rating = ? WHERE id=?", latest_rating[0]["ROUND(AVG(rating),2)"], anime_id)

        flash("Rating removed.", 'success')

        # User-reached route via POST
        return redirect("/history/" + username)


@app.route("/community")
@login_required
def community():
    """Show members of community"""

    # List of dicts containing info about each user
    users = db.execute("SELECT username, pfp_url, date_joined, substr(bio, 1, 200) AS bio FROM users ORDER BY LOWER(username)")

    # Change date to Month Day, Year format
    for user in users:
        user['date_joined'] = standard_date(user['date_joined'])

    # User-reached route via GET
    return render_template("community.html", users=users)


@app.route("/user-profile")
@login_required
def userProfile():
    """Redirect to logged in user's profile"""

    # Logged in user's username
    username = db.execute("SELECT username FROM users WHERE id=?", session.get("user_id"))[0]['username']

    # User-reached route via GET
    return redirect("/profile/" + username)


@app.route("/profile/<username>")
@login_required
def profile(username):
    """Show user's profile"""

    # Get list containing dict with user info
    users_list = db.execute(
        "SELECT id, username, bday, pfp_url, gender, bday, date_joined, bio FROM users WHERE username=?", username)

    # Check if username in database. If not, return 404 error page
    if not users_list:
        return render_template("404.html")

    # Dict containing info about user
    user_info = users_list[0]

    # Check if username belongs to user logged in
    if user_info['id'] == session.get("user_id"):
        isLoggedInUser = True
    else:
        isLoggedInUser = False

    user_id = user_info['id']

    # Alter dates so written Month Day, Year
    user_info['bday'] = standard_date(user_info['bday'])
    user_info['date_joined'] = standard_date(user_info['date_joined'])

    # List of dicts with information about 5 of user's favorite anime
    favorites = db.execute(
        "SELECT title, image_url FROM anime JOIN favorites ON anime.id=favorites.anime_id WHERE user_id=? ORDER BY rank LIMIT 5", user_id)

    # List of dicts with information about 3 most recent shows a user has rated
    show_history = db.execute(
        "SELECT anime.title, ratings.rating, ratings.comment, ratings.time FROM ratings JOIN anime ON anime.id = ratings.anime_id WHERE user_id = ? ORDER BY time DESC LIMIT 3", user_id)

    # User-reached route via GET
    return render_template("profile.html", user_info=user_info, favorites=favorites, isLoggedInUser=isLoggedInUser, show_history=show_history)


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def editProfile():
    """"Edit user's profile"""

    # ID of logged in user
    user_id = session.get("user_id")

    if request.method == "GET":

        # Info about user
        user_info = db.execute("SELECT username, date_joined, bday, pfp_url, gender, bio FROM users WHERE id = ?", user_id)[0]

        # User-reached route via GET
        return render_template("edit_profile.html", user_info=user_info, genders=GENDERS, current_date=CURRENT_DATE)

    if request.method == "POST":

        # Store info retrieved from form
        pfp_url = request.form.get("pfp")
        bio = request.form.get("bio")
        gender = request.form.get("gender")

        # Set bday to None if left empty by user
        birthday = request.form.get("birthday")
        bday = birthday if birthday != "" else None

        # Update user info in database based on form
        db.execute("UPDATE users SET pfp_url=?, bio=?, bday=?, gender=? WHERE id=?", pfp_url, bio, bday, gender, user_id)

        # User-reached route via POST
        return redirect("/user-profile")


@app.route("/user-favorites")
@login_required
def userFavorites():
    """Redirect to logged in user's favorites list"""

    # Logged in user's username
    username = db.execute("SELECT username FROM users WHERE id=?", session.get("user_id"))[0]['username']

    # User-reached route via GET
    return redirect("/favorites/" + username)


@app.route("/favorites/<username>")
@login_required
def favorites(username):
    """List of favorite anime of specified user"""

    # List containing dict with id corresponding to username
    users_list = db.execute("SELECT id FROM users WHERE username=?", username)

    # Check if username in database. If not, return 404 error page
    if not users_list:
        return render_template("404.html")

    # Dict containing id of user
    user_info = users_list[0]

    # Store whether username belongs to the user logged in
    isLoggedInUser = False

    # ID of user logged in
    loggedInUser = session.get("user_id")

    # Check if username belongs to user logged in
    if user_info['id'] == loggedInUser:
        isLoggedInUser = True

    user_id = user_info['id']

    # List of dicts containing information about each favorite anime
    favorites = db.execute(
        "SELECT title, image_url, season, episodes, genre FROM anime JOIN favorites ON anime.id=favorites.anime_id WHERE user_id=? ORDER BY rank", user_id)

    # User-reached route via GET
    return render_template("favorites.html", favorites=favorites, username=username, isLoggedInUser=isLoggedInUser)


# Source: Week 9 lecture
@app.route("/title-search")
@login_required
def titleSearch():
    """Search for anime titles"""

    query = "%" + request.args.get("q") + "%"
    anime = db.execute(
        "SELECT title, title_english FROM anime WHERE title LIKE ? OR title_english LIKE ? ORDER BY title LIMIT 15", query, query)
    return jsonify(anime)


# Source: Week 9 lecture
@app.route("/user-search")
@login_required
def userSearch():
    """Search for users"""

    users = db.execute("SELECT username FROM users WHERE username LIKE ? ORDER BY username LIMIT 10",
                       "%" + request.args.get("q") + "%")
    return jsonify(users)


@app.route("/add-favorites", methods=["GET", "POST"])
@login_required
def addFavorites():
    """Add anime to favorites list"""

    # ID of logged in user
    user_id = session.get("user_id")

    if request.method == "GET":

        # Retrieve the number of favorites a user has from database
        numFavorites = db.execute("SELECT MAX(rank) FROM favorites WHERE user_id=?", user_id)[0]['MAX(rank)']

        # User-reached route via GET
        return render_template("add_favorites.html", numFavorites=numFavorites, maxTitles=MAX_FAVORITES)

    if request.method == "POST":

        # Title entered by user in lowercase + remove english title if user used autocomplete
        title = request.form.get("favorite").lower().split(" (english: ")[0]

        # Retrieve list containing dict with info about anime matching title
        anime_list = db.execute(
            "SELECT id, title, title_english FROM anime WHERE LOWER(title)=? OR LOWER(title_english)=?", title, title)

        # Check if title in database; error alert if not
        if not anime_list:
            flash("Invalid title. Please try again.", 'warning')
            return redirect("/add-favorites")

        # Dict containing info about anime
        anime = anime_list[0]

        # Title of anime (English if possible; if not, romanized Japanese)
        title = anime['title_english'] if anime['title_english'] != "" else anime['title']

        # Check if title already in user's favorites list; error alert if already added
        if db.execute("SELECT anime_id FROM favorites WHERE anime_id=? AND user_id=?", anime['id'], user_id):
            flash("You already added " + title + "!", 'warning')
            return redirect("/add-favorites")

        # Alert user that title has been added to favorites
        flash("Added " + title + "!", 'success')

        # Insert info about anime into favorites table
        db.execute("INSERT INTO favorites (user_id, anime_id, rank) VALUES(?, ?, ?)",
                   user_id, anime['id'], request.form.get("rank"))

        # User-reached route via POST
        return redirect("/add-favorites")


@app.route("/remove-favorites", methods=["GET", "POST"])
@login_required
def removeFavorites():
    """"Remove anime from favorites list"""

    # ID of logged in user
    user_id = session.get("user_id")

    if request.method == "GET":

        # List of dicts containing info about each of user's favorite anime
        favorites = db.execute(
            "SELECT title, id FROM anime JOIN favorites ON anime.id=favorites.anime_id WHERE user_id=? ORDER BY rank", user_id)

        # User-reached route via GET
        return render_template("remove_favorites.html", favorites=favorites)

    if request.method == "POST":

        # ID of anime that user chose
        anime_id = request.form.get("id_remove")

        # Check if title selected; if not, error alert
        if anime_id is None:
            flash("Please select a title.", 'warning')
            return redirect("/remove-favorites")

        # Retrieve title corresponding to anime ID
        title = db.execute("SELECT title FROM anime WHERE id=?", anime_id)[0]['title']

        # Alert that anime removed from favorites
        flash("Removed " + title + "!", 'success')

        # Retrieve rank of anime to be removed
        rank = db.execute("SELECT rank FROM favorites WHERE user_id=? AND anime_id=?", user_id, anime_id)[0]['rank']

        # Delete entry in favorites corresponding to user_id and anime_id
        db.execute("DELETE FROM favorites WHERE user_id=? AND anime_id=?", user_id, request.form.get("id_remove"))

        # Update ranks of other favorites corresponding to the user_id in favorites table in database
        for i in range(rank, MAX_FAVORITES):
            db.execute("UPDATE favorites SET rank=? WHERE user_id=? AND rank=?", i, user_id, i + 1)

        # User-reached route via POST
        return redirect("/remove-favorites")


@app.route("/")
@login_required
def index():
    """Homepage with top 10"""

    shows = db.execute("SELECT title, image_url, genre, episodes, rating FROM anime ORDER BY rating DESC LIMIT 10")
    return render_template("top_ten.html", shows=shows)


@app.route("/rate", methods=["GET", "POST"])
@login_required
def rate():
    """Rate anime"""

    user_id = session.get("user_id")

    if request.method == "GET":

        return render_template("rate.html")

    # Check for invalid inputs
    user_rating = request.form.get("rate")
    if not user_rating.isdigit() or int(user_rating) < 0 or int(user_rating) > 10:
        flash("Invalid rating!", 'warning')
        return render_template("rate.html")

    # Title entered by user in lowercase + remove english title if user used autocomplete
    title = request.form.get("title").lower().split(" (english: ")[0]

    comment = request.form.get("comment")

    # check if title exists (case insensitive)
    check_title = db.execute("SELECT title, id FROM anime WHERE LOWER(title) = ? OR LOWER(title_english) = ?", title, title)
    if not check_title:
        flash("Invalid title. Please try again.", 'warning')
        return render_template("rate.html")

    title_id = check_title[0]["id"]

    # update user rating if already rated before
    rated = db.execute("SELECT rating FROM ratings WHERE anime_id = ? AND user_id=?", title_id, user_id)
    if not rated:
        db.execute("INSERT INTO ratings (user_id, anime_id, rating, comment) VALUES (?, ?, ?, ?)",
                   user_id, title_id, user_rating, comment)
    else:
        db.execute("UPDATE ratings SET rating=?, comment=?, time=CURRENT_TIMESTAMP WHERE anime_id=? AND user_id=?",
                   user_rating, comment, title_id, user_id)

    latest_rating = db.execute("SELECT ROUND(AVG(rating),2) FROM ratings WHERE anime_id=?", title_id)
    db.execute("UPDATE anime SET rating = ? WHERE id=?", latest_rating[0]["ROUND(AVG(rating),2)"], title_id)
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted; error alert if not
        if not request.form.get("username"):
            flash("Please enter a username", 'danger')
            return redirect("/login")

        # Ensure password was submitted; error alert if not
        elif not request.form.get("password"):
            flash("Please enter a password", 'danger')
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct; error alert if not
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get("password")):
            flash("Invalid username and/or password", 'danger')
            return redirect("/login")

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # Redirect user to home page
        return redirect("/")

    # User-reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Get info
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if username provided is alphanumeric
        if not username.isalnum():
            flash("Username must consist of alphanumeric characters.", 'danger')
            return redirect("/register")

        # Update taken based on whether username taken or not
        username_list = db.execute("SELECT username FROM users")
        taken = False
        for user in username_list:
            if user['username'] == username:
                taken = True
                break

        # Alert if no username provided or taken
        if not username or taken:
            flash("Username taken or left blank.", 'danger')
            return redirect("/register")

        # Alert if username over 20 characters
        if len(username) > 20:
            flash("Username cannot be over 20 characters.", 'danger')
            return redirect("/register")

        # Alert if password over 20 characters
        if len(password) > 20:
            flash("Password cannot be over 20 characters.", 'danger')
            return redirect("/register")

        # Alert if no password provided or password doesn't match confirmation
        if not password or password != confirmation:
            flash("Password left blank or passwords do not match.", 'danger')
            return redirect("/register")

        # Check if email address valid; alert if invalid
        emailAddress = email.split("@")

        if len(emailAddress) != 2 or not emailAddress[0].isalnum():
            flash("Enter a valid email address.", 'danger')
            return redirect("/register")

        emailDomain = emailAddress[1].split(".")

        if len(emailDomain) != 2 or not emailDomain[0].isalnum() or not emailDomain[1].isalnum():
            flash("Enter a valid email address.", 'danger')
            return redirect("/register")

        # Hash password
        pass_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Add username and password to database
        db.execute("INSERT INTO users (username, hash, email) VALUES(?, ?, ?)", username, pass_hash, email)

        # Alert user that they registered
        flash("Successfully registered!", 'success')

        # Redirect to login / User-reached route via POST
        return redirect("/login")

    # User-reached route via GET
    else:
        return render_template("register.html")


@app.route("/new-password", methods=["GET", "POST"])
def newPassword():
    """Change password"""

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


@app.route("/forgot-password", methods=["GET", "POST"])
def forgotPassword():
    """Request temp password if forgotten"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")

        # Query database for username
        if not username:
            flash("Username Required", 'danger')
            return render_template("forgot_password.html")

        user_info = db.execute("SELECT username, email FROM users WHERE username = ? AND email = ?", username, email)

        # Ensure account exists
        if not user_info:
            flash("Invalid username or email!", 'danger')
            return render_template("forgot_password.html")

        # create temporary password
        pwo = PasswordGenerator()

        # length of required password
        pwo.minlen = 6
        pwo.maxlen = 15

        # generate temporary password
        temp = pwo.generate()

        # Update the hashed password in the database
        hash_password = generate_password_hash(temp)
        db.execute("UPDATE users SET hash = ? WHERE username = ?", hash_password, username)

        flash("Temporary password sent. Please use it to change your password!", 'success')

        # send email notification with a temporary password (remains valid until the password is changed using the "Change Password" feature
        # or another "Forgot Password" POST request is made in which case a new email is sent with a new temp password)

        # to test this feature, you may create an account with a your own email or use the account information only used for this project

        # weebtube username: cs50user
        # email: cs50weebtubeuser@gmail.com
        # email password: weebtube#234

        msg = Message("Forgot Password - WeebTube", recipients=[email])
        msg.html = render_template("reset_password.html", username=username, temp=temp)
        mail.send(msg)

        # Redirect user to change password
        return redirect("/new-password")

    # User reached route via GET (as by clicking the Forgot Password button)
    else:
        return render_template("forgot_password.html")


@app.route("/create-watch-party", methods=["GET", "POST"])
@login_required
def createWatchParty():
    """Create new watch party"""

    # load friend list of the user
    user_id = session.get("user_id")
    friend_usernames = db.execute(
        "SELECT username, id FROM users WHERE id IN (SELECT friend_id FROM friends WHERE user_id = ? AND pending = 0) ORDER BY username ASC", user_id)

    if request.method == "POST":

        room_link = request.form.get("room-link")

        # warning if no friend is selected
        if not request.form.getlist("friend"):
            flash("Enter a friend's username!", 'warning')
            return redirect("/create-watch-party")

        # check if the user already added friend(s) for the same watch party
        # helpful source: https://stackoverflow.com/questions/13207697/how-to-remove-square-brackets-from-list-in-python
        friends = (", ".join(repr(e) for e in request.form.getlist("friend"))).replace("'", "")

        if not request.form.get("title"):
            flash("Add a title!", 'warning')
            return redirect("/create-watch-party")

        # Title entered by user in lowercase + remove english title if user used autocomplete
        title = request.form.get("title").lower().split(" (english: ")[0]

        # check if title exists (case insensitive)
        check_title = db.execute("SELECT title, id FROM anime WHERE LOWER(title) = ? OR LOWER(title_english) = ?", title, title)
        if not check_title:
            flash("Invalid title. Please try again.", 'warning')
            return redirect("/create-watch-party")

        # store the title as seen in the "title" column (not "title_english") of the anime table
        real_title = check_title[0]["title"]

        if "https://app.kosmi.io/room/" not in room_link:
            flash("Enter a valid link!", 'warning')
            return redirect("/create-watch-party")

        if not request.form.get("meeting-time"):
            flash("Fill out the event date & time!")
            return redirect("/create-watch-party")

        # check if the user is hosting another watch party at the same time
        # (if the user forgot to add a friend to the invite, they can delete their watch party and create a new one)
        date = request.form.get("meeting-time").split("T")[0]
        time = request.form.get("meeting-time").split("T")[1]

        alreadyHosting = db.execute(
            "SELECT date, time FROM watchparty WHERE date = ? AND time = ? AND host = ?", date, time, user_id)

        if alreadyHosting:
            flash("You are already hosting a watch party at this time!", 'warning')
            return redirect("/create-watch-party")

        message = request.form.get("message")
        if not message:
            message = "Hey! I'm planning on watching " + real_title + " on " + \
                standard_date(date) + " at " + time + " ET!\nHere's the link if you want to join: " + room_link

        if room_link not in message:
            flash("At a minimum, your message must include the kosmi room link!", 'warning')
            return redirect("/create-watch-party")

        db.execute("INSERT INTO watchparty (host, watching, message, date, time) VALUES (?, ?, ?, ?, ?)",
                   user_id, real_title, message, date, time)
        party_id = db.execute("SELECT id FROM watchparty WHERE host = ? AND date = ? AND time = ?", user_id, date, time)[0]["id"]

        # pending requests
        for friend in request.form.getlist("friend"):
            recipient = db.execute("SELECT id FROM users WHERE username = ?", friend)[0]["id"]
            db.execute("INSERT INTO participants (party_id, participant, pending) VALUES (?, ?, ?)", party_id, recipient, 1)

        # Alert user that invitation has been sent
        flash("Invitation sent! Recipients: " + friends, 'success')

        # User-reached route via POST
        return redirect("/watch-party")

    else:
        # Redirect user to home page
        return render_template("watchparty_request.html", friend_usernames=friend_usernames, current_date=EST_CURRENT_DATETIME)


@app.route("/watch-party-requests", methods=["GET", "POST"])
@login_required
def watchPartyRequests():
    """Display watch party requests in inbox"""
    # NOTE ABOUT PENDING VALUES: 0 = accepted, 1 = awaiting response, 2 = originally accepted but canceled, 3 = declined

    user_id = session["user_id"]
    if request.method == "GET":
        # User reached route via GET
        return redirect("/inbox#watch_party")
    else:
        # Retrieve the watch party id
        party_id = request.form.get("request")

        # Check if user declined request; change pending to 3 in the database
        if request.form.get("response") == "decline":
            db.execute("UPDATE participants SET pending = 3 WHERE participant = ? AND party_id = ?",
                       user_id, party_id)
            flash("Request declined", 'success')
            return redirect("/inbox")

        # Update database to reflect that the user is attending the watch party
        db.execute("UPDATE participants SET pending = 0 WHERE participant = ? AND party_id = ?",
                   user_id, party_id)

        flash("You are now attending the watch party!", 'success')
        return redirect("/inbox")


@app.route("/watch-party", methods=["GET", "POST"])
@login_required
def watchPartyRecords():
    """Display watch parties user is hosting and attending"""

    user_id = session["user_id"]

    date = EST_CURRENT_DATETIME.split("T")[0]

    # hosting table on the page will update when there is at least one participant that accepts the request
    hosting = db.execute("""SELECT watchparty.id, watchparty.watching, watchparty.host, watchparty.date, watchparty.time, watchparty.message, GROUP_CONCAT(participants.participant) participants
                        FROM watchparty JOIN participants ON watchparty.id=participants.party_id
                        WHERE watchparty.host = ? AND participants.pending = 0 AND DATE(watchparty.date,'+1 day') >= ?
                        GROUP BY watchparty.id""",
                         user_id, date)
    # pending table on the page will update when there is at least one participant that is still pending for a watch party
    allPending = db.execute("""SELECT watchparty.id, watchparty.watching, watchparty.host, watchparty.date, watchparty.time, GROUP_CONCAT(participants.participant) participants
                        FROM watchparty JOIN participants ON watchparty.id=participants.party_id
                        WHERE watchparty.host = ? AND participants.pending = 1 AND DATE(watchparty.date,'+1 day') >= ?
                        GROUP BY watchparty.id""",
                            user_id, date)

    # if null, unavailable participants table updates (all participants canceled or denied the watchparty)
    available = db.execute("""SELECT watchparty.id
                        FROM watchparty JOIN participants ON watchparty.id=participants.party_id
                        WHERE watchparty.host = ? AND (participants.pending = 1 OR participants.pending = 0) AND DATE(watchparty.date,'+1 day') >= ?
                        GROUP BY watchparty.id""",
                           user_id, date)

    if not available:
        noneAvailable = db.execute("""SELECT watchparty.id, watchparty.watching, watchparty.host, watchparty.date, watchparty.time
                                   FROM watchparty JOIN participants ON watchparty.id=participants.party_id
                                   WHERE watchparty.host = ? AND (participants.pending = 2 OR participants.pending = 3) AND DATE(watchparty.date,'+1 day') >= ?
                                   GROUP BY watchparty.id""",
                                   user_id, date)
    else:
        noneAvailable = None

    # Reformat date and add participant usernames for non-pending watch parties
    for event in hosting:
        event["date"] = standard_date(event["date"])
        participants = event["participants"].split(",")
        event["participants"] = ""
        for participant in participants:
            friend = db.execute("SELECT username FROM users WHERE id=?", int(participant.replace("'", "")))[0]["username"]
            event["participants"] = event["participants"] + [', ', ""][event["participants"] == ""] + friend

    # Reformat date and add participant usernames for pending
    for event in allPending:
        event["date"] = standard_date(event["date"])
        participants = event["participants"].split(",")
        event["participants"] = ""
        for participant in participants:
            friend = db.execute("SELECT username FROM users WHERE id=?", int(participant.replace("'", "")))[0]["username"]
            event["participants"] = event["participants"] + [', ', ""][event["participants"] == ""] + friend

    # participating table on the watch party main page will update with watch parties the user is attending
    joining = db.execute("""SELECT watchparty.id, watchparty.host, watchparty.host host_name, watchparty.host host_pfp, watchparty.watching, watchparty.date, watchparty.time, watchparty.message, participants.participant
                        FROM watchparty JOIN participants ON watchparty.id=participants.party_id
                        WHERE participants.participant = ? AND DATE(watchparty.date,'+1 day') >= ? AND pending = 0""",
                         user_id, date)

    # Reformat Date
    for event in joining:
        event["date"] = standard_date(event["date"]) + " at " + event["time"] + " ET"

        # change host info from number ids to text usernames + pfp_url
        host_info = db.execute("SELECT username, pfp_url FROM users WHERE id = ?", event["host"])[0]
        event["host_name"] = host_info["username"]
        event["host_pfp"] = host_info["pfp_url"]

    return render_template("watchparty_main.html", hosting=hosting, allPending=allPending, noneAvailable=noneAvailable, joining=joining, user_id=user_id)


@app.route("/watch-party-cancel", methods=["GET", "POST"])
@login_required
def cancel():
    """User can no longer attend the watch party"""
    # NOTE ABOUT PENDING VALUES: 0 = accepted, 1 = awaiting response, 2 = originally accepted but canceled, 3 = declined

    # User ID
    user_id = session["user_id"]

    # ID of the host and watch party
    host_id = int(request.form.get("remove_watchparty").split("X")[0])
    party_id = int(request.form.get("remove_watchparty").split("X")[1])

    # if the person who is canceling is the host, the watch party is deleted from the database
    if user_id is host_id:
        db.execute("DELETE FROM watchparty WHERE host=? AND id=?", user_id, party_id)
        db.execute("DELETE FROM participants WHERE party_id=?", party_id)
        flash("You canceled a watch party!", 'success')
    else:
        # if the person who is canceling is a participant, the participant's pending value changes to 2
        host = db.execute("SELECT username FROM users WHERE id=?", host_id)[0]["username"]
        db.execute("UPDATE participants SET pending = 2 WHERE participant=? AND party_id=?", user_id, party_id)

        flash("You are no longer attending " + host + "'s Watch Party!", 'success')
    return redirect("/watch-party")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    if e.code == 404:
        return render_template("404.html")
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)