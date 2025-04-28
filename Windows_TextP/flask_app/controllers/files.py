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

@app.route("/add_file", methods=["POST"])
def create_file():
    #NO VALIDATIONS ON CREATE
    # if not File.validate_form(request.form):
    #     return redirect('/home')# redirect to the route where the user form is rendered.
    if "is_shared" in request.form:
        shared = True
    else:
        shared = False
    data = {
        "name" : "New File",
        "file_type" :request.form["file_type"],
        "text" : "",
        "is_shared": shared,
        "user_id":session["user"]
    }
    original_name = data["name"]
    i = 0
    while File.check_name(data):
        i = i+1
        data['name'] = (f"{original_name}({i})")

    new_file_id = File.save(data) #Called in a variable to capture ID
    return redirect(f"{request.form["where"]}")

#READ

@app.route("/shared_files")
def view_file_list():
    if not "user" in session:
        return redirect("/")

    all_files = (File.get_all_files_with_user())
    session["where"] = "shared_files"


    return render_template("file_list.html", user = User.get_one(session["user"]), all_files = all_files, where = session["where"])

@app.route("/my_files")
def view_my_files():
    if not "user" in session:
        return redirect("/")

    all_files = (File.get_one_users_files({"id":session["user"]}))
    session["where"] = "my_files"

    return render_template("file_list.html", user = User.get_one(session["user"]), all_files = all_files, where = session["where"])

#READ
@app.route("/files/<int:id>/properties")
def file_properties(id):
    if not "user" in session:
        return redirect("/")
    file = File.get_one(id)
    author = User.get_one(file["user_id"])
    
    return render_template("file_properties.html", user = User.get_one(session["user"]), file = file, author = author, where = session["where"])


#One File (READ + UPDATE FORM)
@app.route("/files/<int:id>")
def view_file(id):
    if not "user" in session:
        return redirect("/")

    file = File.get_one(id)
    author = User.get_one(file["user_id"])

    return render_template("one_file.html", current_file = File.get_one(id), user = User.get_one(session["user"]), file = file, author = author, where = session["where"])

#UPDATE
@app.route("/update_file/<int:id>", methods=["POST"])
def update_file(id):
    if int(session["user"]) != int(File.get_one(id)["user_id"]) and not User.get_one(session['user'])["is_admin"]:
        flash("Access is denied!", "errors")
        return redirect(f"/{session['where']}")


    if not File.validate_form(request.form):
        return redirect(f'/files/edit/{id}')# redirect to the route where the user form is rendered.

    if "is_shared" in request.form:
        shared = True
    else:
        shared = False

    if File.get_one(id)["file_type"] == "pdf":
        data = {
            "id" : id,
            "name" : request.form["name"],
            "file_type" :request.form["file_type"],
            "is_shared" : shared,
            "text" : File.get_one(id)["text"],
        }
    else:
        data = {
            "id" : id,
            "name" : request.form["name"],
            "file_type" :request.form["file_type"],
            "is_shared" : shared,
            "text" : request.form["text"],
        }

    if File.check_name(data):
        if data['name'] != File.get_one(id)['name']: #You can Keep the Same name.
            flash("File already Exists with that Name!", "add_file")
            return redirect(f"/files/edit/{id}")

    new_file_id = File.update(data) #Called in a variable to capture ID
    return redirect(f"/{session['where']}")

#DELETE
@app.route('/files/delete/<int:id>')
def delete_file(id):

    if session["user"] == (File.get_one(id)["user_id"]) or User.get_one(session['user'])["is_admin"]:
        File.delete(id)
        
    else: flash("Access is denied!", "errors")
    return redirect(f"/{session['where']}")