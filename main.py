from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/LOGIN.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("LOGIN.html")

@app.route("/<usr>")
def user(usr):
    # Passing the username to a template or dynamically creating the response.
    return f"<h1>{usr}</h1>"  # Displays the username dynamically


@app.route("/index.html")
def homepage():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

