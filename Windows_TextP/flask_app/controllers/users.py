from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
import os
bcrypt = Bcrypt(app)
upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])

@app.route("/")
def index():
    if "user" in session:
        session["user"] = ""
    all_users = User.get_all()
    return render_template("index.html", all_users = all_users)


@app.route("/users/info:<int:id>")
def one_user(id):
    user = User.get_one(id)
    return render_template("one_user.html", user = user)

@app.route('/edit_users')
def edit_User():
    session['where'] = "edit_users"
    all_users = User.get_all()
    thisUser = User.get_one(session['user'])
    return render_template("edit_users.html", user = thisUser, all_users = all_users)

#UPDATE METHOD
@app.route('/update_user:<int:user_id>', methods = ["POST"])
def update_user(user_id):
    user = User.get_one(user_id)

    if session['user'] != user_id:
        flash("Not Your Account", "errors")
        return redirect('/home')

    if not bcrypt.check_password_hash(user['password'], request.form['old_password']):
        # if we get False after checking the password
        flash("Invalid Current Password", "errors")
        return redirect('/edit_users')

    if "is_admin" in request.form:
        adminTrue = True
    else:
        adminTrue = False

    data = { 
        "id": user_id,
        "username" : request.form["username"],
        "is_admin" : adminTrue,
        "password" : request.form["password"],
        "confirm"  : request.form["confirm"],
    }
    if request.files['profile_picture']:

        if user['profile_picture']:
            os.remove(os.path.join(upload_folder,user['profile_picture']))
        file = request.files['profile_picture']
        filename = user['username'] + file.filename
        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)

        data["profile_picture"]= filename
    else:
        data["profile_picture"] = user["profile_picture"]

    if not User.validate_update_form(data):
        return redirect('/edit_users')

    if request.form['password']:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        data["password"] = pw_hash
        data["confirm"] = "Sanitized"
    else:
        data["password"] = user['password']

    User.update(data)

    return redirect("/edit_users")



#DELETE METHOD
@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    users = User.get_all()
    user = User.get_one(user_id)
    other_admins = False
    for u in users:
        if u.is_admin == 1 and u.id != session['user']:
            other_admins = True
    if not other_admins:
        flash("There must always be 1 admin!", "errors")
        return redirect(f"/{session['where']}")
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