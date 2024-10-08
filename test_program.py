import sqlite3
from datetime import datetime

# Assuming you have established a connection and cursor
conn = sqlite3.connect('bank_application.db')
cursor = conn.cursor()

Security_Question = [
    "What is your pet's name?",
    "What school did you go to?",
    "Where were you born?",
    "What is your last name?"
]
current_user_id = None  # Global variable to hold the currently logged-in user ID


def check_credentials(table_name, user_id, password):
    cursor.execute(f"SELECT id, password FROM {table_name} WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    return user and user[1] == password  # Return True if credentials are valid


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
            # admin_menu()  # Redirect to admin menu
        # Check if the user is a normal user
        elif check_credentials("Users", user_id, password):
            print("\nLogin successful as User!")
            current_user_id = user_id  # Store the logged-in user ID
            user_menu()  # Redirect to user menu
        else:
            print("\nInvalid ID or password. Please try again.")


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
    cursor.execute("SELECT id FROM Bank_Accounts WHERE account_holder = ? AND account_status = 'active'", (current_user_id,))
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
    cursor.execute("SELECT loan_id, loan_balance FROM Loans WHERE user_id = ? AND loan_status = 'Approved'", (current_user_id,))
    loan = cursor.fetchone()

    if not loan:
        print("You do not have any approved loans to repay.")
        return

    loan_id, loan_balance = loan

    # Step 2: Check if the user has any active bank accounts
    cursor.execute("SELECT id, balance FROM Bank_Accounts WHERE account_holder = ? AND account_status = 'active'", (current_user_id,))
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


def user_menu():
    """
    Menu for normal users.
    """
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
            print("View accounts... ")
            fetch_user_bank_account()
            # Add logic to view accounts using current_user_id
        elif choice == '2':
            fields = []
            values = []
            users_table = ["name", "email", "contact_info", "account_status", "preferred_language", "security_question",
                           "security_answer"]

            for index, column in enumerate(users_table, start=1):
                print(f"{index}. {column}")
            field_choice = int(input(f"Enter the field to update: "))
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
            # Add logic to update profile using current_user_id
            update_accounts("Users", current_user_id, fields, values)
        elif choice == '3':
            print("Withdraw funds... ")
            withdraw_funds()
            # Add logic to withdraw funds using current_user_id
        elif choice == '4':
            print("Send money... ")
            send_money()
            # Add logic to send money using current_user_id
        elif choice == '5':
            print("Deposit funds... ")
            deposit_funds()
            # Add logic to transfer funds using current_user_id
        elif choice == '6':
            print("Apply for a loan... ")
            apply_for_loan()
            # Add logic to apply for a loan using current_user_id
        elif choice == '7':
            print("Repay loan... ")
            repay_loan()
            # Add logic to repay loan using current_user_id
        elif choice == '8':
            print("Goodbye!")
            break

        else:
            print("Invalid choice! Please pick again.")


# Example usage of the login system
login_menu()
