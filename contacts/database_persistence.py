from contextlib import contextmanager

import logging
import psycopg2
from psycopg2.extras import DictCursor

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger =logging.getLogger(__name__)

class DatabasePersistence:
    def __init__(self):
        self._setup_schema()

    def _setup_schema(self):
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT (*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' and table_name = 'categories';
                    """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE categories (
                            id serial PRIMARY KEY,
                            title text NOT NULL UNIQUE);
                    """)
                    cursor.execute("""
                        SELECT COUNT (*)
                        FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'contacts';
                    """)
                    if cursor.fetchone()[0] == 0:
                        cursor.execute(""""
                            CREATE TABLE contacts (
                                id serial PRIMARY KEY,
                                name text NOT NULL,
                                phone varchar(15),
                                email text,
                                category_id integer NOT NULL REFERENCES categories (id) ON DELETE CASCADE
                            );
                        """)
    @contextmanager
    def _database_connect(self):
        connection = psycopg2.connect(dbname='contacts')
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def get_all_categories(self):
        query = "SELECT * FROM categories"
        logger.info("Executing query: %s", query)
        with self._database_connect() as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

        categories = [dict(result) for result in results]
        for category in categories:
            contacts = self._find_contacts_for_category(category['id'])
            category.setdefault('contacts', contacts)

        return categories
    
    def find_category_by_id(self, category_id):
        query = "SELECT * FROM categories WHERE id = %s"
        logger.info("Executing query: %s with category_id: %s", 
                    query, category_id)
        with self._database_connect() as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (category_id, ))
                category = dict(cursor.fetchone())

        contacts = self._find_contacts_for_category(category_id)
        category.setdefault('contacts', contacts)
        return category
    
    def _find_contacts_for_category(self, category_id):
        query = "SELECT * FROM contacts WHERE category_id = %s"
        logger.info("Executing query: %s with category_id: %s", query, category_id)
        with self._database_connect() as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (category_id, ))
                return cursor.fetchall()
            

    def create_new_category(self, title):
        query = "INSERT INTO categories (title) VALUES (%s)"
        logger.info("Executing query: %s with title: %s", query, title)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (title, ))
    
    def create_new_contact(self, category_id, name, phone, email):
        query = "INSERT INTO contacts (name, phone, email, category_id) VALUES (%s, %s, %s, %s)"
        logger.info("Executing query: %s with name: %s, phone: %s, email: %s, category_id: %s",
                    query, name, phone, email, category_id)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, phone, email, category_id, ))

    def update_category_by_id(self, category_id, new_title):
        query = "UPDATE categories SET title = %s WHERE id = %s"
        logger.info("Executing query: %s with new_title: %s and id: %s", 
                    query, new_title, category_id)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (new_title, category_id, ))

    def delete_category_by_id(self, category_id):
        query = "DELETE FROM categories WHERE id = %s"
        logger.info("Executing query: %s with category_id: %s", 
                    query, category_id)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (category_id, ))
   
    def edit_contact(self, category_id, contact_id, name, phone, email):
        query = "UPDATE contacts SET name = %s, phone = %s, email = %s WHERE category_id = %s AND id = %s"
        logger.info("Executing query: %s with name: %s, phone: %s, email: %s, category_id: %s, id: %s",
                    query, name, phone, email, category_id, contact_id)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, phone, email, category_id, contact_id, ))

    def delete_contact_from_category(self, category_id, contact_id):
        query = "DELETE FROM contacts WHERE category_id = %s AND id = %s"
        logger.info("Executing query: %s with category_id: %s and contact_id: %s", 
                    query, category_id, contact_id)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (category_id, contact_id, ))

    def delete_all_contacts(self, category_id):
        query = "DELETE FROM contacts WHERE category_id = %s"
        logger.info("Executing query: %s with cateogry_id: %s",
                    query, category_id)
        with self._database_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (category_id, ))