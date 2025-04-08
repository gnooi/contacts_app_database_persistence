import secrets
from functools import wraps
import os
import json
import re


from flask import (Flask,
                   g, 
                   render_template,
                   url_for,
                   flash, 
                   redirect, 
                   request)

from contacts.utils import (
    error_for_category_title,
    error_for_contact,
    find_contact_by_id
)

from werkzeug.exceptions import NotFound

from contacts.database_persistence import DatabasePersistence

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

def require_category(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        category_id = kwargs.get('category_id')
        category = g.storage.find_category_by_id(category_id)
        if not category:
            raise NotFound(description="Category not found")
        return f(category=category, *args, **kwargs)

    return decorated_function

def require_contact(f):
    @wraps(f)
    @require_category
    def decorated_function(category, *args, **kwargs):
        contact_id = kwargs.get('contact_id')
        contact = find_contact_by_id(contact_id, category['contacts'])

        if not contact:
            raise NotFound(description="Contact not found")
        return f(category=category, contact=contact, *args, **kwargs)
    
    return decorated_function

@app.before_request
def load_db():
    g.storage = DatabasePersistence()

@app.route("/")
def index():
    return redirect(url_for('get_categories'))

@app.route("/categories")
def get_categories():
    categories = g.storage.get_all_categories()
    return render_template('categories.html', 
                           categories=categories)

@app.route("/categories", methods=["POST"])
def create_category():
    title = request.form["category_title"].strip()

    error = error_for_category_title(title, g.storage.get_all_categories())
    if error:
        flash(error, "error")
        return render_template('new_category.html', title=title)

    g.storage.create_new_category(title)
    flash("The category has been created.", "success")
    return redirect(url_for('get_categories'))

@app.route("/categories/new")
def add_new_category():
    return render_template("new_category.html")

@app.route("/categories/<int:category_id>")
@require_category
def show_category(category, category_id):
    return render_template('category.html', category=category)

@app.route("/categories/<int:category_id>/contacts", methods=["POST"])
@require_category
def create_contact(category, category_id):
    name = request.form["name"].strip()
    phone = request.form["phone"].strip()
    email = request.form["email"].strip()

    error = error_for_contact(name)

    if error:
        flash(error, "error")
        return render_template('category.html', category=category, category_id=category_id)
    
    g.storage.create_new_contact(category_id, name, phone, email)
    flash("The contact was added.", "success")
    return redirect(url_for('show_category', category_id=category_id))


@app.route("/categories/<int:category_id>/edit", methods=["POST"])
@require_category
def edit_category(category, category_id):
    return render_template('edit_category.html', category=category)

@app.route("/categories/<int:category_id>", methods=["POST"])
@require_category
def update_category(category, category_id):
    title = request.form["category_title"].strip()

    error = error_for_category_title(title, g.storage.get_all_categories())
    if error:
        flash(error, "error")
        return render_template('edit_category.html', 
                               category=category,
                               title=title)
    
    g.storage.update_category_by_id(category_id, title)
    flash("The category has been updated.", "success")
    return redirect(url_for('show_category', category_id=category_id)) 

@app.route("/categories/<int:category_id>/contacts/<int:contact_id>/info", methods=["GET"])
@require_contact
def contact_info(category, contact, category_id, contact_id):
    return render_template('contact_info.html',
                           category=category,
                           contact=contact)

@app.route("/categories/<int:category_id>/contacts/<int:contact_id>/edit", methods=["POST"])
@require_contact
def edit_contact(category, contact, category_id, contact_id):
    return render_template('edit_contact.html',
                           category=category,
                           contact=contact)

@app.route("/categories/<int:category_id>/contacts/<int:contact_id>", methods=["POST"])
@require_contact
def update_contact(category, contact, category_id, contact_id):
    name = request.form["name"].strip()
    phone = request.form["phone"].strip()
    email = request.form["email"].strip()

    error = error_for_contact(name)

    if error:
        flash(error, "error")
        return render_template('edit_contact.html', 
                               category=category,
                               contact=contact,
                               name=name, 
                               phone=phone,
                               email=email)
    
    g.storage.edit_contact(category_id, contact_id, name, phone, email)
    flash("The contact was edited.", "success")
    return redirect(url_for('show_category', category_id=category_id))

@app.route("/categories/<int:category_id>/delete", methods=["POST"])
@require_category
def delete_category(category, category_id):
    g.storage.delete_category_by_id(category_id)
    flash("The category has been deleted.", "success")
    return redirect(url_for('get_categories'))

@app.route("/categories/<int:category_id>/contacts/delete", methods=["POST"])
@require_category
def delete_all_contacts(category, category_id):
    g.storage.delete_all_contacts(category_id)
    flash("All contacts have been deleted.", "success")
    return redirect(url_for('show_category', category_id=category_id))

@app.route("/categories/<int:category_id>/contacts/<int:contact_id>/delete", methods=["POST"])
@require_contact
def delete_contact(category, contact, category_id, contact_id):
    g.storage.delete_contact_from_category(category_id, contact_id)
    flash("The contact has been deleted.", "success")
    return redirect(url_for('show_category', category_id=category_id))

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)