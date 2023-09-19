from icecream import ic
import bcrypt


# User registration: Hash the user's password
def hash_password(password: str):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hash


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


# Example usage:
if __name__ == "__main__":
    # Get the user's password from user input (you may use a secure method to do this)
    user_password = input("Enter your password: ")

    # Hash the password before storing it in the database
    hashed_password = hash_password(user_password)
    ic(hashed_password)
    # Now, you can store `hashed_password` in your database along with the salt used.
    # When checking a login attempt, you will retrieve the salt associated with the user
    # and use bcrypt to verify the entered password against the stored hash.

    # For example, if you retrieve the stored salt as `stored_salt`:
    password = input("Enter your password for login: ")
    if check_password(password, hashed_password):
        print("Login successful")
    else:
        print("Login failed")
