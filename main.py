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
    return redirect(url_for("login"))  # Directs to login page

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

@app.route("/contact")
def contact():
    return render_template("contact.html")

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
