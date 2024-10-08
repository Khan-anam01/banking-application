import sqlite3
from datetime import datetime

import view_table

# Establish database connection
conn = sqlite3.connect('bank_application.db')
cursor = conn.cursor()

# Global variable to hold the currently logged-in user ID
current_user_id = None

# Security Questions
Security_Question = [
    "What is your pet's name?",
    "What school did you go to?",
    "Where were you born?",
    "What is your last name?"
]


# Check credentials function
def check_credentials(table_name, user_id, password):
    cursor.execute(f"SELECT id, password FROM {table_name} WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    return user and user[1] == password  # Return True if credentials are valid


# Login menu
def login_menu():
    global current_user_id  # Use global variable to track the current user
    print("Welcome! Please log in.")
    while True:
        user_id = input("Enter your ID: ")
        password = input("Enter your password: ")

        # Check if the user is an admin
        if check_credentials("Admin", user_id, password):
            print("\nLogin successful as Admin!")
            current_user_id = user_id  # Store the logged-in admin ID
            admin_menu()  # Redirect to admin menu
        # Check if the user is a normal user
        elif check_credentials("Users", user_id, password):
            print("\nLogin successful as User!")
            current_user_id = user_id  # Store the logged-in user ID
            user_menu()  # Redirect to user menu
        else:
            print("\nInvalid ID or password. Please try again.")


# User menu function
def user_menu():
    while True:
        print(f"\nWelcome to the User menu! Logged in as User ID: {current_user_id}")
        choice = input("""
        1. View Accounts
        2. Update Profile
        3. Withdraw Funds
        4. Send Money
        5. Deposit Funds
        6. Apply for a Loan
        7. Repay Loan
        8. Exit
        Enter your choice: """)

        if choice == '1':
            fetch_user_bank_account()
        elif choice == '2':
            update_profile()
        elif choice == '3':
            withdraw_funds()
        elif choice == '4':
            send_money()
        elif choice == '5':
            deposit_funds()
        elif choice == '6':
            apply_for_loan()
        elif choice == '7':
            repay_loan()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please pick again.")


# Admin menu function
def admin_menu():
    while True:
        print(f"\nWelcome to the Admin menu! Logged in as Admin ID: {current_user_id}")
        choice = input("""
        1. Add Accounts
        2. Delete Accounts
        3. Activate Accounts
        4. Deactivate Accounts
        5. Update Accounts
        6. Change/Reset Passwords
        7. Approve/Reject Loans
        8. Exit
        Enter your choice: """)

        if choice == '1':
            account_choice = input("1. User account\n2. Admin account\n3. Bank account\n4. Exit: ")
            if account_choice == '1':
                add_user(current_user_id)
            elif account_choice == '2':
                add_admin(current_user_id)
            elif account_choice == '3':
                create_bank_account(current_user_id)
            elif account_choice == '4':
                break
            else:
                print("Invalid entry!")
        elif choice == '2':
            account_choice = input("1. User account\n2. Admin account\n3. Bank account\n4. Exit: ")
            if account_choice == '1':
                delete_user_record(current_user_id)
            elif account_choice == '2':
                delete_admin_record(current_user_id)
            elif account_choice == '3':
                delete_bank_account(current_user_id)
            elif account_choice == '4':
                break
            else:
                print("Invalid entry!")
        elif choice == '3':
            activate_accounts()
        elif choice == '4':
            deactivate_accounts()
        elif choice == '5':
            table_name = input("Enter the table to update: ")
            account_id = input("Enter the account id to update: ")
            update_field = input("Enter the field you want to update")
            update_value = input("Enter the new value of the field")
            update_accounts(table_name, account_id, update_field, update_value)
        elif choice == '6':
            manage_password()
        elif choice == '7':
            approve_or_reject_loan()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid entry. Try again.")


# user functions
def fetch_user_bank_account():
    user_id = current_user_id
    cursor.execute('''
                SELECT id, account_type, account_status, balance, recent_transaction, 
                       transaction_date, credit_amount, date_created
                FROM Bank_Accounts WHERE account_holder = ?
            ''', (user_id,))
    user_accounts = cursor.fetchall()

    if user_accounts:
        print("\nList of user accounts:")
        print("{:<5} {:<15} {:<15} {:<10} {:<25} {:<25} {:<15} {:<10}".format(
            "id", "account type", "account_status", "balance", "recent_transaction", "transaction_date",
            "credit_amount", "date created"))
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


def update_accounts(table_name, account_id, fields, values):
    """
    Updates one or more fields in the specified table.

    Args:
    table_name (str): Name of the table to update (Users, Admin, Bank_Accounts).
    account_id (str): ID of the record to update.
    fields (list): The list of column names to update.
    values (list): The corresponding new values for the specified fields.

    Returns:
    None
    """
    valid_tables = ['Users', 'Admin', 'Bank_Accounts']
    if table_name not in valid_tables:
        print(f"Invalid table name. Please choose from {valid_tables}.")
        return

    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (account_id,))
    record = cursor.fetchone()

    if record:
        # Create the dynamic update query
        update_fields = ', '.join([f"{field} = ?" for field in fields])
        cursor.execute(f"UPDATE {table_name} SET {update_fields} WHERE id = ?", (*values, account_id))
        conn.commit()
        print(f"Record with ID {account_id} in table {table_name} has been successfully updated.")
    else:
        print(f"Record with ID {account_id} not found in {table_name}.")


