#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import mysql.connector
import re

# MySQL connection
try:
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="enter password",
        database="db_name"
    )
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# cursor to interact with the database
cursor = db_connection.cursor()

# Set of valid platform names in lowercase
VALID_PLATFORMS = {"twitter", "whatsapp", "instagram", "linkedin"}

# Creating the User table if not exists
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# Creating the SocialMediaAccounts table if not exists
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_media_accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            platform VARCHAR(255) NOT NULL,
            account_name VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# Creating the Posts table if not exists
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            content TEXT,
            platform VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# Function to register a new user
def register_user():
    print("User Registration:")
    username = input("Enter your username: ")
    
    # Email validation loop
    while True:
        email = input("Enter your email: ")
        # Check if the email contains an '@' symbol
        if re.search("@", email):
            break
        else:
            print("Invalid email. Please enter a valid email address.")

    password = input("Enter your password: ")

    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        db_connection.commit()
        print("Registration successful!\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db_connection.rollback()

# Function to log in a user
def login_user():
    print("User Login:")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()

        if user_data:
            current_user = {'id': user_data[0], 'username': user_data[1], 'email': user_data[2]}
            print("Login successful!\n")
            return current_user
        else:
            print("Invalid credentials. Please try again.\n")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to display the user's dashboard
def display_dashboard(user):
    print("Dashboard:")
    
    try:
        # Displaying connected social media accounts
        cursor.execute("SELECT * FROM social_media_accounts WHERE user_id = %s", (user['id'],))
        accounts = cursor.fetchall()
        if accounts:
            print("Connected Social Media Accounts:")
            for account in accounts:
                # Display standardized platform name
                print(f"{account[2].capitalize()} on {account[3]}")  # Displaying account name on platform
        else:
            print("No connected social media accounts.")

        # Displaying basic account information
        print("\nBasic Account Information:")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to create a post
def create_post(user, content):
    print("Post Creation:")
    
    try:
        platforms = []
        while True:
            platform = input("Enter the platform (e.g., Twitter, WhatsApp, Instagram, LinkedIn): ")
            # Validate platform against the set of valid platforms 
            if platform.lower() not in VALID_PLATFORMS:
                print(f"Invalid platform: {platform}. Allowed platforms are {', '.join(VALID_PLATFORMS)}")
                continue

            platforms.append(platform.lower())  # Convert platform to lowercase

            another_platform = input("Do you want to add another platform? (yes/no): ")
            if another_platform.lower() != "yes":
                break

        # Construct the parameterized SQL statement
        sql = "INSERT INTO posts (user_id, content, platform) VALUES (%s, %s, %s)"
        
        # Construct the parameterized values for each platform
        values = [(user['id'], content, platform) for platform in platforms]

        # Initialize the cursor outside the try block
        with db_connection.cursor() as cursor:
            # Execute the SQL statement with multiple values
            cursor.executemany(sql, values)

        db_connection.commit()  # Commit changes to the database
        print("Post created successfully!\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db_connection.rollback()

# Function to delete a post
def delete_post(user):
    print("Post Deletion:")
    try:
        cursor.execute("SELECT * FROM posts WHERE user_id = %s", (user['id'],))
        user_posts = cursor.fetchall()

        if not user_posts:
            print("No posts to delete.")
        else:
            print("Your Posts:")
            for i, post in enumerate(user_posts, start=1):
                # Display standardized platform name
                print(f"{i}. {post[2]} on {post[3].capitalize()}")  # Displaying post content on platform

            post_index = int(input("Enter the number of the post to delete: ")) - 1

            if 0 <= post_index < len(user_posts):
                deleted_post_id = user_posts[post_index][0]
                cursor.execute("DELETE FROM posts WHERE id = %s", (deleted_post_id,))
                db_connection.commit()
                print("Post deleted successfully!\n")
            else:
                print("Invalid post number. Please try again.\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to view posts
def view_posts_by_platform(user):
    print("Viewing Posts by Platform:")

    try:
        cursor.execute("SELECT platform, content FROM posts WHERE user_id = %s", (user['id'],))
        posts = cursor.fetchall()

        if not posts:
            print("No posts available.")
        else:
            platforms = set(post[0] for post in posts)  # Get unique platforms
            for platform in platforms:
                print(f"\nPosts on {platform.capitalize()}:")  # Display standardized platform name
                for post in posts:
                    if post[0] == platform:
                        print(f"- {post[1]}")
            print("\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to connect a social media account
def connect_social_media_account_with_keyword_arguments(user, platform, account_name, **kwargs):
    print("Connect Social Media Account:")
    
    # Access additional information using kwargs
    age = kwargs.get('age', '')
    city = kwargs.get('city', '')

    if age and city:
        print(f"Additional Information: Age - {age}, City - {city}")

    # Validate platform against the set of valid platforms (case-insensitive)
    if platform.lower() not in VALID_PLATFORMS:
        print(f"Invalid platform: {platform}. Allowed platforms are {', '.join(VALID_PLATFORMS)}")
        return

    if not account_name:
        print("Invalid input. account_name is required.")
        return

    try:
        # Inserting social media account data into the 'social_media_accounts' table
        cursor.execute("INSERT INTO social_media_accounts (user_id, platform, account_name) VALUES (%s, %s, %s)",
                       (user['id'], platform.lower(), account_name))  # Convert platform to lowercase
        db_connection.commit()
        print("Account connected successfully!\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db_connection.rollback()

# Exit the program
def exit_program():
    print("Exiting the program. Goodbye!")
    sys.exit()

current_user = None

while True:
    print("Menu:")
    print("1. Register")
    print("2. Login")
    print("3. Display Dashboard")
    print("4. Create Post")
    print("5. Delete Post")
    print("6. View Posts")
    print("7. Connect Social Media Account (with Keyword Arguments)")
    print("8. Exit \n")

    choice = input("Enter your choice: ")

    if choice == "1":
        register_user()

    elif choice == "2":
        current_user = login_user()

    elif choice == "3":
        if current_user:
            display_dashboard(current_user)
        else:
            print("Please log in first.\n")

    elif choice == "4":
        if current_user:
            content = input("Enter your post: ")
            create_post(current_user, content)
        else:
            print("Please log in first.\n")

    elif choice == "5":
        if current_user:
            delete_post(current_user)
        else:
            print("Please log in first.\n")
            
    elif choice == "6":
        if current_user:
            view_posts_by_platform(current_user)
        else:
            print("Please log in first. \n")

    elif choice == "7":
        if current_user:
            platform = input("Enter the platform (e.g., Twitter, WhatsApp, Instagram, LinkedIn): ")
            account_name = input("Enter your account name on this platform: ")
            age = input("Enter your age: ")
            city = input("Enter your city: ")
            connect_social_media_account_with_keyword_arguments(current_user, platform, account_name, age=age, city=city)
        else:
            print("Please log in first.\n")

    elif choice == "8":
        exit_program()

    else:
        print("Invalid choice. Please enter a valid option.\n")

# Closing the database connection
try:
    cursor.close()
    db_connection.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)


# In[ ]:




