from flask import Flask, redirect, url_for, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Replace with your actual database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///newdatabase.db"  # Example for SQLite
db = SQLAlchemy(app)

class User(db.Model):  # Capitalize the class name as per Python conventions
    id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column("email", db.String(200), nullable=False, unique=True)
    password = db.Column("password", db.String(200), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.id

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



@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("searched")
    if query:
        return render_template("search.html", query=query)
    return render_template("search.html", query=None)

@app.route("/signup.html", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return "Email is already in use."
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home")) 

    return render_template("signup.html")  # GET method to render the signup page


@app.route("/LOGIN.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]  # Fix this to match form field
        password = request.form["password"]  # Ensure the form has a password field
        user = User.query.filter_by(email=email, password=password).first()  
        if user:
            encrypted_password = caesar_encrypt(password, 3)
            encrypted_username = caesar_encrypt(email, 3)
            session["user" = user]
            return redirect(url_for("user", usr=encrypted_username))  # Corrected line
        else:
            return "Invalid credentials, try again"  # More user-friendly response
    return render_template("LOGIN.html")  # This will render the login page when the method is GET




@app.route("/<usr>")
def user(usr):
    decrypted_username = caesar_decrypt(usr, 3)  # Decrypt the username
    return render_template("password.html", usr=decrypted_username)  # Show the password page

@app.route("/index.html")
def homepage():
    return render_template("index.html")

# Ensure database creation happens within the app context
if __name__ == "__main__":
    with app.app_context():  # Create an application context here
        db.create_all()  # Now it's safe to interact with the database
    app.run(debug=True)  # Run the app with debug mode enabled
