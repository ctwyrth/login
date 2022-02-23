from user_wall_app import app
from flask import render_template, redirect, request, session
from user_wall_app.models.user_wall import User, Message
from flask_bcrypt import Bcrypt
from flask import flash

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if session:
        for key in session:
            if key == 'isLoggedIn':
                if session['isLoggedIn'] == True:
                    return redirect('/welcome')
                else:
                    session.clear()
                    return redirect('/')
            else:
                continue
        return render_template('login.html')
    else:
        return render_template('login.html')  # this return may be extraneous but the process was erroring out otherwise.

@app.route('/register/user', methods=['POST'])
def register():
    if not User.validate_new_user(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])  # creates hashed pw
    print(pw_hash)
    data = {
        'fname': request.form['fname'],
        'lname': request.form['lname'],
        'email': request.form['email'],
        'username': request.form['username'],
        'password': pw_hash
    }
    user_id = User.save(data)  # returns new id from INSERT query
    session['isLoggedIn'] = True  # to pass information between pages
    session['isNew'] = True  # to allow specific welcome message
    session['user_id'] = user_id
    session['fname'] = data['fname']
    print('Logged in:', session['isLoggedIn'])
    return redirect('/')

@app.route('/login_check', methods=['POST'])
def check_login():
    username = {
        'username': request.form['username']
    }
    users_in_db = User.get_by_username(username)
    if not users_in_db:
        flash('No such user exists.', 'danger')
        return redirect('/')
    else:
        user_in_db = users_in_db[0]
        print(user_in_db)
    if not bcrypt.check_password_hash(user_in_db['password'], request.form['password']):
        flash('The password you entered does not match the username you provided.', 'danger')
        return redirect('/')
    session['isLoggedIn'] = True  # to pass information between pages
    session['isNew'] = False  # to allow specific welcome message
    session['user_id'] = user_in_db['id']
    session['fname'] = user_in_db['first_name']
    return redirect('/')

@app.route('/welcome')
def welcome():
    messages = Message.get_new(session['user_id'])
    if not messages:
        messages = {}
        messages_total = 0
    else:
        messages_total = len(messages)
    users = User.show_all()
    return render_template('/welcome.html', new_messages = messages, messages_total = messages_total, users = users)

@app.route('/send_mess', methods=['POST'])
def send_message():
    new_mess = {
        'sender_id': session['user_id'],
        'recipient_id': request.form['recipient_id'],
        'message': request.form['message'],
        'isNew': 1
    }
    Message.create_message(new_mess)
    return redirect('/welcome')

@app.route('/delete_mess/<id>')
def delete_message(id):
    Message.delete_message(id)
    return redirect('/welcome')

@app.route('/mark_read/<id>')
def mark_read(id):
    Message.read(id)
    return redirect('/')

@app.route('/show/<int:id>')
def show_record(id):
    data = {
        'id': id
    }
    return render_template("/details.html", user = User.show(data))

@app.route('/edit/<int:id>')
def edit(id):
    data = {
        'id': id
    }
    return render_template("edit.html", user = User.show(data))

@app.route('/update/<int:id>') 
def update(id):
    data = {
        'id': id,
        "xx":request.form['xx'],
    }
    User.update(data)
    return redirect(f"/show/{id}")

@app.route('/delete/<int:id>') 
def delete(id):
    data = {
        'id': id,
    }
    User.delete(data)
    return redirect('/show')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')