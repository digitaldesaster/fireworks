# app.py

```
from flask import Flask, render_template, request, session
from core import auth
from datetime import timedelta
import os
from flask_login import LoginManager, current_user, login_required
from core.db_user import User
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialize Flask-Login with proper session durations
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # For "Remember me"
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)    # For "Remember me"
app.config['REMEMBER_COOKIE_SECURE'] = False                   # Set to True in production with HTTPS
app.config['REMEMBER_COOKIE_HTTPONLY'] = True                  # No JavaScript access

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return User.objects(email=user_id).first()

@app.route('/register', methods=['GET', 'POST'])
def register():
	return auth.do_register(request)

@app.route('/login', methods=['GET', 'POST'])
def login():
	return auth.do_login(request)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	return auth.do_logout()

# Route for the home page
@app.route("/")
@app.route("/index")
@login_required
def index():
	return render_template("index.html")

if __name__ == '__main__':
	app.run(debug=True)

```

# tailwind.config.js

```
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./node_modules/flyonui/dist/js/*.js", // Added FlyonUI JS components path
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flyonui"),
    require("flyonui/plugin"), // For FlyonUI JS components
    require('tailwindcss-motion'), // Added motion plugin
  ],
  flyonui: {
    themes: ["light", "dark", "gourmet"],
  },
};

```

# templates

## ../templates/index.html

```
<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Flask App</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/output.css') }}"
    />
  </head>
  <body>
    <nav class="navbar rounded-box shadow">
      <div class="w-full flex items-center justify-between">
        <div class="navbar-start">
          <a
            class="link text-base-content/90 link-neutral text-xl font-semibold no-underline"
            href="#"
            >Flask</a
          >
        </div>
        <div class="navbar-end">
          <div
            class="dropdown relative inline-flex rtl:[--placement:bottom-end]"
          >
            <button
              id="dropdown-avatar"
              type="button"
              class="dropdown-toggle"
              aria-haspopup="menu"
              aria-expanded="false"
              aria-label="User menu"
            >
              <div class="avatar placeholder">
                <div class="bg-primary text-primary-content w-10 rounded-full">
                  <span class="text-sm font-bold"
                    >{{ current_user.firstname[0] }}{{ current_user.name[0]
                    }}</span
                  >
                </div>
              </div>
            </button>
            <ul
              class="dropdown-menu dropdown-open:opacity-100 hidden min-w-60"
              role="menu"
              aria-orientation="vertical"
              aria-labelledby="dropdown-avatar"
            >
              <li>
                <form
                  action="{{ url_for('logout') }}"
                  method="post"
                  class="w-full"
                >
                  <input
                    type="hidden"
                    name="csrf_token"
                    value="{{ csrf_token() }}"
                  />
                  <button type="submit" class="dropdown-item w-full text-left">
                    <span class="icon-[tabler--logout] size-5 shrink-0"></span>
                    Logout
                  </button>
                </form>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>

    <div class="container mx-auto px-4 py-12">
      <div class="card max-w-2xl mx-auto">
        <div class="card-body text-center">
          <h5 class="card-title mb-2.5">
            Welcome back, {{ current_user.firstname }} {{ current_user.name }}!
          </h5>
          <p class="mb-4">
            We're glad to see you again. Here's your personal dashboard
            overview.
          </p>
          <div class="card-actions">
            <button class="btn btn-primary">Learn More</button>
          </div>
        </div>
      </div>
    </div>

    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>

```

## ../templates/register.html

