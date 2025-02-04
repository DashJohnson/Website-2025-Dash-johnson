from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "f$F9w@K^b7Zp8lm@JzUuD"


# Replace with your actual database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///newdatabase.db"  # Example for SQLite
db = SQLAlchemy(app)

class User(db.Model):  # Capitalize the class name as per Python conventions
    id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column("email", db.String(200), nullable=False, unique=True)
    password = db.Column("password", db.String(200), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.id


class Entry(db.Model):
    entrieid = db.Column("entrieid", db.Integer, primary_key=True)
    content = db.Column("content", db.String(500), nullable=False)
    date_posted = db.Column("date_posted", db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.entrieid

# Caesar cipher encryption and decryption functions
def caesar_encrypt(text, shift):
    encrypted_text = []
    for char in text:
        if char.isalpha():
            shifted = ord(char) + shift
            if char.islower():
                if shifted > ord('z'):
                    shifted -= 26
            elif char.isupper():
                if shifted > ord('Z'):
                    shifted -= 26
            encrypted_text.append(chr(shifted))
        else:
            encrypted_text.append(char)  # Non-alphabetic characters stay the same
    return ''.join(encrypted_text)

def caesar_decrypt(text, shift):
    decrypted_text = []
    for char in text:
        if char.isalpha():
            shifted = ord(char) - shift
            if char.islower():
                if shifted < ord('a'):
                    shifted += 26
            elif char.isupper():
                if shifted < ord('A'):
                    shifted += 26
            decrypted_text.append(chr(shifted))
        else:
            decrypted_text.append(char)  # Non-alphabetic characters stay the same
    return ''.join(decrypted_text)

@app.route("/")
def home():
    return render_template("index.html")





@app.route("/signup.html", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("email is already being used")
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home")) 

    return render_template("signup.html")  # GET method to render the signup page


@app.route("/LOGIN.html", methods=["POST", "GET"])
def login():
    if "user_id" in session:  # Check if the user is already logged in
        user = User.query.get(session["user_id"])  # Fetch the user from the database
        encrypted_email = caesar_encrypt(user.email, 3)  # Encrypt email
        return redirect(url_for("user", usr=encrypted_email))  # Redirect to user page with encrypted email

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            encrypted_password = caesar_encrypt(password, 3)  # Encrypt password if needed
            encrypted_username = caesar_encrypt(email, 3)  # Encrypt email
            session["user_id"] = user.id  # Store only user_id in session
            return redirect(url_for("user", usr=encrypted_username))  # Redirect to user page with encrypted email
        else:
            return "Invalid credentials, try again"
    return render_template("LOGIN.html")





@app.route("/<usr>")
def user(usr):
    if "user_id" in session:  # Check if the user_id exists in the session
        user = User.query.get(session["user_id"])  # Fetch the user from the database
        if user:
            decrypted_username = caesar_decrypt(usr, 3)  # Decrypt the username (email)
            return render_template("password.html", usr=decrypted_username)  # Show the decrypted email on the page
    return redirect(url_for("login"))  # Redirect to login if user is not logged in


@app.route("/index.html")
def homepage():
    return render_template("index.html")

@app.route("/account.html")
def account():
    return render_template("account.html")

@app.route("/logout.html")
def logout():
    flash("you have been logged out")
    session.clear()
    return redirect(url_for("login"))

@app.route("/DEVELOPER_DIARIES.html")
def diaries():
    entries = Entry.query.all()
    return render_template("DEVELOPER_DIARIES.html")

@app.route("/search.html", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("searched")  # Get the search query from the form
        search_by = request.form.get("search_by")  # Get which field to search by (developer, date, content)

        if query:
            if search_by == "developer":
                # Assuming "developer" is a field or related model, adapt to your schema
                results = Entry.query.filter(Entry.developer.contains(query)).all()  
            elif search_by == "date":
                # Assuming "date_posted" is a datetime field, adapt to format
                try:
                    date_query = datetime.strptime(query, "%Y-%m-%d")  # Date format: YYYY-MM-DD
                    results = Entry.query.filter(Entry.date_posted == date_query).all()
                except ValueError:
                    results = []  # If the date format is wrong, return no results
            else:
                # Default search by content
                results = Entry.query.filter(Entry.content.contains(query)).all()

            return render_template("search.html", query=query, results=results)

    return render_template("search.html", query=None)


@app.route("/submit", methods=["POST"])
def submit():
    entry_content = request.form.get('entry')
    if entry_content:
        new_entry = Entry(content=entry_content)
        db.session.add(new_entry)
        db.session.commit()
    return redirect(url_for('diaries'))

# Ensure database creation happens within the app context
if __name__ == "__main__":
    with app.app_context():  # Create an application context here
        db.create_all()  # Now it's safe to interact with the database
    app.run(debug=True)  # Run the app with debug mode enabled
