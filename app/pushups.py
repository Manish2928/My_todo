from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import datetime

pushups = Blueprint('pushups', __name__)
mysql = MySQL()

@pushups.route('/pushups', methods=['GET', 'POST'])
def pushups_home():

    # Check if users are logged in
    if 'user_id' not in session:
        flash('Please Login to access your Profile.')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Add new push-up entry
        pushup_count = request.form.get('pushup_count')
        comment = request.form.get('comment')

        cur = mysql.connection.cursor()
        cur.execute(
        "INSERT INTO pushups (pushup_count, comment, created_at, user_id) VALUES (%s, %s, %s, %s)",
        (pushup_count, comment, datetime.datetime.now(), session['user_id'])
        )

        mysql.connection.commit()
        cur.close()

        flash('Push-up log added successfully!', 'success')
        return redirect(url_for('pushups.pushups_home'))

    # Fetch all push-up records for the logged-in user
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, pushup_count, comment, created_at FROM pushups WHERE user_id = %s", 
        (session['user_id'],)
    )
    pushups_data = cur.fetchall()
    cur.close()

    return render_template('pushups.html', pushups=pushups_data)

@pushups.route('/pushups/delete/<int:id>', methods=['GET','POST'])
def delete_pushup(id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to delete your push-up log.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']  # Get the logged-in user's ID
    cur = mysql.connection.cursor()

    # Check if the push-up log exists and belongs to the logged-in user
    cur.execute("SELECT id FROM pushups WHERE id = %s AND user_id = %s", (id, user_id))
    pushup = cur.fetchone()

    if not pushup:
        flash('You are not authorized to delete this push-up log.', 'danger')
        return redirect(url_for('pushups.pushups_home'))

    # Delete the push-up log
    cur.execute("DELETE FROM pushups WHERE id = %s AND user_id = %s", (id, user_id))
    mysql.connection.commit()
    cur.close()

    flash('Push-up log deleted successfully!', 'success')
    return redirect(url_for('pushups.pushups_home'))


@pushups.route('/pushups/edit/<int:id>', methods=['GET', 'POST'])
def edit_pushup(id):
     # Check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to edit your push-up log.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']  # Get the logged-in user's ID

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Update the push-up log
        pushup_count = request.form.get('pushup_count')
        comment = request.form.get('comment')

        cur.execute(
            "UPDATE pushups SET pushup_count = %s, comment = %s WHERE id = %s AND user_id = %s",
            (pushup_count, comment, id,user_id)
        )
        mysql.connection.commit()
        cur.close()

        flash('Push-up log updated successfully!', 'success')
        return redirect(url_for('pushups.pushups_home'))

    # Fetch the push-up log to edit
    cur.execute(
        "SELECT id, pushup_count, comment FROM pushups WHERE id = %s AND user_id = %s", 
        (id, user_id))    
    
    pushup = cur.fetchone()
    cur.close()

    return render_template('edit_pushup.html', pushup=pushup)
