from datetime import datetime
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("bank_application.db")
cursor = conn.cursor()


# Fetch all records from the Users table
def fetch_users():
    cursor.execute('''
        SELECT id, name, email, contact_info, password, date_created, last_login, account_status, 
               user_role, is_verified, preferred_language, date_of_birth, security_question, security_answer 
        FROM Users
    ''')
    users = cursor.fetchall()

    if users:
        print("\nList of Users:")
        print("{:<5} {:<15} {:<25} {:<15} {:<15} {:<20} {:<20} {:<10} {:<10} {:<10} {:<10} {:<15} {:<25} {:<20}".format(
            "ID", "Name", "Email", "Password", "Contact Info", "Date Created", "Last Login",
            "Status", "Verified", "User Role", "Language", "Date of Birth", "Security Question", "Security Answer"
        ))
        print("-" * 225)

        for user in users:
            # Unpack the fields based on the updated schema
            user_id, name, email, contact_info, password, date_created, last_login, account_status, user_role, is_verified, preferred_language, date_of_birth, security_question, security_answer = user

            # Display the fields in the correct columns
            print(
                "{:<5} {:<15} {:<25} {:<15} {:<15} {:<20} {:<20} {:<10} {:<10} {:<10} {:<10} {:<15} {:<20} {:<20}".format(
                    user_id, name, email, password, contact_info, date_created, last_login,
                    account_status, is_verified, user_role, preferred_language, date_of_birth, security_question,
                    security_answer
                ))
    else:
        print("No users found in the database.")


def fetch_admin():
    cursor.execute('''
            SELECT id, name, email, password, role, last_login, created_at, 
                   status
            FROM Admin
        ''')
    admins = cursor.fetchall()

    if admins:
        print("\nList of admins:")
        print("{:<5} {:<23} {:<25} {:<15} {:<15} {:<20} {:<20} {:<10}".format(
            "ID", "Name", "Email", "Password", "Role", "Date Created", "Last Login", "Status"))
        print("-" * 225)

        for admin in admins:
            admin_id, name, email, password, role, last_login, created_at, status = admin

            # Replace None with 'N/A' or any other placeholder for display purposes
            last_login = last_login if last_login is not None else 'N/A'
            created_at = created_at if created_at is not None else 'N/A'

            print("{:<5} {:<20} {:<25} {:<15} {:<15} {:<20} {:<20} {:<10}".format(
                admin_id, name, email, password, role, created_at, last_login, status))
    else:
        print("No admins found in the database.")


def fetch_bank_accounts():
    cursor.execute('''
            SELECT id, account_holder, created_by, account_type, account_status, balance, recent_transaction, 
                   transaction_date, credit_amount, date_created
            FROM Bank_Accounts
        ''')
    bank_accounts = cursor.fetchall()

    if bank_accounts:
        print("\nList of bank accounts:")
        print("{:<5} {:<15} {:<15} {:<15} {:<15} {:<10} {:<25} {:<25} {:<15} {:<10}".format(
            "id", "account_holder", "created_by", "account type", "account_status", "balance", "recent_transaction", "transaction_date", "credit_amount", "date created"))
        print("-" * 225)

        for bank_account in bank_accounts:
            bank_id, account_holder, admin_id, account_type, account_status, balance, recent_transaction, transaction_date, credit_amount, date_created = bank_account

            # Replace None with 'N/A' or any other placeholder for display purposes
            # last_login = last_login if last_login is not None else 'N/A'
            # created_at = created_at if created_at is not None else 'N/A'

            print("{:<5} {:<15} {:<15} {:<15} {:<15} {:<10} {:<25} {:<25} {:<15} {:<10}".format(
                bank_id, account_holder, admin_id, account_type, account_status, balance, recent_transaction, transaction_date, credit_amount, date_created))
    else:
        print("\nNo bank accounts found in the database.")


def fetch_user_bank_account():
    user_id = input("\nEnter Account holders ID: ")
    cursor.execute('''
                SELECT id, account_type, account_status, balance, recent_transaction, 
                       transaction_date, credit_amount, date_created
                FROM Bank_Accounts WHERE account_holder = ?
            ''',  (user_id,))
    user_accounts = cursor.fetchall()

    if user_accounts:
        print("\nList of user accounts:")
        print("{:<5} {:<15} {:<15} {:<10} {:<25} {:<25} {:<15} {:<10}".format(
            "id", "account type", "account_status", "balance", "recent_transaction", "transaction_date", "credit_amount", "date created"))
        print("-" * 225)

        for user_account in user_accounts:
            bank_id, account_type, account_status, balance, recent_transaction, transaction_date, credit_amount, date_created = user_account

            # Replace None with 'N/A' or any other placeholder for display purposes
            # last_login = last_login if last_login is not None else 'N/A'
            # created_at = created_at if created_at is not None else 'N/A'

            print("{:<5} {:<15} {:<15} {:<10} {:<25} {:<25} {:<15} {:<10}".format(
                bank_id, account_type, account_status, balance, recent_transaction,
                transaction_date, credit_amount, date_created))
    else:
        print("\nNo bank accounts found in the database.")


def fetch_loans():
    """
    Allows the admin or user to view all loan applications and their status.
    """
    cursor.execute('''
        SELECT loan_id, user_id, loan_amount, loan_status, loan_type, date_applied, date_approved, loan_balance
        FROM Loans
    ''')
    loans = cursor.fetchall()

    if loans:
        print("\nList of Loans:")
        print("{:<10} {:<10} {:<15} {:<10} {:<15} {:<15} {:<15} {:<15}".format(
            "Loan ID", "Account ID", "Loan Amount", "Status", "Loan Type", "Date Applied", "Date Approved", "Balance"))
        print("-" * 100)

        for loan in loans:
            loan_id, account_id, loan_amount, loan_status, loan_type, date_applied, date_approved, loan_balance = loan
            date_approved = date_approved if date_approved is not None else 'N/A'
            print("{:<10} {:<10} {:<15} {:<10} {:<15} {:<15} {:<15} {:<15}".format(
                loan_id, account_id, loan_amount, loan_status, loan_type, date_applied, date_approved, loan_balance))
    else:
        print("\nNo loan applications found.")


fetch_users()
# fetch_admin()
# fetch_bank_accounts()
# fetch_user_bank_account()
# fetch_loans()
# Close the connection
# conn.close()

