from flask import Blueprint, render_template, redirect , url_for , request,flash,session,make_response
from werkzeug.security import generate_password_hash, check_password_hash
import secrets  # For generating secure tokens
from flask import g  # For storing user info globally during the request            
from . import mysql


auth = Blueprint('auth', __name__)

@auth.before_app_request
def auto_login():
    if 'user_id' not in session:
        remember_token = request.cookies.get('remember_token')
        if remember_token:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, email, name FROM users WHERE remember_token = %s", (remember_token,))
            user = cur.fetchone()
            cur.close()

            if user:
                stored_token = user[4]  # The hashed remember_token column from the database

                # Use `check_password_hash` to compare the hashed token with the provided token
                if check_password_hash(stored_token, remember_token):
                    # Log in the user automatically
                    session['user_id'] = user[0]
                    session['email'] = user[1]
                    session['user_name'] = user[2]


# for the login
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_form():
    email = request.form.get('log-email').lower()  # Normalize email to lowercase
    password = request.form.get('log-Password')
    remember = True if request.form.get('remembareme') else False

    # Check if the user exists in the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if not user:
        flash('Invalid email or password. Please try again.')
        return render_template('login.html')

    # Assuming `user[3]` is the hashed password column
    stored_password = user[3]  # Adjust index as needed
    
   

    if not check_password_hash(stored_password, password):
        flash('Invalid email or password. Please try again.')
        return render_template('login.html')
    
   # Store user information in the session
    session['user_id'] = user[0]  # Store user ID (adjust index as needed)
    session['email'] = user[1]  # Store email (adjust index as needed)
    session['user_name'] = user[2]  # Store user name (adjust index as needed)

    # Handle "Remember Me"
    response = make_response(redirect(url_for('main.profile')))  # Default response

    if remember:
        # Generate a secure token for "Remember Me"
        remember_token = secrets.token_hex(16)
        hashed_token = generate_password_hash(remember_token)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET remember_token = %s WHERE id = %s", (hashed_token, user[0]))
        mysql.connection.commit()
        cur.close()

        # Set a persistent cookie for the token
        response = make_response(redirect(url_for('main.profile')))
        response.set_cookie('remember_token', remember_token, max_age=7 * 24 * 60 * 60, httponly=True, secure=True)
        return response

    # Redirect to the profile page on successful login
    flash('Logged in successfully!')
    return redirect(url_for('main.profile'))  # Replace `main.profile` with your actual route


@auth.route('/logout')
def logout():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        # Clear the remember token in the database
        cur.execute("UPDATE users SET remember_token = NULL WHERE id = %s", (session['user_id'],))
        mysql.connection.commit()
        cur.close()

    session.clear()  # Clear all session data
    response = make_response(redirect(url_for('auth.login')))
    response.set_cookie('remember_token', '', expires=0)  # Delete the cookie
    flash('You have been logged out.')
    return response


# for the singup 
@auth.route('/singup')
def singup():
    return render_template('singup.html')

@auth.route('/singup', methods=['POST'])
def singup_post():
    Email = request.form.get('email')
    Name = request.form.get('name')
    password = request.form.get('password')

   # Check if the user already exists
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (Email,))
    existing_user = cur.fetchone()

    if existing_user:
        flash('User already exists. Please try again.')
        return redirect(url_for('auth.singup'))

    # If user does not exist, create a new user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    cur.execute("INSERT INTO users (email, name, password) VALUES (%s, %s, %s)", (Email.lower(), Name, hashed_password))
    mysql.connection.commit()
    cur.close()




    return redirect(url_for('auth.login'))

