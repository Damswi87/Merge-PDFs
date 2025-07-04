import sqlite3

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    full_name TEXT
)
''')

# Save changes and close connection
conn.commit()
conn.close()

print("Users table created successfully.")
