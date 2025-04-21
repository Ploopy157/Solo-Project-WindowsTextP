from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.user import User
from flask_app.models.file import File

@app.route('/home')
def home():
    if not "user" in session:
        return redirect("/")

    user = User.get_one(session["user"])
        
    return render_template("home.html", user = user)

#CREATE

@app.route("/create_file", methods=["POST"])
def create_file():
    if not File.validate_form(request.form):
        return redirect('/home')# redirect to the route where the user form is rendered.
    

    data = {
        "name" : request.form["name"],
        "file_type" :request.form["file_type"],
        "text" : request.form["text"],
        "user_id":session["user"]
    }
    if not File.check_name(data):
        new_file_id = File.save(data) #Called in a variable to capture ID
    else:
        flash("File already Exists with that Name!", "add_file")
    return redirect("/home")

#READ

@app.route("/files")
def view_file_list():
    if not "user" in session:
            return redirect("/")

    all_files = (File.get_all_files_with_user())


    return render_template("file_list.html", user = User.get_one(session["user"]), all_files = all_files)

@app.route("/files/<int:id>")
def view_file(id):
    if not "user" in session:
            return redirect("/")

    file = File.get_one(id)
    author = User.get_one(file["user_id"])

    return render_template("view_file.html", user = User.get_one(session["user"]), file = file, author = author)


#UPDATE
@app.route('/files/edit/<int:id>')
def edit_file(id):
    if not "user" in session:
        return redirect("/")

    if session["user"] == (File.get_one(id)["user_id"]):
        return render_template("edit_file.html", current_file = File.get_one(id), user = User.get_one(session["user"]))
    else:
        return redirect("/home")

@app.route("/update_file/<int:id>", methods=["POST"])
def update_file(id):
    if not File.validate_form(request.form):
        return redirect(f'/files/edit/{id}')# redirect to the route where the user form is rendered.

    data = {
        "id" : id,
        "name" : request.form["name"],
        "file_type" :request.form["file_type"],
        "text" : request.form["text"],
    }

    if File.check_name(data):
        if data['name'] != File.get_one(id)['name']: #You can Keep the Same name.
            flash("File already Exists with that Name!", "add_file")
            return redirect(f"/files/edit/{id}")

    else:
        new_file_id = File.update(data) #Called in a variable to capture ID
        
    
    return redirect("/home")

#DELETE
@app.route('/files/delete/<int:id>')
def delete_file(id):

    if session["user"] == (File.get_one(id)["user_id"]):
        File.delete(id)
    return redirect("/home")