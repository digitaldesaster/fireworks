import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.db_user import create_user

for i in range(1, 20):
    username = f"User{i}"
    name = f"Name{i}"
    email = f"user{i}.name@gmail.com"
    password = '12345'

    # Create user with generated data
    create_user(username, name, email, password, role='user')