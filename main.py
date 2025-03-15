from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "123"

# Database Connection Function
def db_connect():
    db = sqlite3.connect("expenses.sqlite")
    db.row_factory = sqlite3.Row
    return db

# ✅ Create Blog Table if not exists
def create_blog_table():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date_posted TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Call function to ensure table exists
create_blog_table()

# ✅ Function to Format Date
def format_date(timestamp):
    """Convert timestamp to 'Feb 15th, 2025' format."""
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    day_suffix = lambda d: "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return dt.strftime(f"%b {dt.day}{day_suffix(dt.day)}, %Y")

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

# ✅ Blog - View All Posts
@app.route("/blog")
def blog():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM blog_posts ORDER BY date_posted DESC")
    posts = cur.fetchall()
    conn.close()
    return render_template("blog.html", posts=posts, format_date=format_date)

# ✅ Blog - View a Single Post
@app.route("/post/<int:post_id>")
def post(post_id):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,))
    post = cur.fetchone()
    conn.close()
    
    if not post:
        return "Post Not Found", 404
    
    return render_template("post.html", post=post, format_date=format_date)

# ✅ Blog - Create a New Post
@app.route("/create_blog", methods=["GET", "POST"])
def create_blog():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        date_posted = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO blog_posts (title, content, date_posted) VALUES (?, ?, ?)", 
                    (title, content, date_posted))
        conn.commit()
        conn.close()
        return redirect(url_for("blog"))

    return render_template("create_blog.html")

if __name__ == "__main__":
    app.run(debug=True)