def update_menu():
    """
    Menu to prompt the user for table, record ID, field, and new value to update.
    """
    print("Which table do you want to update?")

    # Tables and fields for updating
    table_options = ["Users", "Admin", "Bank_Accounts"]
    users_table = ["name", "email", "contact_info", "account_status", "user_role",
                   "is_verified", "preferred_language", "security_question", "security_answer"]
    admins_table = ["name", "email", "role", "status"]
    bank_accounts = ["account_status", "credit_amount"]

    # Display table options
    for idx, option in enumerate(table_options, 1):
        print(f"{idx}. {option}")

    try:
        table_choice = int(input("Enter the number of the table to update: "))

        # Initialize the 'field' variable
        fields = []
        values = []

        if table_choice in [1, 2, 3]:
            table_name = table_options[table_choice - 1]
            record_id = input(f"Enter the ID of the record to update in {table_name}: ")

            # Handle updates for the Users table
            if table_name == "Users":
                for index, field_option in enumerate(users_table, 1):
                    print(f"{index}. {field_option}")
                field_choice = int(input(f"Enter the field to update in {table_name}: "))

                if 1 <= field_choice <= len(users_table):
                    field = users_table[field_choice - 1]
                    if field == "security_question":
                        # If "security question" is chosen, prompt for both question and answer

                        for index, count in enumerate(Security_Question, start=1):
                            print(f"{index}. {count}")
                        choice = int(input("choose your security question from the above list: "))
                        new_question = Security_Question[choice - 1]
                        new_answer = input("Enter the new security answer: ")

                        # Append both to fields and values
                        fields.append("security_question")
                        fields.append("security_answer")
                        values.append(new_question)
                        values.append(new_answer)
                    else:
                        new_value = input(f"Enter the new value for {field}: ")
                        fields.append(field)
                        values.append(new_value)
                else:
                    print("Invalid field choice.")
                    return  # Exit if invalid field is chosen

            # Handle updates for the Admin table
            elif table_name == "Admin":
                for index, field_option in enumerate(admins_table, 1):
                    print(f"{index}. {field_option}")
                field_choice = int(input(f"Enter the field to update in {table_name}: "))
                if 1 <= field_choice <= len(admins_table):
                    field = admins_table[field_choice - 1]
                    new_value = input(f"Enter the new value for {field}: ")
                    fields.append(field)
                    values.append(new_value)
                else:
                    print("Invalid field choice.")
                    return

            # Handle updates for the Bank_Accounts table
            elif table_name == "Bank_Accounts":
                for index, field_option in enumerate(bank_accounts, 1):
                    print(f"{index}. {field_option}")
                field_choice = int(input(f"Enter the field to update in {table_name}: "))
                if 1 <= field_choice <= len(bank_accounts):
                    field = bank_accounts[field_choice - 1]
                    new_value = input(f"Enter the new value for {field}: ")
                    fields.append(field)
                    values.append(new_value)
                else:
                    print("Invalid field choice.")
                    return

            # Call the update function with the fields and values
            update_accounts(table_name, record_id, fields, values)
        else:
            print("Invalid choice. Please try again.")

    except ValueError:
        print("Invalid input. Please enter a number corresponding to the menu choice.")


