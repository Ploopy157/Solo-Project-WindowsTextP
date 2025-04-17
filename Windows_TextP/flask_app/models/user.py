# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connect_to_mysql
from flask import flash
#only needed for Email Validation
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
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
            return false
        user = results[0] 
        return user

#GET User by Email
    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        print(query)
        result = connect_to_mysql('windows_textp_db').query_db(query, {"email": email})
        if len(result) < 1:
            return False
        return cls(result[0])

#CREATE    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (first_name, is_shared, password, created_at, updated_at) VALUES (%(first_name)s, %(is_shared)s, %(email)s, %(password)s, NOW(), NOW());"
        # insert call returns ID
        data_id = connect_to_mysql('windows_textp_db').query_db(query, data) 
        return data_id

#UPDATE
    @classmethod
    def update(cls, data):
        query = """
                UPDATE users
                SET first_name = %(first_name)s, is_shared = %(is_shared)s, password = %(password)s, updated_at = NOW()
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
            flash("First name must be at least 2 characters.", "register")
            is_valid = False
            if not str.isalpha(form['first_name']):
                flash("First Name must contain only Letters.", "register")
                isvalid = False
                

        if len(form['password']) < 8:
            flash("Password must be at least 8 characters.", "register")
            is_valid = False

        if form['confirm'] != form["password"]:
            flash("Password and Confirm Password must match.", "register")
            is_valid = False


        #Check if User is first/last and make sure they are an admin.

        return is_valid
