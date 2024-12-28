#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, session, url_for
from functools import wraps
import json
from flask_login import login_user, logout_user, login_required, current_user
from core import db_user, db_connect
from datetime import timedelta

def is_public_route():
    public_routes = ['/login', '/register', '/static']
    return request.path.startswith(tuple(public_routes))

def do_register(request):
    if request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not all([firstname, name, email, password]):
            return render_template('register.html', status='error', 
                                error_message='All fields are required')
            
        if len(password) < 8:
            return render_template('register.html', status='error',
                                error_message='Password must be at least 8 characters')

        result = db_user.create_user(firstname, name, email, password)
        
        if 'error' in result:
            error_message = 'Email already exists' if result['error'] == 'user exists' else 'Registration failed'
            return render_template('register.html', status='error',
                                error_message=error_message)
            
        return redirect(url_for('login'))
    
    return render_template('register.html')

def do_login(request):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form

        status = db_user.check_password(email, password)

        if status['status'] == 'ok':
            user = db_user.User.objects(email=email).first()
            login_user(user, remember=remember, duration=timedelta(days=30) if remember else None)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', status='error')
    else:
        return render_template('login.html')

def do_logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))