def deposit_funds():
    """
    Function to deposit money into the user's own account, checking account status.
    """
    global current_user_id  # Use the logged-in user ID from the global scope
    account_id = input("Enter the account ID for deposit: ")

    # Fetch account details
    cursor.execute("SELECT balance, account_status, account_holder FROM Bank_Accounts WHERE id = ?", (account_id,))
    result = cursor.fetchone()

    if result:
        current_balance, account_status, account_holder = result

        # Check if the account belongs to the current user
        if account_holder != current_user_id:
            print("You are not authorized to deposit into this account.")
            return

        # Check if the account is active
        if account_status != "active":
            print("This account is inactive. Please contact the administrator.")
            return

        deposit_amount = float(input("Enter the amount to deposit: "))

        if deposit_amount > 0:
            new_balance = current_balance + deposit_amount
            recent_transaction = f"Deposit of {deposit_amount}"
            transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update the balance, recent transaction, and transaction date
            cursor.execute('''
                UPDATE Bank_Accounts
                SET balance = ?, recent_transaction = ?, transaction_date = ?
                WHERE id = ?
            ''', (new_balance, recent_transaction, transaction_date, account_id))

            conn.commit()
            print(f"Successfully deposited {deposit_amount}. New balance is {new_balance}.")
        else:
            print("Deposit amount must be positive.")
    else:
        print("Account not found.")


# done by user
def withdraw_funds():
    """
    Function to withdraw money from the user's own account, checking account status.
    """
    global current_user_id  # Use the logged-in user ID from the global scope
    account_id = input("Enter the account ID for withdrawal: ")

    # Fetch account details
    cursor.execute("SELECT balance, account_status, account_holder FROM Bank_Accounts WHERE id = ?", (account_id,))
    result = cursor.fetchone()

    if result:
        current_balance, account_status, account_holder = result

        # Check if the account belongs to the current user
        if account_holder != current_user_id:
            print("You are not authorized to withdraw from this account.")
            return

        # Check if the account is active
        if account_status != "active":
            print("This account is inactive. Please contact the administrator.")
            return

        withdraw_amount = float(input("Enter the amount to withdraw: "))

        if withdraw_amount > 0:
            if withdraw_amount <= current_balance:
                new_balance = current_balance - withdraw_amount
                recent_transaction = f"Withdrawal of {withdraw_amount}"
                transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Update the balance, recent transaction, and transaction date
                cursor.execute('''
                    UPDATE Bank_Accounts
                    SET balance = ?, recent_transaction = ?, transaction_date = ?
                    WHERE id = ?
                ''', (new_balance, recent_transaction, transaction_date, account_id))

                conn.commit()
                print(f"Successfully withdrew {withdraw_amount}. New balance is {new_balance}.")
            else:
                print("Insufficient funds.")
        else:
            print("Withdrawal amount must be positive.")
    else:
        print("Account not found.")


