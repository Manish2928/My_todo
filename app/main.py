from flask import Blueprint, render_template, url_for,session,flash, redirect

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')




@main.route('/profile')
def profile():
    # Check if users are logged in
    if 'user_id' not in session:
        flash('Please Login to access your Profile.')
        return redirect(url_for('auth.login'))
    
    # Pass session data to the template
    return render_template('profile.html', user_name=session.get('user_name'))