```
<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Register - Flask App</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/output.css') }}"
    />
  </head>
  <body class="bg-base-200 min-h-screen flex items-center justify-center">
    <div class="w-full max-w-md p-6">
      <div class="rounded-box border-base-content/10 bg-base-100 p-8 shadow-lg">
        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold text-base-content/90">
            Create Account
          </h1>
          <p class="text-base-content/60 mt-2">Please fill in your details</p>
        </div>

        {% if status == 'error' %}
        <div class="alert alert-error mb-4">
          <span>{{ error_message if error_message else 'Registration failed. Please check your input.' }}</span>
        </div>
        {% endif %}

        <form method="POST" action="{{ url_for('register') }}">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
          <div class="space-y-6">
            <div class="form-control">
              <label class="label" for="firstname">
                <span class="label-text">First Name</span>
              </label>
              <input
                type="text"
                id="firstname"
                name="firstname"
                class="input input-bordered w-full"
                required
                autocomplete="off"
              />
            </div>

            <div class="form-control">
              <label class="label" for="name">
                <span class="label-text">Last Name</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                class="input input-bordered w-full"
                required
                autocomplete="off"
              />
            </div>

            <div class="form-control">
              <label class="label" for="email">
                <span class="label-text">Email</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                class="input input-bordered w-full"
                placeholder="your@email.com"
                required
                autocomplete="off"
              />
            </div>

            <div class="form-control">
              <label class="label" for="password">
                <span class="label-text">Password (min. 8 characters)</span>
              </label>
              <input
                type="password"
                id="password"
                name="password"
                class="input input-bordered w-full"
                placeholder="••••••••"
                minlength="8"
                required
                autocomplete="new-password"
              />
            </div>

            <button type="submit" class="btn btn-primary w-full">
              Register
            </button>

            <div class="text-center">
              <a href="/login" class="link link-hover text-sm"
                >Already have an account? Sign in</a
              >
            </div>
          </div>
        </form>
      </div>
    </div>
    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>

```

## ../templates/login.html

```
<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login - Flask App</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/output.css') }}"
    />
  </head>
  <body class="bg-base-200 min-h-screen flex items-center justify-center">
    <div class="w-full max-w-md p-6">
      <div class="rounded-box border-base-content/10 bg-base-100 p-8 shadow-lg">
        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold text-base-content/90">Welcome Back</h1>
          <p class="text-base-content/60 mt-2">Please sign in to continue</p>
        </div>

        <form method="POST" action="{{ url_for('login') }}" autocomplete="on">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
          <div class="space-y-6">
            <div class="form-control">
              <label class="label" for="email">
                <span class="label-text">Email</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                class="input input-bordered w-full"
                placeholder="your@email.com"
                value="{{ email if email }}"
                required
                autocomplete="email"
              />
            </div>

            <div class="form-control">
              <label class="label" for="password">
                <span class="label-text">Password</span>
              </label>
              <input
                type="password"
                id="password"
                name="password"
                class="input input-bordered w-full"
                placeholder="••••••••"
                required
                autocomplete="current-password"
              />
              <label class="label">
                <a href="#" class="label-text-alt link link-hover"
                  >Forgot password?</a
                >
              </label>
            </div>

            <div class="form-control">
              <label class="label cursor-pointer justify-start gap-3">
                <input
                  type="checkbox"
                  class="checkbox checkbox-primary"
                  name="remember"
                />
                <span class="label-text">Remember me</span>
              </label>
            </div>

            {% if status == 'error' %}
            <div class="alert alert-error">
              <span>Invalid email or password</span>
            </div>
            {% endif %}

            <button type="submit" class="btn btn-primary w-full">
              Sign in
            </button>

            <div class="text-center">
              <a href="/register" class="link link-hover text-sm"
                >Don't have an account? Register</a
              >
            </div>
          </div>
        </form>
      </div>
    </div>
    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>

```

# core

## ../core/auth.py

```
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

```

## ../core/db_user.py

```
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

```

## ../core/__init__.py

```
# This file can be empty, it just marks the directory as a Python package 
```

## ../core/db_document.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from bson import json_util

#Date Fields must be named name_date, e.g. contact_date
#This is to make sure that string dates like 01.01.2016 are saved as date objects
#functions to convert strings to date objects are in crud.py (create / update)

#every document needs a required name field !!!