# done by user
def send_money():
    """
    Function to send money from the user's account to another user's account, checking account status.
    """
    global current_user_id  # Use the logged-in user ID from the global scope
    source_account_id = input("Enter the source account ID: ")
    destination_account_id = input("Enter the destination account ID: ")

    if source_account_id == destination_account_id:
        print("Source and destination accounts cannot be the same.")
        return

    # Fetch source account details
    cursor.execute("SELECT balance, account_status, account_holder FROM Bank_Accounts WHERE id = ?",
                   (source_account_id,))
    source_account = cursor.fetchone()

    # Fetch destination account details
    cursor.execute("SELECT balance, account_status FROM Bank_Accounts WHERE id = ?", (destination_account_id,))
    destination_account = cursor.fetchone()

    if not source_account or not destination_account:
        print("One or both account IDs are invalid.")
        return

    source_balance, source_account_status, source_account_holder = source_account
    destination_balance, destination_account_status = destination_account

    # Ensure the source account belongs to the current user
    if source_account_holder != current_user_id:
        print("You are not authorized to send money from this account.")
        return

    # Check if both accounts are active
    if source_account_status != "active":
        print("Your source account is inactive. Please contact the administrator.")
        return
    if destination_account_status != "active":
        print("The destination account is inactive. Please contact the administrator.")
        return

    # Get transfer amount from the user
    transfer_amount = float(input("Enter the amount to transfer: "))

    if transfer_amount <= 0:
        print("Transfer amount must be positive.")
        return

    # Check if the source account has enough balance
    if transfer_amount > source_balance:
        print("Insufficient funds in the source account.")
        return

    # Perform the transfer by adjusting balances
    new_source_balance = source_balance - transfer_amount
    new_destination_balance = destination_balance + transfer_amount

    # Update the source account's balance
    recent_transaction_source = f"Transfer Out - {transfer_amount}"
    transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE Bank_Accounts
        SET balance = ?, recent_transaction = ?, transaction_date = ?
        WHERE id = ?
    ''', (new_source_balance, recent_transaction_source, transaction_date, source_account_id))

    # Update the destination account's balance
    recent_transaction_destination = f"Transfer In - {transfer_amount}"
    cursor.execute('''
        UPDATE Bank_Accounts
        SET balance = ?, recent_transaction = ?, transaction_date = ?
        WHERE id = ?
    ''', (new_destination_balance, recent_transaction_destination, transaction_date, destination_account_id))

    # Commit the transaction
    conn.commit()

    print(
        f"Successfully transferred {transfer_amount} from account {source_account_id} to account {destination_account_id}.")
    print(f"New balance in source account: {new_source_balance}")
    print(f"New balance in destination account: {new_destination_balance}")


def apply_for_loan():
    """
    Allows a user to apply for a loan. The loan is associated with the logged-in user's account.
    A loan can only be applied for if the user has at least one active bank account.
    """
    global current_user_id  # Use the logged-in user ID from the global scope

    # Check if the user has any active bank accounts
    cursor.execute("SELECT id FROM Bank_Accounts WHERE account_holder = ? AND account_status = 'active'",
                   (current_user_id,))
    active_accounts = cursor.fetchall()

    if not active_accounts:
        print("You must have at least one active bank account to apply for a loan. Please contact the administrator.")
        return

    # Proceed to loan application since the user has at least one active account
    loan_amount = float(input("Enter the loan amount: "))
    loan_type = input("Enter the loan type (e.g., personal, business): ")

    # Set the date of loan application
    date_applied = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert loan application into the Loans table
    cursor.execute('''
        INSERT INTO Loans (user_id, loan_amount, loan_status, loan_type, date_applied, loan_balance)
        VALUES (?, ?, 'Pending', ?, ?, ?)
    ''', (current_user_id, loan_amount, loan_type, date_applied, loan_amount))

    conn.commit()

    print(f"Loan application for {loan_amount} submitted successfully. Status: Pending")


def repay_loan():
    """
    Allows a user to repay their loan. It checks if the user has an approved loan and selects an active account to debit for repayment.
    The function handles partial repayments, full repayments, and prevents overpaying.
    """
    global current_user_id  # Assume we are using the logged-in user's ID from the global scope

    # Step 1: Check if the user has an approved loan
    cursor.execute("SELECT loan_id, loan_balance FROM Loans WHERE user_id = ? AND loan_status = 'Approved'",
                   (current_user_id,))
    loan = cursor.fetchone()

    if not loan:
        print("You do not have any approved loans to repay.")
        return

    loan_id, loan_balance = loan

    # Step 2: Check if the user has any active bank accounts
    cursor.execute("SELECT id, balance FROM Bank_Accounts WHERE account_holder = ? AND account_status = 'active'",
                   (current_user_id,))
    active_accounts = cursor.fetchall()

    if not active_accounts:
        print("You must have at least one active bank account to repay the loan. Please contact the administrator.")
        return

    # Display active accounts for the user to select from
    print("\nYour active accounts:")
    for i, (account_id, balance) in enumerate(active_accounts, start=1):
        print(f"{i}. Account ID: {account_id}, Balance: {balance}")

    # Step 3: Prompt user to select an account to debit for the loan repayment
    account_choice = int(input("Select the account number to debit for repayment: ")) - 1
    if account_choice < 0 or account_choice >= len(active_accounts):
        print("Invalid account choice.")
        return

    selected_account_id, account_balance = active_accounts[account_choice]

    # Step 4: Prompt user to enter the repayment amount
    repayment_amount = float(input(f"Enter the amount to repay (Loan Balance: {loan_balance}): "))

    if repayment_amount <= 0:
        print("Repayment amount must be positive.")
        return

    # Step 5: Handle repayment scenarios (partial, full, and overpayments)
    if account_balance == 0:
        print(f"Your selected account (ID: {selected_account_id}) has insufficient funds.")
        return

    if repayment_amount > loan_balance:
        repayment_amount = loan_balance  # Cap the repayment amount to the outstanding loan balance

    # Step 6: Check if the account balance is sufficient
    if account_balance < repayment_amount:
        # Partial repayment scenario
        print(f"Your account balance is less than the repayment amount. Debiting {account_balance} from your account.")
        loan_balance -= account_balance
        recent_transaction = f"Partial Loan Repayment of {account_balance}"
        new_account_balance = 0  # All funds from the account are debited
    else:
        # Full or exact repayment scenario
        print(f"Debiting {repayment_amount} from your account for loan repayment.")
        loan_balance -= repayment_amount
        recent_transaction = f"Loan Repayment of {repayment_amount}"
        new_account_balance = account_balance - repayment_amount

    # Step 7: Update the bank account's balance and transaction details
    transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE Bank_Accounts
        SET balance = ?, recent_transaction = ?, transaction_date = ?
        WHERE id = ?
    ''', (new_account_balance, recent_transaction, transaction_date, selected_account_id))

    # Step 8: Update the loan balance or delete the loan record if fully repaid
    if loan_balance > 0:
        # Loan still has an outstanding balance
        print(f"You still owe {loan_balance}.")
        cursor.execute("UPDATE Loans SET loan_balance = ? WHERE loan_id = ?", (loan_balance, loan_id))
    else:
        # Loan is fully repaid, delete the loan record
        print("Congratulations! Your loan is fully repaid.")
        cursor.execute("DELETE FROM Loans WHERE id = ?", (loan_id,))

    # Step 9: Commit the changes to the database
    conn.commit()

    print("Loan repayment process completed.")


