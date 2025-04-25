from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.user import User
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    if "user" in session:
        session["user"] = ""
    return render_template("index.html")


@app.route("/users/info:<int:id>")
def one_user(id):
    user = User.get_one(id)
    return render_template("one_user.html", user = user)

@app.route('/users/edit:<int:id>')
def update_User(id):
    user = User.get_one(id)
    return render_template("update_user.html", user = user)

#UPDATE METHOD
@app.route('/update_user:<int:user_id>', methods = ["POST"])
def update_user(user_id):
    User.update(request.form)
    return redirect(f'/users/info:{user_id}')

#DELETE METHOD
@app.route('/delete_user:<int:user_id>')
def delete_user(user_id):
    User.delete(user_id)
    return redirect("/")

#CREATE METHOD
@app.route('/register', methods=["POST"])
def create_user():

    # Weird stuff because checkboxes area a pain.
    if "is_admin" in request.form:
        adminTrue = True
    else:
        adminTrue = False

    data = { 
        "username" : request.form["username"],
        "is_admin" : adminTrue,
        "password" : request.form["password"],
        "confirm"  : request.form["confirm"]
    }
    if not User.validate_form(data):
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data["password"] = pw_hash
    data["confirm"] = "Sanitized"

    new_user_id = User.save(data) #Called in a variable to capture ID
    session["user"] = new_user_id
    return redirect("/home")

#Login Method
@app.route('/login', methods=["POST"])
def login():
    user_in_db = User.get_by_username(request.form["username"])
    # user is not registered in the db
    if not user_in_db:
        flash("Invalid Username/Password", "login")
        return redirect("/")
        
    if not bcrypt.check_password_hash(user_in_db.password, request.form['loginPassword']):
        # if we get False after checking the password
        flash("Invalid Username/Password", "login")
        return redirect('/')
    # if the passwords matched, we set the user_id into session
    session['user'] = user_in_db.id
    # never render on a post!!!
    return redirect("/home")

@app.route('/logout')
def log_out():
    session.clear()
    flash("Successfully Logged Out", "logout")
    return redirect("/")