#converts mongo to Json and formats _date properly
def mongoToJson(document):
    data = document.to_mongo()
    #format all _date fields

    for key,value in data.items():
        if key.find('_date') !=-1:
            try:
                #print data[key]
                data[key] = document[key].strftime('%d.%m.%Y %H:%M')
                #print data[key]
            except:
                pass
        elif key.find('filter') !=-1:
            try:
                i=0
                for filter in document[key]:
                    if '_date' in filter['field']:
                        data[key][i]['value'] = document[key][i]['value'].strftime('%d.%m.%Y')
                    i=i+1
            except:
                pass

    return json_util.dumps(data)

class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))

class User(DynamicDocument):
    email = StringField(required=True,min_length=1)
    salutation = StringField(default='')
    firstname = StringField(default='')
    name = StringField(default='')
    # comment = StringField(default='')
    # active = StringField(default='off')
    # newsletter = StringField(default='off')
    # event_date = DateField(default=None)
    # age_int = IntField(default=None) # required=True,min_length=4,unique=True
    # salary_float = FloatField(default=None)
    # ai_provider= StringField(default='')
    # user = StringField(default='')
    # files = StringField(default='')
    # more_files = StringField(default='')
    # link = StringField(default='')
    
    meta = {'queryset_class': CustomQuerySet}
    def searchFields(self):
        return ['email','firstname','name']
    def fields(self, list_order = False):
        email = {'name' :  'email', 'label' : 'Email', 'class' : '', 'type' : 'SingleLine', 'required' : True,'full_width':True}
        salutation = {'name' :  'salutation', 'label' : 'Anrede', 'class' : '', 'type' : 'SimpleListField','full_width':False}
        firstname = {'name' :  'firstname', 'label' : 'Vorname', 'class' : '', 'type' : 'SingleLine', 'full_width':False}
        name = {'name' :  'name', 'label' : 'Nachname', 'class' : '', 'type' : 'SingleLine','full_width':False}
        # comment = {'name' :  'comment', 'label' : 'Kommentar', 'class' : '', 'type' : 'MultiLine','full_width':True}
        # active = {'name' :  'active', 'label' : 'Aktiv', 'class' : '', 'type' : 'CheckBox', 'full_width':False}
        # newsletter = {'name' :  'newsletter', 'label' : 'Newsletter', 'class' : '', 'type' : 'CheckBox', 'full_width':False}
        # event_date = {'name' :  'event_date', 'label' : 'Event-Datum', 'class' : 'hidden-xs', 'type' : 'Date', 'full_width':False}
        # age_int = {'name' :  'age_int', 'label' : 'Alter', 'class' : 'hidden-xs', 'type' : 'IntField', 'full_width':False}
        # salary_float = {'name' :  'salary_float', 'label' : 'Gehalt', 'class' : 'hidden-xs', 'type' : 'FloatField', 'full_width':False}
        # ai_provider = {'name' :  'ai_provider', 'label' : 'Firma', 'class' : 'hidden-xs', 'type' : 'AdvancedListField', 'full_width':False}
        # user = {'name' :  'user', 'label' : 'User', 'class' : '', 'type' : 'DocumentField', 'full_width':False,'module' : 'user','document_field':'email'}
        # files = {'name' :  'files', 'label' : 'Files', 'class' : 'hidden-xs', 'type' : 'FileField','full_width':True}
        # more_files = {'name' :  'more_files', 'label' : 'More Files', 'class' : 'hidden-xs', 'type' : 'FileField','full_width':True}
        # link = {'name' :  'link', 'label' : 'Link', 'class' : '', 'type' : 'ButtonField','full_width':False,'link':'/d/user'}

        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [firstname,name,email]
        return [email,salutation,firstname,name]
    def to_json(self):
        return mongoToJson(self)

class File(DynamicDocument):
    name = StringField(required=True,min_length=4)
    meta = {'queryset_class': CustomQuerySet}
    def searchFields(self):
        return ['name']
    def fields(self, list_order = False):
        name = {'name' :  'name', 'label' : 'Name', 'class' : '', 'type' : 'SingleLine', 'required' : True,"full_width" : False}
        category = {'name' :  'category', 'label' : 'Kategorie', 'class' : 'hidden-xs', 'type' : 'TextField',"full_width" : False}
        document_id = {'name' :  'document_id', 'label' : 'Dokument', 'class' : 'hidden-xs', 'type' : 'TextField',"full_width" : True}

        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [name]
        return [name]
    def to_json(self):
        return mongoToJson(self)
