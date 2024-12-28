#!/usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, \
     check_password_hash

from core.db_document import *
from flask_login import UserMixin

class User(Document, UserMixin):
    firstname = StringField()
    name = StringField()
    email = StringField()
    pw_hash = StringField()
    role = StringField()

    def get_id(self):
        return str(self.email)

def hash_password(password):
    return (generate_password_hash(password))

def check_password(email, password):
    user = User.objects(email = email).first()
    if user !=None:
        if check_password_hash(user.pw_hash, password):
            return {'status':'ok','message' : 'successfully logged in','user' : user.to_json()}
    return {'status':'error','message' : 'user not found'}

def create_user(firstname, name, email, password,role = 'user'):
    try:
        User.objects.get(email = email)
        return {'error' : 'user exists'}
    except DoesNotExist:
        user = User(firstname = firstname, name = name,email = email, pw_hash = hash_password(password), role = role)
        try:
            user.save()
            return {'ok' : 'user created', 'id' : user.id}
        except:
            return {'error' : 'user not created'}
def delete_user(email,password):
    user = User.objects(email = email).first()
    if user != None:
        if check_password_hash(user.pw_hash, password):
            user.delete()
            return {'ok' : 'deleted'}
        else:
            return {'error' : 'password false'}
    else:
        return {'error' : 'user does not exists'}
def update_password(email,password,new_password):
    try:
        user = User.objects.get(email = email)
        if check_password_hash(user.pw_hash, password):
            user.pw_hash =  hash_password(new_password)
            user.save()
            return {'ok' : 'password updated'}
        else:
            return {'error' : 'password false'}

    except:
        return {'error' : 'user does not exists'}

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
