from typing_extensions import Annotated     # for adding help arguments to the respective cli command functions
import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command(help = "Initializes the database and creates a default user 'bob'")
def initialize():                   # initializes the database with a default user "bob"
    with get_session() as db:       # gets a connection to the database
        drop_all()                  # deletes all tables
        create_db_and_tables()      # recreates all tables
        bob = User('bob', 'bob@mail.com', 'bobpass')    # creates a new user (in memory)
        db.add(bob)                 # tells the database about this new data
        db.commit()                 # tells the database persist the data
        db.refresh(bob)             # updates the user (we use this to get the ID from the db)
        print("Database Initialized")


# TASK 5.1
@cli.command(help = "Retrieves and prints a user by the given username from the database")
# def get_user(username:str):       # retrieves and prints a user by a given username from the database
def get_user(username: Annotated[str, typer.Argument(help = "Username of the user to search for in the database")]):
    with get_session() as db:       # gets a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()   # searches the database for the user by the given username
        if not user:                # if the user is not found
            print(f'{username} not found!')     # prints a message
            return                  # exits the function
        print(user)                 # else the user details are printed when found


# TASK 5.2
@cli.command(help = "Retrieves and prints all users from the database")
def get_all_users():                # retrieves and prints all users from the database
    with get_session() as db:       # gets a connection to the database
        all_users = db.exec(select(User)).all()     # retrieves all users from the database
        if not all_users:           # if no users are found
            print('No users found!')    # prints a message
            return                  # exits the function
        else:
            for user in all_users:  # else it iterates through all users in the database
                print(user)         # and prints each user's details


# TASK 6 
@cli.command(help = "Updates a user's email by the given username")
# def change_email(username: str, new_email:str):   # updates a user's email by a given username
def change_email(username: Annotated[str, typer.Argument(help = "The username of the user whose email is to be updated")],                 
                 new_email: Annotated[str, typer.Argument(help = "The new email address to update for the user")]):
    with get_session() as db:                       # gets a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()       # searches the database for the user by the given username
        if not user:                                # if the user is not found  
            print(f'{username} not found! Unable to update email.')     # prints a message
            return                                  # exits the function
        user.email = new_email                      # else the user's email is to be updated
        db.add(user)                                # updates the database with the new email
        db.commit()                                 # changes are committed to the database 
        print(f"Updated {user.username}'s email to {user.email}")   # prints a confirmation message


# TASK 7
@cli.command(help = "Creates a new user with the given username, email, and password and adds details to the database")
def create_user(username: Annotated[str, typer.Argument(help = "The username of the new user to be created")], 
                email: Annotated[str, typer.Argument(help = "The email address of the new user to be created")], 
                password: Annotated[str, typer.Argument(help = "The password of the new user to be created")]):   
    # creates a new user with the given username, email, and password
    with get_session() as db:       # gets a connection to the database
        newuser = User(username, email, password)           # creates a new user object in memory
        try:                        # tries to add the new user to the database
            db.add(newuser)         # updates the database with the new user details
            db.commit()             # changes are committed to the database
        except IntegrityError as e: # catches the error if the username or email already exists in the database
            db.rollback()                   # lets the database undo any previous steps of a transaction
            print(e.orig)                   # optionally prints the error raised by the database
            print("Username or email already taken!")       # prints an error message
        else:
            print(newuser)          # else prints the new user's details if successfully created


# TASK 8
@cli.command(help = "Deletes a user by the given username from the database")
# def delete_user(username: str):       # deletes a user by a given username
def delete_user(username: Annotated[str, typer.Argument(help = "The username of the user to be deleted from the database")]):
    with get_session() as db:           # gets a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()       # searches the database for the user by the given username
        if not user:                    # if the user is not found, prints an error message and exits the function
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)                 # else the user is deleted from the database
        db.commit()                     # changes are committed to the database
        print(f'User {username} deleted successfully.')     # prints a confirmation message


# EXERCISE 1
@cli.command(help = "Finds and prints users whose username or email contains the given partial string")
# def find_user_partial(partial: str):
def find_user_partial(partial: Annotated[str, typer.Argument(help = "The partial string to search for in usernames and emails in the database")]):
    with get_session() as db:           # gets a connection to the database
        # searches the database for users whose username or email contains the given partial string
        users = db.exec(select(User).where((User.username.contains(partial)) | (User.email.contains(partial)) )).all()
        if not users:                   # if no users are found matching the partial string
            print(f'No users found matching "{partial}"')       # prints an error message
            return                      # exits the function
        for user in users:              # else it iterates through all matching users and prints each user details from the database
            print(user)


# EXERCISE 2
@cli.command(help = "Lists users from the database by a paginated table using limit and offset values")
# def list_users(limit: int = 10, offset: int = 0):
def list_users(limit: Annotated[int, typer.Argument(help = "The maximum number of users to retrieve from the database", min=1)] = 10, 
               offset: Annotated[int, typer.Argument(help = "The number of users to skip before starting to collect the result set", min=0)] = 0):
    with get_session() as db:           # gets a connection to the database
        users = db.exec(select(User).offset(offset).limit(limit)).all()         # applies offset and limit in order to paginate the results
        if not users:                   # if no users are found in the specified range
            print('No users found!')    # prints an error message and exits the function
            return
        for user in users:              # else it iterates through all retrieved users from the database and prints each user details from the database
            print(user)


# EXERCISE 3
# modified all functions with help statements for all arguments and commands
# added comments as documentation explaining each line of each function

if __name__ == "__main__":
    cli()