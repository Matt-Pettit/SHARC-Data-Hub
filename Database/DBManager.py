import os
import csv
import sqlite3

# Set the directory where the CSV files are located
csv_dir = './'

# Create a new SQLite database file
db_file = 'Database/combined_data.db'
conn = sqlite3.connect(db_file)
c = conn.cursor()

def display_table_data(table_name):
    """Display the data in the given table."""
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    
    # Get the column names
    c.execute(f"PRAGMA table_info({table_name})")
    column_names = [row[1] for row in c.fetchall()]
    
    # Print the column names
    print(f"Data for table '{table_name}':")
    print(", ".join(column_names))
    
    # Print the data rows
    for row in rows:
        print(", ".join(str(item) for item in row))
    print()

def add_data_to_table(table_name):
    """Prompt the user to enter data and add it to the given table."""
    # Get the column names
    c.execute(f"PRAGMA table_info({table_name})")
    column_names = [row[1] for row in c.fetchall()]
    
    # Prompt the user for input
    print(f"Adding data to table '{table_name}':")
    values = []
    for column_name in column_names:
        value = input(f"Enter value for '{column_name}': ")
        values.append(value)
    
    # Insert the data into the table
    insert_query = f"INSERT INTO {table_name} VALUES ({','.join('?' for _ in range(len(values)))})"
    c.execute(insert_query, values)
    conn.commit()
    print("Data added successfully.")
    print()

def clear_table_data(table_name):
    """Clears all data from the specified table."""
    c.execute(f"DELETE FROM {table_name}")
    conn.commit()
    print(f"All data cleared from table '{table_name}'")

# Loop through the tables in the database and display the data
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = [row[0] for row in c.fetchall()]

for table_name in table_names:
    display_table_data(table_name)

# Prompt the user to edit any tables
while True:
    edit_tables = input("Do you want to edit any tables? (y/n) ").lower()
    if edit_tables == 'n':
        break
    elif edit_tables == 'y':
        print("Available tables:")
        for table_name in table_names:
            print(f"- {table_name}")
        table_to_edit = input("Enter the name of the table you want to edit: ")
        if table_to_edit in table_names:
            action = input("Do you want to add data or clear the table? (add/clear) ").lower()
            if action == 'add':
                add_data_to_table(table_to_edit)
            elif action == 'clear':
                clear_table_data(table_to_edit)
            else:
                print("Invalid action. Please enter 'add' or 'clear'.")
        else:
            print(f"Table '{table_to_edit}' does not exist.")
    else:
        print("Invalid input. Please enter 'y' or 'n'.")

# Close the database connection
conn.close()
