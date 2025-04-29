from flask_app.config.mysqlconnection import connect_to_mysql
from flask import flash
from flask_app.models import user

class File:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.file_type = data['file_type']
        self.text = data['text']
        self.is_shared = data['is_shared']
        self.user_id  = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        #Empty Dictionaries, Will be filled from DB when we need them
        self.user = None
#GET ALL
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM files;"
        results = connect_to_mysql('windows_textp_db').query_db(query)
        # "results" is an array of dictionaries.
        files = []
        for file in results:
            files.append(cls(file))
        return files

#GET ONE BY ID
    @classmethod
    def get_one(cls, id):
        query = """
                SELECT * FROM files 
                WHERE id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, {"id": id})
        # "results" is an array of dictionaries.
        if not results:
            return False
        file = results[0] 
        return file

#CREATE    
    @classmethod
    def save(cls, data):
        query = """INSERT INTO files (name, file_type, text, is_shared, user_id, created_at, updated_at) 
        VALUES (%(name)s, %(file_type)s, %(text)s, %(is_shared)s, %(user_id)s, NOW(), NOW());"""
        # insert call returns ID
        data_id = connect_to_mysql('windows_textp_db').query_db(query, data) 
        return data_id

#UPDATE
    @classmethod
    def update(cls, data):
        query = """
                UPDATE files
                SET name = %(name)s, file_type = %(file_type)s, text = %(text)s, is_shared = %(is_shared)s, updated_at = NOW()
                WHERE id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, data)
        return results

#DELETE
    @classmethod
    def delete(cls, id):
        query = """
                DELETE FROM files
                WHERE id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, {"id": id})
        return results

#GET File WITH USER
    @classmethod
    def get_all_files_with_user(cls):
        # Get all files, and their one associated User that created it
        query = "SELECT * FROM files JOIN users ON files.user_id = users.id WHERE is_shared = 1;"
        results = connect_to_mysql('windows_textp_db').query_db(query)
        all_files = []
        if results != False:
            for row in results:
                # Create a file class instance from the information from each db row
                one_file = cls(row)
                # Prepare to make a User class instance, looking at the class in models/user.py
                one_files_author_info = {
                    # Any fields that are used in BOTH tables will have their name changed, (id, created_at, updated_at)
                    # which depends on the order you put them in the JOIN query, use a print statement in your classmethod to show this.
                    "id": row['users.id'], 
                    "username": row['username'],
                    "is_admin": row['is_admin'],
                    "password": row['password'],
                    "created_at": row['users.created_at'],
                    "updated_at": row['users.updated_at'],
                    "profile_picture": row['profile_picture']
                }
                # Create the class instance
                author = user.User(one_files_author_info)
                # Associate thee class instances
                one_file.user = author
                all_files.append(one_file)
        return all_files

#GET Files from USER
    @classmethod
    def get_one_users_files(cls, data):
        # Get all files, and their one associated User that created it
        query = """SELECT * FROM files 
                    WHERE user_id = %(id)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, data)
        all_files = []
        if results:
            for row in results:
                # Create a file class instance from the information from each db row
                one_file = cls(row)
                all_files.append(one_file)
        return all_files

#GET Files from Name
    @classmethod
    def check_name(cls, data):
        # Get all files, and their one associated User that created it
        query = """SELECT * FROM files 
                    WHERE name = %(name)s
                    AND file_type = %(file_type)s;"""
        results = connect_to_mysql('windows_textp_db').query_db(query, data)
        all_files = []
        for row in results:
            # Create a file class instance from the information from each db row
            one_file = cls(row)
            all_files.append(one_file)
        
        if not all_files:
            exists = False
        else:
            exists = True
        return exists


#VALIDATION
    @staticmethod
    def validate_form(form):
        is_valid = True # we assume this is true

        if form['name']:
            if len(form['name']) < 3:
                flash("Name be at least 3 characters.", "add_file")
                is_valid = False
        else:
            flash("Name is Required!", "add_file")
            is_valid = False

        return is_valid