class Filter(DynamicDocument):
    name = StringField(required=True,min_length=4)
    meta = {'queryset_class': CustomQuerySet}
    def searchFields(self):
        return ['name']
    def fields(self, list_order = False):
        name = {'name' :  'name', 'label' : 'Name', 'class' : '', 'type' : 'SingleLine', 'required' : True}
        category = {'name' :  'category', 'label' : 'Kategorie', 'class' : '', 'type' : 'SingleLine'}

        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [name, category]
        return [name, category]
    def to_json(self):
        return mongoToJson(self)

#AI Chat Bot Code
class Model(DynamicDocument):
    provider = StringField(required=True, min_length=1)
    model = StringField(required=True, min_length=1)
    name = StringField(required=True, min_length=1)

    meta = {'queryset_class': CustomQuerySet}

    def searchFields(self):
        return ['provider', 'model', 'name']

    def fields(self, list_order=False):
        provider = {'name': 'provider', 'label': 'Provider', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        model = {'name': 'model', 'label': 'Model', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}

        if list_order:
            return [name, provider, model]
        return [name, provider, model]

    def to_json(self):
        return mongoToJson(self)

class History(DynamicDocument):
    username = StringField()
    chat_started = IntField()
    messages = StringField()
    first_message = StringField()
    link = StringField(default='')
    def searchFields(self):
        return ['messages','first_message']
    def fields(self, list_order=False):
        username = {'name': 'username', 'label': 'Username', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': False}
        chat_started = {'name': 'chat_started', 'label': ' Started', 'class': '', 'type': 'IntField', 'required': True, 'full_width': False}
        first_message = {'name': 'first_message', 'label': 'First Message', 'class': '', 'type': 'SingleLine', 'required': False, 'full_width': True}
        messages = {'name': 'messages', 'label': 'Messages', 'class': '', 'type': 'MultiLine', 'required': False, 'full_width': True}
        link = {'name' :  'link', 'label' : 'Chat', 'class' : '', 'type' : 'ButtonField','full_width':False,'link':'/chat/history'}
        if list_order:
            return [username, first_message,chat_started,link]
        return [username,first_message,chat_started, messages,link]
        
class Prompt(DynamicDocument):
    name = StringField(required=True, min_length=1)
    welcome_message = StringField(required=True, min_length=1)
    system_message = StringField(required=True, min_length=1)
    prompt = StringField(required=True, min_length=1)
    link = StringField(default='')
    files = StringField(default='')

    meta = {'queryset_class': CustomQuerySet}

    def searchFields(self):
        return ['name', 'system_message', 'prompt']

    def fields(self, list_order=False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        welcome_message = {'name': 'welcome_message', 'label': 'Welcome Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        system_message = {'name': 'system_message', 'label': 'System Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        prompt = {'name': 'prompt', 'label': 'Prompt', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        link = {'name' :  'link', 'label' : 'Use Prompt', 'class' : '', 'type' : 'ButtonField','full_width':False,'link':'/chat/prompt'}
        files = {'name' :  'files', 'label' : 'Files', 'class' : 'hidden-xs', 'type' : 'FileField','full_width':True}

        if list_order:
            return [name,welcome_message, system_message, prompt,link]
        return [name,welcome_message, system_message, prompt,files,link]

    def to_json(self):
        return mongoToJson(self)

```

## ../core/db_connect.py

```
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

# Your MongoDB URI
mongodb_uri = f"mongodb+srv://{mongodb_user}:{mongodb_pwd}@cluster0.3sguoku.mongodb.net/flyon?retryWrites=true&w=majority&appName=Cluster0"

# Connect to your MongoDB database with SSL certificate verification
connect(host=mongodb_uri, tlsCAFile=certifi.where())

# class User(DynamicDocument):
#   user_name = StringField()
#   email = StringField(required=True)

# user = User(user_name="John Doe", email="mynbi@example.com")

# user.save()
```

