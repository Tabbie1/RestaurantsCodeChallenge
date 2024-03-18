import sqlite3
import random

# Connect to the SQLite database
conn = sqlite3.connect('restaurant_reviews.db')
c = conn.cursor()

# Check if tables already exist
c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='restaurants'")
table_exists = c.fetchone()[0]

if not table_exists:
    # Create restaurants table
    c.execute('''CREATE TABLE restaurants
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  price INTEGER)''')

    # Create customers table
    c.execute('''CREATE TABLE customers
                 (id INTEGER PRIMARY KEY,
                  first_name TEXT,
                  last_name TEXT)''')

    # Create reviews table with foreign key constraints for restaurant_id and customer_id
    c.execute('''CREATE TABLE reviews
                 (id INTEGER PRIMARY KEY,
                  restaurant_id INTEGER,
                  customer_id INTEGER,
                  star_rating INTEGER,
                  FOREIGN KEY(restaurant_id) REFERENCES restaurants(id),
                  FOREIGN KEY(customer_id) REFERENCES customers(id))''')

    # Commit changes
    conn.commit()

# Close connection
conn.close()

# Your class implementations and test cases go here...


class Restaurant:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.id = None  # Initialize id to None

    def save_to_db(self):
        # Save restaurant to the database and assign an id
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("INSERT INTO restaurants (name, price) VALUES (?, ?)", (self.name, self.price))
        self.id = c.lastrowid  # Get the id of the last inserted row
        conn.commit()
        conn.close()

    def reviews(self):
        # Fetch reviews for this restaurant from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT * FROM reviews WHERE restaurant_id=?", (self.id,))
        reviews = c.fetchall()
        conn.close()
        return reviews

    def customers(self):
        # Fetch customers who reviewed this restaurant from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT customers.* FROM customers JOIN reviews ON customers.id = reviews.customer_id WHERE reviews.restaurant_id=?", (self.id,))
        customers = c.fetchall()
        conn.close()
        return customers

    @classmethod
    def fanciest(cls):
        # Fetch the fanciest restaurant from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT * FROM restaurants ORDER BY price DESC LIMIT 1")
        fanciest_restaurant = c.fetchone()
        conn.close()
        if fanciest_restaurant:
            restaurant = cls(fanciest_restaurant[1], fanciest_restaurant[2])
            restaurant.id = fanciest_restaurant[0]
            return restaurant
        else:
            return None

    def all_reviews(self):
        # Fetch all reviews for this restaurant from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT customers.first_name, customers.last_name, reviews.star_rating FROM customers JOIN reviews ON customers.id = reviews.customer_id WHERE reviews.restaurant_id=?", (self.id,))
        reviews = c.fetchall()
        conn.close()
        formatted_reviews = [f"Review for {self.name} by {customer[0]} {customer[1]}: {customer[2]} stars." for customer in reviews]
        return formatted_reviews


class Customer:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.id = None  # Initialize id to None

    def save_to_db(self):
        # Save customer to the database and assign an id
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("INSERT INTO customers (first_name, last_name) VALUES (?, ?)", (self.first_name, self.last_name))
        self.id = c.lastrowid  # Get the id of the last inserted row
        conn.commit()
        conn.close()

    def reviews(self):
        # Fetch reviews left by this customer from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT * FROM reviews WHERE customer_id=?", (self.id,))
        reviews = c.fetchall()
        conn.close()
        return reviews

    def restaurants(self):
        # Fetch restaurants reviewed by this customer from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT restaurants.name FROM restaurants JOIN reviews ON restaurants.id = reviews.restaurant_id WHERE reviews.customer_id=?", (self.id,))
        restaurants = c.fetchall()
        conn.close()
        return restaurants

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        # Fetch favorite restaurant of this customer from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("SELECT restaurant_id FROM reviews WHERE customer_id=? ORDER BY star_rating DESC LIMIT 1", (self.id,))
        favorite_restaurant_id = c.fetchone()
        conn.close()
        if favorite_restaurant_id:
            conn = sqlite3.connect('restaurant_reviews.db')
            c = conn.cursor()
            c.execute("SELECT * FROM restaurants WHERE id=?", (favorite_restaurant_id[0],))
            favorite_restaurant = c.fetchone()
            conn.close()
            return Restaurant(favorite_restaurant[1], favorite_restaurant[2])
        else:
            return None

    def add_review(self, restaurant, rating):
        # Add a review for a restaurant by this customer to the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("INSERT INTO reviews (restaurant_id, customer_id, star_rating) VALUES (?, ?, ?)", (restaurant.id, self.id, rating))
        conn.commit()
        conn.close()

    def delete_reviews(self, restaurant):
        # Delete all reviews for a restaurant by this customer from the database
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("DELETE FROM reviews WHERE restaurant_id=? AND customer_id=?", (restaurant.id, self.id))
        conn.commit()
        conn.close()


