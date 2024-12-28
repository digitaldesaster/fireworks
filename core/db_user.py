#!/usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from core.db_document import *
from flask_login import UserMixin
import logging
from mongoengine.errors import NotUniqueError, ValidationError, OperationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Document, UserMixin):
    firstname = StringField(required=True)
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    pw_hash = StringField(required=True)
    role = StringField(required=True, default='user')

    def get_id(self):
        return str(self.email)

def hash_password(password):
    return generate_password_hash(password)

def check_password(email, password):
    try:
        user = User.objects(email=email).first()
        if user and check_password_hash(user.pw_hash, password):
            return {'status': 'ok', 'message': 'successfully logged in', 'user': user.to_json()}
        return {'status': 'error', 'message': 'Invalid email or password'}
    except Exception as e:
        logger.error(f"Error checking password for {email}: {str(e)}")
        return {'status': 'error', 'message': 'Authentication error occurred'}

def create_user(firstname, name, email, password, role='user'):
    try:
        # Check if user exists first
        if User.objects(email=email).first():
            return {'error': 'user exists'}

        # Create new user
        user = User(
            firstname=firstname,
            name=name,
            email=email,
            pw_hash=hash_password(password),
            role=role
        )
        user.save()
        logger.info(f"User created successfully: {email}")
        return {'ok': 'user created', 'id': str(user.id)}

    except ValidationError as e:
        logger.error(f"Validation error creating user {email}: {str(e)}")
        return {'error': 'Invalid user data provided'}
    except NotUniqueError as e:
        logger.error(f"Duplicate email error for {email}")
        return {'error': 'user exists'}
    except OperationError as e:
        logger.error(f"Database operation error creating user {email}: {str(e)}")
        return {'error': 'Database error occurred'}
    except Exception as e:
        logger.error(f"Unexpected error creating user {email}: {str(e)}")
        return {'error': 'An unexpected error occurred'}

def delete_user(email, password):
    try:
        user = User.objects(email=email).first()
        if not user:
            return {'error': 'user does not exist'}
        
        if not check_password_hash(user.pw_hash, password):
            return {'error': 'incorrect password'}
        
        user.delete()
        logger.info(f"User deleted successfully: {email}")
        return {'ok': 'deleted'}
    except Exception as e:
        logger.error(f"Error deleting user {email}: {str(e)}")
        return {'error': 'Failed to delete user'}

def update_password(email, password, new_password):
    try:
        user = User.objects(email=email).first()
        if not user:
            return {'error': 'user does not exist'}

        if not check_password_hash(user.pw_hash, password):
            return {'error': 'incorrect password'}

        user.pw_hash = hash_password(new_password)
        user.save()
        logger.info(f"Password updated successfully for user: {email}")
        return {'ok': 'password updated'}
    except ValidationError as e:
        logger.error(f"Validation error updating password for {email}: {str(e)}")
        return {'error': 'Invalid password format'}
    except Exception as e:
        logger.error(f"Error updating password for {email}: {str(e)}")
        return {'error': 'Failed to update password'}

# for i in range(1, 101):
#     username = f"User{i}"
#     name = f"Name{i}"
#     email = f"user{i}.name@gmail.com"
#     password = '12345'

#     # Create user with generated data
#     create_user(username, name, email, password, role='user')

#print (check_password('alexander.fillips@gmail.com','Standard!!'))


#create_user('Alex', 'Fillips', 'alexander.fillips@gmail.com', 'Standard!!',role = 'admin')

#for user in User.objects():
#	print (user.to_json())
