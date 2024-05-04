import psycopg2
from faker import Faker
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters for initial connection to the default database
initial_db_params = {
    'dbname': 'postgres',
    'user': 'baeldung',
    'password': 'baeldung',
    'host': 'localhost'
}

# Database connection parameters
db_params = {
    'dbname': 'sql_chatbot',
    'user': 'baeldung',
    'password': 'baeldung',
    'host': 'localhost'
}

# Connect to the default PostgreSQL server
conn = psycopg2.connect(**initial_db_params)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Cursor to execute commands
cur = conn.cursor()

# Check if the specific database exists and create if not
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s",
            (db_params['dbname'],))
exists = cur.fetchone()
if not exists:
    cur.execute(f"CREATE DATABASE {db_params['dbname']}")
    print(f"Database {db_params['dbname']} created successfully.")

# Close the initial connection
cur.close()
conn.close()

# Connect to PostgreSQL server
conn = psycopg2.connect(**db_params)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Cursor to execute commands
cur = conn.cursor()

# Create tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        birthdate DATE
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        product_name VARCHAR(255),
        quantity INTEGER,
        order_date DATE,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
""")

print("Tables created successfully.")

# Generating and inserting fake data
fake = Faker()

# Insert data into Users
user_ids = []
for _ in range(100):  # Generate 100 users
    name = fake.name()
    email = fake.email()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=90)
    cur.execute("INSERT INTO Users (name, email, birthdate) VALUES (%s, %s, %s) RETURNING id",
                (name, email, birthdate))
    user_id = cur.fetchone()[0]
    user_ids.append(user_id)

# Insert data into Orders
for user_id in user_ids:
    # Each user can have 1 to 5 orders
    num_orders = fake.random_int(min=1, max=5)
    for _ in range(num_orders):
        product_name = fake.word()
        quantity = fake.random_int(min=1, max=10)
        order_date = fake.date_between(start_date='-1y', end_date='today')
        cur.execute("INSERT INTO Orders (user_id, product_name, quantity, order_date) VALUES (%s, %s, %s, %s)",
                    (user_id, product_name, quantity, order_date))

# Commit changes and close the connection
conn.commit()
cur.close()
conn.close()

print("Fake data inserted successfully.")