# Admin functions
def generate_admin_id():
    cursor.execute("SELECT id FROM Admin ORDER BY id DESC LIMIT 1")
    last_admin = cursor.fetchone()

    if last_admin:
        last_id_num = int(last_admin[0][3:])  # Extract the numeric part from 'ADM0001'
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # If no admins exist, start with 1

    # Format the new ID as 'ADM0001', 'ADM0002', etc.
    new_admin_id = f"ADM{new_id_num:04d}"
    return new_admin_id


# done by admin
def add_admin(current_admin_id):
    """
    Allows a super admin to add a new admin.
    """
    # Check if the current admin is active and a super admin
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to add records. Admin status is inactive.")
        return

    if admin[0] != 'Super Admin':
        print("Only Super Admins can add other admins.")
        return

    # Proceed to add new admin
    admin_id = generate_admin_id()
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    role = input("Enter admin role (default is 'Admin'): ") or 'Admin'
    status = input("Enter admin status (active/inactive): ")

    while True:
        password = input("Enter your password: ")
        confirm_password = input("Confirm your password: ")
        if password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")

    # Insert data into Admin table
    cursor.execute('''
        INSERT INTO Admin (id, name, email, password, role, status, last_login, created_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (admin_id, name, email, password, role, status))

    conn.commit()
    print("Admin added successfully.")


# Function to add a User
def generate_user_id():
    cursor.execute("SELECT id FROM Users ORDER BY id DESC LIMIT 1")
    last_user = cursor.fetchone()

    if last_user:
        last_id_num = int(last_user[0][2:])  # Extract the numeric part from 'US0001'
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # If no users exist, start with 1

    # Format the new ID as 'US0001', 'US0002', etc.
    new_user_id = f"US{new_id_num:04d}"
    return new_user_id


# done by user
def add_user(current_admin_id):
    """
    Allows an active admin to add a new user.
    """
    # Check if the current admin is active
    cursor.execute("SELECT status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You do not have permission to add users. Admin status is inactive.")
        return

    # Proceed to add new user
    print("Enter user details in the prompt below")
    user_id = generate_user_id()
    name = input("Enter user name: ")
    email = input("Enter user email: ")
    contact_info = input("Enter user contact info: ")
    date_of_birth = input("Enter date of birth (YYYY-MM-DD, optional): ")
    account_status = 'inactive'  # User account starts as inactive until verified
    user_role = 'user'
    is_verified = 0
    preferred_language = 'en'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Security question selection
    print("\nChoose your preferred security question:")
    for index, question in enumerate(Security_Question, start=1):
        print(f"{index}. {question}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: ")) - 1
            if 0 <= choice < len(Security_Question):
                security_question = Security_Question[choice]
                break
            else:
                print("Invalid choice, please select a valid number.")
        except ValueError:
            print("Please enter a number.")

    security_answer = input("Enter your security answer: ")

    # Password validation loop
    while True:
        password = input("Enter your password: ")
        confirm_password = input("Confirm your password: ")
        if password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")

    # Insert data into Users table
    cursor.execute('''
        INSERT INTO Users (id, name, email, contact_info, password, account_status, 
                           user_role, is_verified, preferred_language, date_of_birth, 
                           last_login, security_question, security_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, email, contact_info, password, account_status, user_role, is_verified,
          preferred_language, date_of_birth, date, security_question, security_answer))

    conn.commit()
    print("User added successfully. Account is inactive until verified.")


