import requests
from faker import Faker
import random
import itertools

# API base URL
BASE_URL = "http://127.0.0.1:5000/api"
def get_token():
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": "root", "password": "act"})
    return response.json().get("access_token")
# JWT token for authorization (replace with a valid token)
TOKEN = get_token()
HEADERS = {
    
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Initialize Faker
fake = Faker()

# Generate Tables
def generate_tables(n):
    for _ in range(n):
        data = {
            "capacity": 4,
            "location": fake.word().capitalize()
        }
        response = requests.post(f"{BASE_URL}/tables/add", headers=HEADERS, json=data)
        print(response.json())


# Generate Customers
def generate_customers(n):
    for _ in range(n):
        data = {
            "name": fake.name(),
            "contact_details": fake.email()
        }
        response = requests.post(f"{BASE_URL}/customers/add", headers=HEADERS, json=data)
        print(response.json())


# Generate Reservations
def generate_reservations(n):
    for i in range(n):
        data = {
            "customer_id": i+1,
            "table_id" : i+1,
            "reservation_date": fake.date_between(start_date='-30d', end_date='+30d').strftime('%Y-%m-%d'),
            "reservation_time": fake.time(),
            "person_count": random.randint(2, 4),
        }
        response = requests.post(f"{BASE_URL}/reservations/add", headers=HEADERS, json=data)
        print(response.json())


# Generate Menu
def generate_menu(n):
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage']
    for _ in range(n):
        data = {
            "dish_name": fake.word().capitalize(),
            "category": random.choice(categories),
            "price": round(random.uniform(5, 50), 2)
        }
        response = requests.post(f"{BASE_URL}/menu/add", headers=HEADERS, json=data)
        print(response.json())


# Generate Orders
def generate_orders(n):
    for _ in range(n):
        data = {
            "reservation_id": random.randint(1, 10),
            "total_amount": round(random.uniform(20, 200), 2),
            "order_status": random.choice(['Pending', 'In Progress', 'Completed', 'Cancelled'])
        }
        response = requests.post(f"{BASE_URL}/orders/add", headers=HEADERS, json=data)
        print(response.json())


# Generate unique combinations of order_id and dish_id
def generate_order_items(n):
    # Create all unique pairs of (order_id, dish_id)
    order_dish_pairs = list(itertools.product(range(1, 11), range(1, 11)))  # 10 orders, 10 dishes

    # Shuffle the pairs to randomize insertion order
    random.shuffle(order_dish_pairs)

    for i in range(min(n, len(order_dish_pairs))):  # Ensure we don't exceed available pairs
        order_id, dish_id = order_dish_pairs[i]  # Select a unique combination

        # Prepare data for the API request
        data = {
            "order_id": order_id,
            "dish_id": dish_id,
            "quantity": random.randint(1, 5)
        }

        # Send POST request to the API
        response = requests.post(f"{BASE_URL}/order_items/add", headers=HEADERS, json=data)

        # Print the response for debugging
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Non-JSON response:", response.text)

# Generate Payments
def generate_payments(n):
    for _ in range(n):
        data = {
            "order_id": random.randint(1, 10),
            "amount_paid": round(random.uniform(10, 200), 2),
            "payment_method": random.choice(['Cash', 'Credit Card', 'Mobile Payment'])
        }
        response = requests.post(f"{BASE_URL}/payments/add", headers=HEADERS, json=data)
        print(response.json())


# Generate Fake Data via API
generate_tables(10)
generate_customers(10)
generate_reservations(10)
generate_menu(10)
generate_orders(10)
generate_order_items(20)
generate_payments(10)

print("Fake data inserted successfully via API!")