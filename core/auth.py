#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, session, url_for
from functools import wraps
import json

from core import db_user, db_connect

def is_public_route():
    public_routes = ['/login', '/register', '/static']
    return request.path.startswith(tuple(public_routes))

#login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_public_route():
            return f(*args, **kwargs)
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def do_register(request):
    if request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not all([firstname, name, email, password]):
            return render_template('register.html', status='error')
            
        if len(password) < 8:
            return render_template('register.html', status='error')

        result = db_user.create_user(firstname, name, email, password)
        
        if 'error' in result:
            return render_template('register.html', status='error')
            
        return redirect(url_for('login'))
    
    return render_template('register.html')


def do_login(request):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        status = db_user.check_password(email,password)

        if status['status'] == 'ok':
            data = json.loads(status['user'])
            session['user_email'] = data['email']
            session['user_fn'] = data['firstname']
            session['user_ln'] = data['name']
            session['user_name'] = data['firstname'] + ' ' + data['name']
            session['user_role'] = data['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', status='error')
    else:
        return render_template('login.html')

def do_logout():
    if 'user_email' in session:
            session.pop('user_email')
    return redirect(url_for('login'))
