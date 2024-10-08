import sqlite3

# Connect to SQLite database (creates the database file if it doesn't exist)
conn = sqlite3.connect('bank_application.db')
cursor = conn.cursor()

# Create Admin table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Admin (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'Admin',
        last_login DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('active', 'inactive')) NOT NULL
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        contact_info TEXT,
        password TEXT NOT NULL,
        date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME,
        account_status TEXT CHECK(account_status IN ('active', 'inactive', 'suspended')) DEFAULT 'inactive', -- Default to 'inactive' until verified
        user_role TEXT DEFAULT 'user',
        is_verified BOOLEAN DEFAULT 0,
        preferred_language TEXT DEFAULT 'en',
        date_of_birth DATE,
        security_question TEXT,
        security_answer TEXT
    );
''')
# Table schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bank_Accounts (
        id TEXT PRIMARY KEY,
        account_holder TEXT NOT NULL,
        created_by TEXT NOT NULL,
        account_type TEXT NOT NULL,
        account_status TEXT,
        balance INTEGER DEFAULT 0.00,
        recent_transaction TEXT DEFAULT '0.00',
        transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        credit_amount TEXT DEFAULT 'N/A',
        date_created DATETIME DEFAULT CURRENT_TIMESTAMP
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        loan_amount REAL NOT NULL,
        loan_status TEXT NOT NULL DEFAULT 'Pending',
        loan_type TEXT NOT NULL,
        date_applied DATE NOT NULL,
        date_approved DATE,
        loan_balance REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Currency(
        currency_code CHAR(3) PRIMARY KEY,  -- Currency code (USD, EUR, etc.)
        currency_name VARCHAR(50) NOT NULL  -- Name of the currency
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Currency_Exchange(
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each rate
        base_currency CHAR(3),                 -- Base currency (e.g., USD)
        target_currency CHAR(3),               -- Target currency (e.g., EUR)
        exchange_rate DECIMAL(15, 6),          -- Exchange rate (e.g., 1 USD = 0.85 EUR)
        last_updated TIMESTAMP,                -- Date and time the rate was last updated
        source VARCHAR(100),                   -- Optional: Source of the rate (e.g., central bank)
        FOREIGN KEY (base_currency) REFERENCES Currency(currency_code),
        FOREIGN KEY (target_currency) REFERENCES Currency(currency_code)
    
    );
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