class Review:
    def __init__(self, restaurant, customer, star_rating):
        self.restaurant = restaurant
        self.customer = customer
        self.star_rating = star_rating
        self.id = None  # Initialize id to None

    def save_to_db(self):
        # Save review to the database and assign an id
        conn = sqlite3.connect('restaurant_reviews.db')
        c = conn.cursor()
        c.execute("INSERT INTO reviews (restaurant_id, customer_id, star_rating) VALUES (?, ?, ?)", (self.restaurant.id, self.customer.id, self.star_rating))
        self.id = c.lastrowid  # Get the id of the last inserted row
        conn.commit()
        conn.close()

    def get_customer(self):
        return self.customer

    def get_restaurant(self):
        return self.restaurant

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."




# Creating instances of Restaurant and Customer
restaurant_names = ["Kilimanjaro", "KFC", "Serena", "Ole Sereni", "Sarova", "Serena"]
restaurant_instances = [Restaurant(name, random.randint(1, 5)) for name in restaurant_names]
for restaurant in restaurant_instances:
    restaurant.save_to_db()

customer_names = [("Mary", "Ann"), ("Joyce", "Wambui"), ("Terry", "Maina"), ("Joy", "Njeri"), ("Chep", "Kiprop")]
customer_instances = [Customer(first_name, last_name) for first_name, last_name in customer_names]
for customer in customer_instances:
    customer.save_to_db()

# Adding reviews
Review(restaurant_instances[0], customer_instances[0], 4).save_to_db()
Review(restaurant_instances[1], customer_instances[0], 5).save_to_db()
Review(restaurant_instances[0], customer_instances[1], 3).save_to_db()
Review(restaurant_instances[2], customer_instances[2], 4).save_to_db()
Review(restaurant_instances[3], customer_instances[3], 5).save_to_db()
Review(restaurant_instances[4], customer_instances[3], 3).save_to_db()
Review(restaurant_instances[5], customer_instances[4], 4).save_to_db()
Review(restaurant_instances[1], customer_instances[4], 5).save_to_db()

# Test cases
# Review customer()
# Test case: Review customer()
print("Test case: Review customer()")
review_instance = Review(restaurant_instances[0], customer_instances[0], 4)
print(review_instance.get_customer().full_name())  # Expected output: Mary Ann


# Test case: Review restaurant()
print("Test case: Review restaurant()")
print(review_instance.get_restaurant().name)  # Expected output: Kilimanjaro

# Restaurant reviews()
print("Test case: Restaurant reviews()")
for review in restaurant_instances[0].reviews():
    print(f"{review[1]} stars by customer ID {review[2]}")  # Expected output: 4 stars by customer ID 1

# Restaurant customers()
print("Test case: Restaurant customers()")
for customer in restaurant_instances[0].customers():
    print(f"{customer[1]} {customer[2]}")  # Expected output: Mary Ann

# Customer reviews()
print("Test case: Customer reviews()")
for review in customer_instances[0].reviews():
    print(f"Rating: {review[3]} for restaurant ID {review[1]}")  # Expected output: Rating: 4 for restaurant ID 1

# Customer restaurants()
print("Test case: Customer restaurants()")
for restaurant in customer_instances[0].restaurants():
    print(restaurant[0])  # Expected output: Kilimanjaro

# Customer full_name()
print("Test case: Customer full_name()")
print(customer_instances[0].full_name())  # Expected output: Mary Ann

# Customer favorite_restaurant()
print("Test case: Customer favorite_restaurant()")
print(customer_instances[0].favorite_restaurant().name)  # Expected output: KFC

# Customer add_review()
print("Test case: Customer add_review()")
customer_instances[0].add_review(restaurant_instances[2], 5)  # Adding a review for restaurant Serena by Mary Ann

# Customer delete_reviews()
print("Test case: Customer delete_reviews()")
customer_instances[0].delete_reviews(restaurant_instances[0])  # Deleting all reviews for Kilimanjaro by Mary Ann
