import re 

def error_for_category_title(title, categories):
    if any(category['title'] == title for category in categories):
        return "The title must be unique."
    elif not 1 <= len(title) <= 100:
        return "The title must be between 1 and 100 characters"
    else:
        return None

def error_for_contact(name):
    if not 1 <= len(name) <= 100:
        return "Name must be between 1 and 100 characters"
    elif not re.match("^[A-Za-z ]+$", name):
        return "Name must only contain alphabetic characters and spaces."
    
    return None

def find_contact_by_id(contact_id, contacts):
    return next((contact for contact in contacts if contact['id'] == contact_id), None)