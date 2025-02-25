#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from mongoengine import *
from dotenv import load_dotenv
import certifi

# Load environment variables from .env file
load_dotenv()

# Retrieve your MongoDB password from an environment variable
mongodb_pwd = os.getenv('MONGODB_PWD')
mongodb_user = os.getenv('MONGODB_USER')
mongodb_uri = os.getenv('MONGODB_URI')

# Connect to your MongoDB database with SSL certificate verification
#connect(host=mongodb_uri, tlsCAFile=certifi.where())
connect(host=mongodb_uri)

# class User(DynamicDocument):
#   user_name = StringField()
#   email = StringField(required=True)

# user = User(user_name="John Doe", email="mynbi@example.com")

# user.save()