def generate_account_id():
    cursor.execute("SELECT id FROM Bank_Accounts ORDER BY id DESC LIMIT 1")
    last_account = cursor.fetchone()

    if last_account:
        last_id_num = int(last_account[0][2:])  # Extract the numeric part from 'ADM0001'
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # If no admins exist, start with 1

    new_account_id = f"BA{new_id_num:04d}"
    return new_account_id


# done by admin
def create_bank_account(current_admin_id):
    """
    Allows an active admin to create a new bank account for a user.
    """
    # Check if the current admin is active
    cursor.execute("SELECT status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You do not have permission to add bank accounts. Admin status is inactive.")
        return

    # Proceed to create new bank account
    account_id = generate_account_id()
    user_id = input("Enter the user id for the account: ")
    account_type = input("Enter the type of account (e.g., Saving, Checking): ")
    admin_id = current_admin_id
    balance = input("Enter the initial deposit: ")
    credit_amount = input("Enter the initial credit given: ")
    account_status = 'inactive'  # Default status for newly created accounts
    date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert into the Bank_Accounts table without specifying recent_transaction
    cursor.execute('''
        INSERT INTO Bank_Accounts (id, account_holder, created_by, account_type, account_status, balance, 
                                   transaction_date, credit_amount, date_created)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
    ''', (account_id, user_id, admin_id, account_type, account_status, balance,
          credit_amount, date_created))

    conn.commit()
    print("Bank account created successfully.")


def delete_admin_record(current_admin_id):
    """
    Deletes a record from the Admin table based on the admin ID. Only Super Admins can delete admin records.
    """
    # Check if the current admin is active and a super admin
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to delete records. Admin status is inactive.")
        return

    if admin[0] != 'super':
        print("Only Super Admins can delete admin records.")
        return

    # Get admin ID to delete
    admin_id = input("Enter the Admin ID to delete: ")

    # Check if the admin record exists
    cursor.execute("SELECT id FROM Admin WHERE id = ?", (admin_id,))
    admin_record = cursor.fetchone()

    if not admin_record:
        print("Admin record not found.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete Admin ID {admin_id}? (yes/no): ").lower()
    if confirmation != 'yes':
        print("Operation cancelled.")
        return

    # Delete the admin record
    cursor.execute("DELETE FROM Admin WHERE id = ?", (admin_id,))
    conn.commit()

    print(f"Admin record with ID {admin_id} has been successfully deleted.")


def delete_user_record(current_admin_id):
    """
    Deletes a record from the Users table based on the user ID. Super and Management Admins can delete user records.
    """
    # Check if the current admin is active
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to delete records. Admin status is inactive.")
        return

    # Get user ID to delete
    user_id = input("Enter the User ID to delete: ")

    # Check if the user record exists
    cursor.execute("SELECT id FROM Users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        print("User record not found.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete User ID {user_id}? (yes/no): ").lower()
    if confirmation != 'yes':
        print("Operation cancelled.")
        return

    # Delete the user record
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    conn.commit()

    print(f"User record with ID {user_id} has been successfully deleted.")


def delete_bank_account(current_admin_id):
    """
    Deletes a record from the Bank_Accounts table based on the account ID.
    Super and Management Admins can delete bank account records.
    """
    # Check if the current admin is active
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_admin_id,))
    admin = cursor.fetchone()

    if not admin or admin[1] != 'active':
        print("You do not have permission to delete records. Admin status is inactive.")
        return

    # Get bank account ID to delete
    account_id = input("Enter the Bank Account ID to delete: ")

    # Check if the bank account record exists
    cursor.execute("SELECT id FROM Bank_Accounts WHERE id = ?", (account_id,))
    account = cursor.fetchone()

    if not account:
        print("Bank account record not found.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete Bank Account ID {account_id}? (yes/no): ").lower()
    if confirmation != 'yes':
        print("Operation cancelled.")
        return

    # Delete the bank account record
    cursor.execute("DELETE FROM Bank_Accounts WHERE id = ?", (account_id,))
    conn.commit()

    print(f"Bank account with ID {account_id} has been successfully deleted.")


