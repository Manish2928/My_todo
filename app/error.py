from flask import Blueprint, render_template
from jinja2 import TemplateNotFound

# Create a Blueprint for error handling
error = Blueprint('error', __name__)

# 404 - Not Found
@error.app_errorhandler(404)
def handle_404_error(e):
    return render_template('404.html', error=str(e)), 404

# 403 - Forbidden
@error.app_errorhandler(403)
def handle_403_error(e):
    return render_template('403.html', error=str(e)), 403

# 500 - Internal Server Error
@error.app_errorhandler(500)
def handle_500_error(e):
    return render_template('500.html', error=str(e)), 500

# 400 - Bad Request
@error.app_errorhandler(400)
def handle_400_error(e):
    return render_template('400.html', error=str(e)), 400

# Generic Exception Handler
@error.app_errorhandler(Exception)
def handle_generic_exception(e):
    return "    <h1>An Unexpected Error Occurred</h1> ", 500


@error.app_errorhandler(TemplateNotFound)
def handle_template_not_found(e):
    return render_template('template_error.html', error=str(e)), 500
