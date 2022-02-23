from user_wall_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

DB = 'user_wall'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-zA-Z])(?=.*[!#\$%&\?]).{8,24}$')  # password info pop up or explanation: Must be 8-24 characters long and contain: -1 upper case letter, -1 lower case letter, -1 number, -2 special characters (?!@$%&*-_)
FIRSTNAME_REGEX = re.compile(r'^[A-Za-z]+(((\'|\-|\ )?([A-Za-z])+))?$')
LASTNAME_REGEX = re.compile(r'^(\s)*[A-Za-z]+((\s)?((\'|\-|\.|\ )?([A-Za-z])*))*(\s)*$')
DATE_REGEX = re.compile(r'\d{4}-(02-(0[1-9]|[12][0-9])|(0[469]|11)-(0[1-9]|[12][0-9]|30)|(0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))$')  # Validates date format and days in month, does not validate leap year - February 29th match

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.username = data['username']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save(cls,data):
        query = "INSERT INTO users (first_name, last_name, email, username, password) VALUES (%(fname)s, %(lname)s, %(email)s, %(username)s, %(password)s);"
        return connectToMySQL(DB).query_db(query,data)

    @classmethod
    def show_all(cls):
        query = "SELECT * FROM users;"
        users_from_db = connectToMySQL(DB).query_db(query)
        all_users = []
        for user in users_from_db:
            all_users.append(cls(user))
        return all_users

    @classmethod
    def show(cls, data):
        query = "SELECT * FROM users WHERE users.id = %(id)s;"
        result = connectToMySQL(DB).query_db(query,data)
        user = cls(result[0])
        return user

    @classmethod
    def update(cls,data):
        query = "UPDATE users SET first_name=%(fname)s, last_name=%(lname)s, email=%(email)s, updated_at = NOW() WHERE users.id = %(id)s;"
        return connectToMySQL(DB).query_db(query,data)

    @classmethod
    def delete(cls,data):
        query = "DELETE FROM users WHERE users.id = %(id)s;"
        return connectToMySQL(DB).query_db(query,data)

    @classmethod
    def get_by_username(cls,data):
        query = "SELECT * FROM users WHERE users.username = %(username)s;"
        return connectToMySQL(DB).query_db(query,data)

    @staticmethod
    def validate_new_user(user):  # This is the registration validation mechanism.
        is_valid = True
        if len(user['fname']) < 3:
            flash("Your first name must be more than 3 characters long.", 'warning')  # This check meets the project parameters but leaves out a number of valid first names.
            is_valid = False
            print('first name failed')
        if not FIRSTNAME_REGEX.match(user['fname']):
            flash("Please only use valid alphabetic characters or the accepted special characters (-, ').", 'warning')
            is_valid = False
        else:
            print('first name passed')
        if len(user['lname']) < 3:
            flash("Your last name must be more than 3 characters long.", 'warning')  # This check meets the project parameters but leaves out a number of valid last names.
            is_valid = False
            print('last name failed')
        if not LASTNAME_REGEX.match(user['lname']):
            flash("Please only use valid alphabetic characters or the accepted special characters (-, ., ').", 'warning')
            is_valid = False
        else:
            print('last name passed')
        if not User.validate_email(user['email']):
            flash("The email address you entered does not appear to be valid.", 'warning')
            is_valid = False
        else:
            print('email is valid')
        if not User.validate_unique(user['email']):
            flash("That email was already in our database!", 'warning')
            is_valid = False
        else:
            print('email is unique')
        if len(user['username']) < 5:
            flash('Your username needs to be at least 5 characters long.', 'warning')
            is_valid = False
            print('that is too short')
        if not PASSWORD_REGEX.match(user['password']):
            flash('Your password must be 8-24 characters in length and contain 1 uppercase letter, 1 lower case letter, 1 number, and 1 special character (?, !, @, $, %, &, *, -, _).', 'warning')
            is_valid = False
            print('that password is weak')
        print(is_valid)
        return is_valid

    @staticmethod
    def validate_email(email):  # This function validates the email address against our regex check.
        isValid = True
        if not EMAIL_REGEX.match(email):
            isValid = False
        return isValid

    @staticmethod
    def validate_unique(email):
        isUnique = True
        users_list = User.show_all()
        for user in users_list:
            if email == user.email:
                isUnique = False
        return isUnique

class Message:
    def __init__(self,data):
        self.id = data['id']
        self.sender_id = data['sender_id']
        self.recipient_id = data['recipient_id']
        self.message = data['message']
        self.isNew = data['isNew']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_new(cls,id):
        data = {
            'id': id
        }
        query = "SELECT messages.id, messages.sender_id, message, messages.created_at, users.username AS author FROM messages LEFT JOIN users ON messages.sender_id = users.id WHERE recipient_id = %(id)s AND isNew = 1;"
        return connectToMySQL(DB).query_db(query,data)

    @classmethod
    def get_old(cls,data):
        query = "SELECT * FROM messages LEFT JOIN users ON %(id)s = messages.recipient_id WHERE messages.isNew = 0;"
        return connectToMySQL(DB).query_db(query,data)

    @classmethod
    def read(cls,data):
        message_id = {
            'id': data
        }
        query = "UPDATE messages SET isNew=0 WHERE messages.id = %(id)s;"
        return connectToMySQL(DB).query_db(query,message_id)

    @classmethod
    def delete_message(cls,data):
        message_id = {
            'id': data
        }
        query = "DELETE FROM messages WHERE messages.id = %(id)s;"
        return connectToMySQL(DB).query_db(query,message_id)

    @classmethod
    def create_message(cls,data):
        query = "INSERT INTO messages (sender_id, recipient_id, message, isNew) VALUES (%(sender_id)s, %(recipient_id)s, %(message)s, %(isNew)s);"
        return connectToMySQL(DB).query_db(query,data)


# bcrypt.generate_password_hash(password_string) <--- create hash
# bcrypt.check_password_hash(hashed_password, password_string) <--- compare hash to pwd