# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connect_to_mysql
from flask import flash
#only needed for Email Validation
import re
PASSWORD_REQUIREMENT = re.compile(r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$')

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.username = data['username']
        self.is_admin = data['is_admin']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        self.profile_picture = None

#GET ALL
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connect_to_mysql('windows_textp_db').query_db(query)
        # "results" is an array of dictionaries.
        users = []
        for user in results:
            users.append(cls(user))
        return users

#GET ONE
    @classmethod
    def get_one(cls, id):
        query = """
                SELECT * FROM users 
                WHERE id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, {"id": id})
        # "results" is an array of dictionaries.
        if not results:
            return False
        user = results[0] 
        return user

#GET User by Email
    @classmethod
    def get_by_username(cls, username):
        query = "SELECT * FROM users WHERE username = %(username)s;"
        print(query)
        result = connect_to_mysql('windows_textp_db').query_db(query, {"username": username})
        if len(result) < 1:
            return False
        return cls(result[0])

#CREATE    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (username, is_admin, password, created_at, updated_at) VALUES (%(username)s, %(is_admin)s, %(password)s, NOW(), NOW());"
        # insert call returns ID
        data_id = connect_to_mysql('windows_textp_db').query_db(query, data) 
        return data_id

#UPDATE
    @classmethod
    def update(cls, data):
        query = """
                UPDATE users
                SET user = %(username)s, is_admin = %(is_admin)s, password = %(password)s, updated_at = NOW()
                WHERE id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, data)
        return results
#DELETE
    @classmethod
    def delete(cls, id):
        query = """
                DELETE FROM users
                WHERE id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, {"id": id})
        return results
#VALIDATION
    @staticmethod
    def validate_form(form):
        is_valid = True # we assume this is true

        if len(form['username']) < 2:
            flash("Username must be at least 2 characters!", "register")
            is_valid = False
            if not str.isalpha(form['username']):
                flash("Username must contain only Letters!", "register")
                isvalid = False
                if User.get_by_username(form['username']):
                    flash("Somebody already used this name!", "register")
                    is_valid = False
                

        if len(form['password']) < 8:
            flash("Password must be at least 8 characters!", "register")
            is_valid = False
        
        if not PASSWORD_REQUIREMENT.match(form['password']):
            flash("Password must include at least one number and one special character!", "register")

        if form['confirm'] != form["password"]:
            flash("Password and Confirm Password must match!", "register")
            is_valid = False

        if User.get_all() == False:
            if form['is_admin'] == False:
                print("FIRST USER MUST BE ADMIN")
                flash("The first user must be an admin!", "register")
                is_valid = False
                



        #Check if User is first/last and make sure they are an admin.

        return is_valid
