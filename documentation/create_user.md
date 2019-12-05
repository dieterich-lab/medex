# Create user
To login in the app (e.g. http://127.0.0.1:5000/login), users have to be created in Redis.
For creating a user, use script `user_management.py`. 
Run the following command:

```python user_management.py create_user kate@a.a 123```

# Delete user

To delete user from Redis, run the command:

```python user_management.py delete_user kate@a.a```

# Create users from a file
To implement: multiline input file, where each line contains username and password to create

# Forgot password
To implement: send an email to reset a password

 