def activate_accounts():
    # Ensure the admin performing the action is active and get their role
    cursor.execute("SELECT status, role FROM Admin WHERE id = ?", (current_user_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You are not authorized to perform this action or your account is inactive.")
        return

    role = input("Enter the type of account to activate (Admin/User/Bank Account): ").strip().lower()
    account_id = input(f"Enter the {role.capitalize()} ID to activate: ")

    if role == 'admin':
        # Check if the current admin has super privileges
        if admin[1] != 'super':
            print("Only super admins are allowed to activate other admin accounts.")
            return

        cursor.execute('SELECT status FROM Admin WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'active':
            confirmation = input(f"Are you sure you want to activate admin {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Admin
                    SET status = 'active'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Admin account {account_id} has been activated.")
            else:
                print("Action canceled.")
        else:
            print(f"Admin account {account_id} is already active or does not exist.")

    elif role == 'user':
        cursor.execute('SELECT account_status FROM Users WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'active':
            confirmation = input(f"Are you sure you want to activate user {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Users
                    SET account_status = 'active'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"User account {account_id} has been activated.")
            else:
                print("Action canceled.")
        else:
            print(f"User account {account_id} is already active or does not exist.")

    elif role == 'bank account' or role == 'bank':
        cursor.execute('SELECT account_status FROM Bank_Accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'active':
            confirmation = input(
                f"Are you sure you want to activate bank account {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Bank_Accounts
                    SET account_status = 'active'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Bank account {account_id} has been activated.")
            else:
                print("Action canceled.")
        else:
            print(f"Bank account {account_id} is already active or does not exist.")

    else:
        print("Invalid account type. Please enter 'Admin', 'User', or 'Bank Account'.")


def deactivate_accounts():
    # Ensure the admin performing the action is active and get their role
    cursor.execute("SELECT status, role FROM Admin WHERE id = ?", (current_user_id,))
    admin = cursor.fetchone()

    if not admin or admin[0] != 'active':
        print("You are not authorized to perform this action or your account is inactive.")
        return

    role = input("Enter the type of account to deactivate (Admin/User/Bank Account): ").strip().lower()
    account_id = input(f"Enter the {role.capitalize()} ID to deactivate: ")

    if role == 'admin':
        # Check if the current admin has super privileges
        if admin[1] != 'super':
            print("Only super admins are allowed to deactivate other admin accounts.")
            return

        cursor.execute('SELECT status FROM Admin WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'inactive':
            confirmation = input(f"Are you sure you want to deactivate admin {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Admin
                    SET status = 'inactive'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Admin account {account_id} has been deactivated.")
            else:
                print("Action canceled.")
        else:
            print(f"Admin account {account_id} is already inactive or does not exist.")

    elif role == 'user':
        cursor.execute('SELECT account_status FROM Users WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'inactive':
            confirmation = input(f"Are you sure you want to deactivate user {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Users
                    SET account_status = 'inactive'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"User account {account_id} has been deactivated.")
            else:
                print("Action canceled.")
        else:
            print(f"User account {account_id} is already inactive or does not exist.")

    elif role == 'bank account' or role == 'bank':
        cursor.execute('SELECT account_status FROM Bank_Accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()

        if account and account[0] != 'inactive':
            confirmation = input(
                f"Are you sure you want to deactivate bank account {account_id}? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                cursor.execute('''
                    UPDATE Bank_Accounts
                    SET account_status = 'inactive'
                    WHERE id = ?
                ''', (account_id,))
                conn.commit()
                print(f"Bank account {account_id} has been deactivated.")
            else:
                print("Action canceled.")
        else:
            print(f"Bank account {account_id} is already inactive or does not exist.")

    else:
        print("Invalid account type. Please enter 'Admin', 'User', or 'Bank Account'.")


def manage_password():
    cursor.execute("SELECT role, status FROM Admin WHERE id = ?", (current_user_id,))
    user_role = cursor.fetchall()

    if user_role[0][1] != 'inactive':

        choice = input("Do you want to change or reset the password: ")
        if choice == 'reset':
            choice = input("Enter the user id of the account you want to reset: ")
            if user_role[0][0] == 'super':

                while True:
                    new_password = input("Enter your new password: ")
                    confirm_password = input("Re-enter your password: ")
                    print(choice)
                    if new_password != confirm_password:
                        print("Passwords do not match")
                    else:
                        if choice[:2] == 'US':
                            cursor.execute("""UPDATE Users SET password = ? Where id = ?"""
                                           , (new_password, choice,))
                            print("Password reset successfully")
                            break
                        elif choice[:2] == 'AD':
                            cursor.execute("""UPDATE Admin SET password = ? where id = ?"""
                                           , (new_password, choice))
                            print("Password reset successfully")
                            break
            elif user_role[0][0] == 'management':
                while True:
                    if choice[:2] == 'AD':
                        print("You dont have the authority to change another admins password")
                        break

                    elif choice[:2] == 'US':
                        while True:
                            new_password = input("Enter your new password: ")
                            confirm_password = input("Re-enter your password: ")
                            if new_password != confirm_password:
                                print("Passwords do not match")
                            else:
                                cursor.execute("""UPDATE Users SET password = ? Where id = ?"""
                                               , (new_password, choice,))
                                print("Password reset successfully")
                                break
        elif choice == 'change':
            user_account = input("Which account do you want to update (user/admin): ").capitalize()
            # Check if the user is super admin and account is 'admin'
            if user_role[0][0] == 'super' and user_account == 'Admin':
                user_id = input("Enter the user id of the admin account: ")
                cursor.execute("SELECT password FROM Admin WHERE id = ?", (user_id,))
                password = cursor.fetchone()
                if password:
                    # Prompt for the current password to validate
                    current_password = input("Enter the current password of the admin account: ")
                    if current_password == password[0]:
                        # Prompt for the new password
                        new_password = input("Enter the new password: ")
                        confirm_password = input("Re-enter the password: ")
                        # Check if the new password matches the confirmation
                        if confirm_password != new_password:
                            print("Password mismatch!")
                        else:
                            # Update the admin's password in the database
                            cursor.execute("UPDATE Admin SET password = ? WHERE id = ?", (new_password, user_id))
                            conn.commit()
                            print("Admin password changed successfully.")
                    else:
                        print("Current password is incorrect.")
                else:
                    print(f"Admin with id {user_id} not found.")
            # Check if the user is a super admin or management admin and the account is 'user'
            elif (user_role[0][0] == 'super' or user_role[0][0] == 'management') and user_account == 'User':
                user_id = input("Enter the user id of the user account: ")
                cursor.execute("SELECT password FROM Users WHERE id = ?", (user_id,))
                password = cursor.fetchone()
                if password:
                    # Prompt for the current password to validate
                    current_password = input("Enter the current password of the user account: ")
                    if current_password == password[0]:
                        # Prompt for the new password
                        new_password = input("Enter the new password: ")
                        confirm_password = input("Re-enter the password: ")
                        # Check if the new password matches the confirmation
                        if confirm_password != new_password:
                            print("Password mismatch!")
                        else:
                            # Update the user's password in the database
                            cursor.execute("UPDATE Users SET password = ? WHERE id = ?", (new_password, user_id))
                            conn.commit()
                            print("User password changed successfully.")
                    else:
                        print("Current password is incorrect.")
                else:
                    print(f"User with id {user_id} not found.")
            else:
                print("You do not have the permission to change this account.")
        else:
            print("Invalid Choice")
    else:
        print("you cant update password because your account is inactive")
    conn.commit()


def approve_or_reject_loan():
    """
    Allows the admin to approve or reject a loan.
    """
    view_table.fetch_loans()
    loan_id = input("Enter the loan ID to process: ")
    account = input("Enter the account to credit: ")

    cursor.execute('''
            SELECT loan_id, user_id, loan_amount, loan_status, loan_type, date_approved, loan_balance
            FROM Loans WHERE loan_id =?
        ''', loan_id)
    loan = cursor.fetchone()

    if not loan:
        print("Invalid loan ID. Please enter a valid loan ID.")
        return

    loan_id, account_id, loan_amount, loan_status, loan_type, date_approved, loan_balance = loan

    # Ensure that date_applied and date_approved are in the correct format

    if loan_status != "Pending":
        print(f"Loan {loan_id} has already been processed. Current status: {loan_status}")
        return

    print(f"Loan ID: {loan_id}, Account ID: {account_id}, Loan Amount: {loan_amount}, Status: {loan_status}")
    decision = input("Approve or Reject loan? (A/R): ").strip().upper()

    if decision == "A":
        # Approve the loan
        date_approved = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update loan status and loan balance
        cursor.execute('''
            UPDATE Loans
            SET loan_status = 'Approved', date_approved = ?, loan_balance = ?
            WHERE loan_id = ?
        ''', (date_approved, loan_balance, loan_id))

        # Add loan amount to the account balance
        cursor.execute('''UPDATE Bank_Accounts SET balance = balance + ? WHERE id = ?''',
                       (loan_amount, account))

        conn.commit()
        print(f"Loan {loan_id} approved. Amount {loan_amount} has been credited to account {account_id}.")
    elif decision == "R":
        # Reject the loan
        cursor.execute('''
            UPDATE Loans
            SET loan_status = 'Rejected'
            WHERE loan_id = ?
        ''', (loan_id,))

        conn.commit()
        print(f"Loan {loan_id} has been rejected.")
    else:
        print("Invalid input. Please enter 'A' to approve or 'R' to reject.")

    print(loan)


# Start the program
login_menu()

# Close the database connection
conn.close()
