# TO DO: finish up setting up the loan html, like, add more functions to it so it's more functional.
# Finish up the HTMLs and the CSS stuff, navigation bars inbetween the logged in routes: credit, loan, budget etc.
# make sure to not delete any of the JS that I set up in the login and register htmls, as well as the log-out functions.

# Any questions regarding templating stuff: 
# https://jinja.palletsprojects.com/en/3.0.x/templates/#tests
# https://www.geeksforgeeks.org/getting-started-with-jinja-template/
# https://www.geeksforgeeks.org/templating-with-jinja2-in-flask/
# {{ }} for expressions.
# {# #} for comments (even multiline) inside the template.
# {% %} for jinja statements (like loops, etc.)
# I encourage you guys to learn templating as it's a great skill! 

# If you want to look into the database, download SQLite, great program to prototype websites that use databases
# https://www.sqlite.org/index.html

# If you guys just want to test out things inside some of the menus you can either load up the HTML by itself without hosting
# or access the account listed below:
# login:    alex
# password: alex
# You might notice that the passwords look all weird in the SQLite file, that's because of bcrypt.

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "123"

# Database Connection Function
def db_connect():
    db = sqlite3.connect("expenses.sqlite")
    db.row_factory = sqlite3.Row
    return db

@app.route("/")
def root():
    return redirect(url_for("signup"))  # Directs to signup page

@app.route("/signup", methods=["GET", "POST"])
def signup():
    errors = []
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")
        confirmpwd = request.form["password2"].encode("utf-8")

        conn = db_connect()
        cur = conn.cursor()

        if password != confirmpwd:
            errors.append("Passwords do not match")

        check_user = cur.execute("SELECT username FROM people WHERE username = ?", (username,)).fetchone()
        if check_user:
            errors.append("That username is already taken! Pick another one.")

        if errors:
            return render_template("signup.html", errors=errors)

        hashed_pwd = bcrypt.hashpw(password, bcrypt.gensalt())
        cur.execute(
            "INSERT INTO people (username, password, budget, credit, loans) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_pwd, 1000, 0, 0),
        )

        conn.commit()
        conn.close()
        
        return redirect(url_for("login"))  # Redirect to login after signup

    return render_template("signup.html", errors=errors)

@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []

    if request.method == "POST":
        username = request.form["user"]
        password = request.form["password"].encode("utf-8")

        conn = db_connect()
        cur = conn.cursor()
        user_data = cur.execute("SELECT username, password FROM people WHERE username = ?", (username,)).fetchone()

        if not user_data:
            errors.append("That username does not exist!")
            return render_template("login.html", errors=errors)

        db_username, db_password = user_data

        if isinstance(db_password, str):
            db_password = db_password.encode("utf-8")

        if not bcrypt.checkpw(password, db_password):
            errors.append("Incorrect password!")
            return render_template("login.html", errors=errors)

        session["user"] = db_username
        return redirect(url_for("home"))  # Redirect to home page after login

    return render_template("login.html", errors=errors)

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

# ✅ Logout Route
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
