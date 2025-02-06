from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import bcrypt
import bleach

app = Flask(__name__)
app.secret_key = "f$F9w@K^b7Zp8lm@JzUuD"

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=45)

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
    developer_name = db.Column("developer_name", db.String(200), nullable=False)

    def __repr__(self):
        return '<Entry %r>' % self.entrieid

def hash_password(password: str) -> str:
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')  

def check_password(stored_password: str, entered_password: str) -> bool:
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8'))




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
            hashed_password = hash_password(password)
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home")) 

    return render_template("signup.html")  # GET method to render the signup page


@app.route("/LOGIN.html", methods=["POST", "GET"])
def login():
    if "user_id" in session:  
        user = User.query.get(session["user_id"])  
        encrypted_email = caesar_encrypt(user.email, 3) 
        return redirect(url_for("user", usr=encrypted_email)) 

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password(user.password, password):  # Verify password hash
            encrypted_password = caesar_encrypt(password, 3)  
            encrypted_username = caesar_encrypt(email, 3) 
            session["user_id"] = user.id
            session.permanent = True
            return redirect(url_for("user", usr=encrypted_username))  
        else:
            flash("Invalid credentials, try again")  
            return redirect(url_for("login"))  

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
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        flash(f"You are logged in and viewing your account. {user.email}")  # Flash message for logged-in user
        encrypted_email = caesar_encrypt(user.email, 3)
        return render_template("account.html", email=encrypted_email)  # Render account page with the message
    else:
        flash("you are not logged in")
        return redirect(url_for("login"))  # Redirect to login if user is not logged in




@app.route("/logout.html")
def logout():
    session.clear()
    flash("you have been logged out")
    return redirect(url_for("login"))

@app.route("/DEVELOPER_DIARIES.html")
def diaries():
    entries = Entry.query.all()
    return render_template("DEVELOPER_DIARIES.html", entries=entries)

@app.route("/search.html", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("searched")
        search_by = request.form.get("search_by")

        if query:
            query = bleach.clean(query)  # Sanitize search input
            if search_by == "developer":
                results = Entry.query.filter(Entry.developer_name.contains(query)).all()
            elif search_by == "date":
                try:
                    date_query = datetime.strptime(query, "%Y-%m-%d")
                    results = Entry.query.filter(Entry.date_posted == date_query).all()
                except ValueError:
                    results = []
            else:
                results = Entry.query.filter(Entry.content.contains(query)).all()

            return render_template("search.html", query=query, results=results)

    return render_template("search.html", query=None)



@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        flash("You have to be logged in to post developer diaries")  
        return redirect(url_for("login"))  

    user = User.query.get(session["user_id"]) 
    if user:  
        code_content = request.form.get('code_entry') 
        note_content = request.form.get('note_entry') 
        
        # Sanitize the inputs to prevent XSS
        sanitized_code_content = bleach.clean(code_content)  # Sanitize code entry
        sanitized_note_content = bleach.clean(note_content)  # Sanitize note entry
        
        if sanitized_code_content and sanitized_note_content:
            # Create the new entry without checking for duplicates
            new_entry = Entry(
                content=f"Code:\n{sanitized_code_content}\n\nNotes:\n{sanitized_note_content}", 
                developer_name=user.email
            )
            db.session.add(new_entry)
            db.session.commit()  
            flash("Developer diary posted successfully!") 
        
        return redirect(url_for('diaries'))  
    else:
        flash("User not found")  
        return redirect(url_for('login'))


# Ensure database creation happens within the app context
if __name__ == "__main__":
    with app.app_context():  # Create an application context here
        db.create_all()  # Now it's safe to interact with the database
    app.run(debug=True)  # Run the app with debug mode enabled
