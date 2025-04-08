from uuid import uuid4

class SessionPersistence:
    def __init__(self, session):
        self.session = session
        if 'categories' not in self.session:
            self.session['categories'] = []

    def get_all_categories(self):
        return self.session['categories']
    
    def find_category_by_id(self, category_id):
        found = (category for category in self.session['categories'] if category['id'] == category_id)
        return next(found, None)  
     
    def create_new_category(self, title):
        categories = self.get_all_categories()
        categories.append({
            'id': str(uuid4()),
            'title': title,
            'contacts': []
        })
    
    def create_new_contact(self, category_id, name, phone, email):
        selected_category = self.find_category_by_id(category_id)
        selected_category['contacts'].append({
            "id": str(uuid4()),
            "name": name,
            "phone": phone,
            "email": email
        })
        self.session.modified = True

    def update_category_by_id(self, category_id, new_title):
        category = self.find_category_by_id(category_id)
        if category:
            category['title'] = new_title
            self.session.modified = True

    def delete_category_by_id(self, category_id):
        self.session['categories'] = [category for category in self.session['categories']
                                      if category['id'] != category_id]
        self.session.modified = True
   
    def edit_contact(self, category_id, contact_id, name, phone, email):
        selected_category = self.find_category_by_id(category_id)
        
        for contact in selected_category['contacts']:
            if contact['id'] == contact_id:
                contact['name'] = name
                contact['phone'] = phone
                contact['email'] = email

        self.session.modified = True

    def delete_contact_from_category(self, category_id, contact_id):
        category = self.find_category_by_id(category_id)
        category['contacts'] = [contact for contact in category['contacts']
                                if contact['id'] != contact_id]
        
        self.session.modified = True

    def delete_all_contacts(self, category_id):
        category = self.find_category_by_id(category_id)
        category['contacts'] = []

        self.session.modified = True