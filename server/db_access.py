import datetime
import sqlite3

class DBAccess:
    """
    A class that holds the DB access - queries the web server is using
    """
    def __init__(self, db_name="ctf_db.db"):
        self.db_name = db_name

    def get_user_by_name(self, username):
        """
        Find a user by name
        :param username: the user name to look for
        :return: A dict with user id, name, password, is_admin, first_car, birth_place
        """
        query = f"SELECT id, name, password, is_admin, first_car, birth_place from Users where name='{username}';"
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            res = cursor.execute(query).fetchone()
            cursor.close()
        if res:
            return {'id': res[0], 'name': res[1], 'password': res[2],
                    'is_admin': res[3], 'first_car': res[4], 'birth_place': res[5]}

    def get_user_by_id(self, id):
        """
        Find a user by id
        :param id: the user id to look for
        :return: A dict with user id, name, password, is_admin, first_car, birth_place
        """
        query = f"SELECT id, name, password, is_admin, first_car, birth_place from Users where id={id};"
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            res = cursor.execute(query).fetchone()
            cursor.close()
        if res:
            return {'id': res[0], 'name': res[1], 'password': res[2],
                    'is_admin': res[3], 'first_car': res[4], 'birth_place': res[5]}

    def set_user_password(self, id, password):
        """
        Set a new password for a user by ID
        :param id: The user ID
        :param password: The new password to set
        :return:
        """
        query = f"UPDATE Users SET password='{password}' WHERE id={id};"
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            cursor.close()

    def get_user_profile(self, id):
        """
        Get the user profile for an ID
        :param id: The user ID
        :return: The user profile dict
        """
        query = f"SELECT full_name, address, email, account FROM user_profile WHERE id={id};"
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            res = cursor.execute(query).fetchone()
            cursor.close()
        if res:
            return {'full_name': res[0], 'address': res[1], 'email': res[2], 'account': res[3]}

    def get_products(self, name_part):
        """
        Get a list of products matching a query
        :param name_part: The substring to look for in the product names
        :return: A list of dicts with id, name, description, price, image
        """
        fields = ['id', 'name', 'description', 'price', 'image']
        fields_out = ['id', 'name', 'desc', 'price', 'img']
        query = f'SELECT {",".join(fields)} from Products WHERE name LIKE "%{name_part.lower()}%" LIMIT 100;'
        print(query)
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            res = cursor.execute(query).fetchall()
            cursor.close()
        if res:
            return [dict(zip(fields_out, row)) for row in res]

    def add_purchase(self, product_id, user_id):
        """
        Record a purchase - that a customer purchased a product
        :return:
        """
        today = datetime.datetime.utcnow().date()
        query = f"INSERT INTO Purchases (date, product_id, user_id) VALUES ('{today}', {product_id}, {user_id});"
        print(query)
        with sqlite3.connect(self.db_name) as db:
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            cursor.close()
