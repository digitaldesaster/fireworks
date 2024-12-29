# app.py

```
from flask import Flask, render_template, request, session, jsonify
from core import auth
from datetime import timedelta
import os
from flask_login import LoginManager, current_user, login_required
from core.db_user import User
from flask_wtf.csrf import CSRFProtect

# Import functions from helper.py and db_helper.py
from core.helper import getList, handleDocument, deleteDocument
from core.db_helper import getFile

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

# Route to handle and update a document
@app.route('/d/<name>', methods=['POST', 'GET'])
@app.route('/d/<name>/<id>', methods=['POST', 'GET'])
@app.route('/d/<name>/<id>/<return_format>', methods=['POST', 'GET'])
@login_required
def doc(name, id='', return_format='html'):
	if return_format == 'json':
		return handleDocument(name, id,request, return_json=True)
	else:
		return handleDocument(name, id,request)

# Route to delete a document
@app.route('/document/delete')
@login_required
def delete_document():
	print(f"[DEBUG] Delete request received with args: {request.args}")
	result = deleteDocument(request)
	print(f"[DEBUG] Delete result: {result}")
	return jsonify(result)

# Route to return a list of documents
@app.route('/list/<name>')
@app.route('/list/<name>/<return_format>')
@login_required
def list(name, return_format='html'):
		if return_format == 'json':
				return getList(name, request, return_json=True)
		else:
				return getList(name, request)

# Route to download a file
@app.route('/download_file/<file_id>')
def download_file(file_id):
		data = getFile(file_id)
		if data['status'] == 'ok':
				data = json.loads(data['data'])
				path = data['path']
				filename = file_id + '.' + data['file_type']
				return send_from_directory(path, filename)
		else:
				return jsonify({'status': 'error', 'message': 'File not found'})

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

## index.html

```
<!doctype html>
<html lang="en" data-theme="light">
  {% include('main/header.html') %}
  <body>
    {% include('main/nav.html') %}
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

## register.html

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
          <span>{{ message if message else 'Registration failed. Please check your input.' }}</span>
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

## login.html

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
              <span>{{ message if message else 'Invalid email or password' }}</span>
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

## testing/create_users.py

```
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
```

## main/footer.html

```

```

## main/header.html

```
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Fireworks</title>
  <link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/output.css') }}"
  />
</head>

```

## main/nav.html

```
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
      <div class="dropdown relative inline-flex rtl:[--placement:bottom-end]">
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
                >{{ current_user.firstname[0] }}{{ current_user.name[0] }}</span
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
            <form action="{{ url_for('logout') }}" method="post" class="w-full">
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

```

## base/collection/pagination.html

```
{% if total != null %}
<div class="flex items-center justify-between px-4 py-3">
  <div class="flex items-center">
    <nav class="flex items-center gap-x-1" aria-label="Pagination">
      {% if prev != null and prev != None %}
      <a
        href="{{collection_url}}?start=0&limit={{limit}}&search={{search}}&id={{id}}&filter={{filter}}"
        class="btn btn-outline btn-primary"
        aria-label="First"
      >
        <span
          class="icon-[tabler--chevrons-left] size-5 rtl:rotate-180 sm:hidden"
        ></span>
        <span class="hidden sm:inline">First</span>
      </a>
      <a
        href="{{collection_url}}?start={{prev}}&limit={{limit}}&search={{search}}&id={{id}}&filter={{filter}}"
        class="btn btn-outline btn-primary"
        aria-label="Previous"
      >
        <span
          class="icon-[tabler--chevron-left] size-5 rtl:rotate-180 sm:hidden"
        ></span>
        <span class="hidden sm:inline">Previous</span>
      </a>
      {% endif %}

      <div class="flex items-center gap-x-1">
        <!-- Page numbers would go here -->
      </div>

      {% if next %}
      <a
        href="{{collection_url}}?start={{next}}&limit={{limit}}&search={{search}}&id={{id}}&filter={{filter}}"
        class="btn btn-outline btn-primary"
        aria-label="Next"
      >
        <span class="hidden sm:inline">Next</span>
        <span
          class="icon-[tabler--chevron-right] size-5 rtl:rotate-180 sm:hidden"
        ></span>
      </a>
      {% endif %} {% if last != null and last != None %}
      <a
        href="{{collection_url}}?start={{last}}&limit={{limit}}&search={{search}}&id={{id}}&filter={{filter}}"
        class="btn btn-outline btn-primary"
        aria-label="Last"
      >
        <span class="hidden sm:inline">Last</span>
        <span
          class="icon-[tabler--chevrons-right] size-5 rtl:rotate-180 sm:hidden"
        ></span>
      </a>
      {% endif %}
    </nav>

    <div class="ml-4 text-sm text-gray-500">
      {% if total > 0 %} Showing
      <span class="font-medium">{{start}}</span>
      to
      <span class="font-medium">{{end}}</span>
      of
      <span class="font-medium">{{total}}</span>
      results {% else %} No results found {% endif %}
    </div>

    <!-- Limit dropdown -->
    <div class="dropdown relative inline-flex rtl:[--placement:bottom-end] ml-4">
      <button
        id="dropdown-default"
        type="button"
        class="dropdown-toggle btn btn-primary"
        aria-haspopup="menu"
        aria-expanded="false"
        aria-label="Limit"
      >
        Limit
        <span
          class="icon-[tabler--chevron-down] dropdown-open:rotate-180 size-4"
        ></span>
      </button>
      <ul
        aria-labelledby="dropdown-default"
        aria-orientation="vertical"
        class="dropdown-menu dropdown-open:opacity-100 hidden min-w-60"
        role="menu"
      >
        <li>
          <a
            class="dropdown-item"
            href="{{collection_url}}?start=0&limit=5&search={{search}}&filter={{filter}}"
          >
            5 Items
          </a>
        </li>
        <li>
          <a
            class="dropdown-item"
            href="{{collection_url}}?start=0&limit=10&search={{search}}&filter={{filter}}"
          >
            10 Items
          </a>
        </li>
        <li>
          <a
            class="dropdown-item"
            href="{{collection_url}}?start=0&limit=20&search={{search}}&filter={{filter}}"
          >
            20 Items
          </a>
        </li>
        <li>
          <a
            class="dropdown-item"
            href="{{collection_url}}?start=0&limit=50&search={{search}}&filter={{filter}}"
          >
            50 Items
          </a>
        </li>
      </ul>
    </div>
  </div>
</div>
{% endif %}

```

## base/collection/collection.html

```
<!doctype html>
<html lang="en">
  {% include('/main/header.html') %}
  <body class="bg-gray-50">
    {% include('/main/nav.html') %}

    <div class="container mx-auto px-4 py-8">
      <div class="card">
        <div class="card-header">
          <a href="{{collection_url}}" class="text-primary-600 text-lg"
            >{{page_name_collection}}</a
          >
        </div>

        <div class="card-body">
          <div class="flex flex-col md:flex-row justify-between gap-4">
            <div class="w-full md:w-1/2">
              <form
                method="GET"
                action="{{ url_for('list', name=collection_name,start=start, limit=limit, filter=filter) }}"
              >
                <div class="relative">
                  <div
                    class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none"
                  >
                    <svg
                      class="w-4 h-4 text-gray-500"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                        clip-rule="evenodd"
                      ></path>
                    </svg>
                  </div>
                  <input
                    type="text"
                    name="search"
                    class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Search"
                    value="{{ search }}"
                  />
                </div>
              </form>
            </div>

            <div class="flex justify-end">
              <a
                href="{{ url_for('doc',name = collection_name) }}"
                class="inline-flex items-center px-4 py-2 bg-primary-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-primary-500 active:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition ease-in-out duration-150"
              >
                New
              </a>
            </div>
          </div>
        </div>

        {% include('/base/collection/table.html') %}
      </div>
    </div>

    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>

```

## base/collection/table.html

```
<div class="w-full overflow-x-auto">
  {% include('/base/collection/pagination.html') %}
  <table class="table">
    <thead>
      <tr>
        {% for header in table_header %}
        <th class="{{header.class}}">{{header.label}}</th>
        {% endfor %}
        <th class="w-16">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for document in table_content %}
      <tr>
        {% for field in document %}
        <td class="{% if field.type == 'ButtonField' %}p-4{% endif %}">
          {% if field.type == 'ButtonField' %}
          <div class="flex justify-start items-center">
            <a href="{{field.link}}/{{field.id}}" class="w-full">
              <button
                type="button"
                class="btn btn-primary btn-sm {{field.class}} truncate"
              >
                {{field.label}}
              </button>
            </a>
          </div>
          {% else %} {{field.value}} {% endif %}
        </td>
        {% endfor %}
        <td class="w-8">
          <a
            href="{{document_url}}/{{document[0].id}}"
            class="btn btn-primary btn-sm"
          >
            <span class="icon-[tabler--edit] size-4"></span>
          </a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% include('/base/collection/pagination.html') %}
</div>

```

## base/document/form_items.html

```
{% for position in document.positions %}
<tr id="itemList_{{position.pos_nr}}">
  <td class="col-sm-1 col-md-1"><input class="item" type="hidden" name="item_{{position.pos_nr}}" id="item_{{position.pos_nr}}" value="{{position.pos_nr}}"><div class="pos" id = "pos_{{position.pos_nr}}">{{position.pos_nr}}</div></td>
  <td class="col-sm-2 col-md-2">
    <input type="hidden" name="itemid_{{position.pos_nr}}" id="itemid_{{position.pos_nr}}" value="{{position.item_id}}">
    <input type="hidden" name="optional_{{position.pos_nr}}" id="optional_{{position.pos_nr}}" value="{{position.optional}}">
    {% if position.optional=='true' %}
    <div id = "itemidtext_{{position.pos_nr}}">{{position.item_id}}<br><span class="label label-danger">Optional</span></div>
    {% else %}
    <div id = "itemidtext_{{position.pos_nr}}">{{position.item_id}}</div>
    {% endif %}

    </td>
  <td class="col-sm-3 col-md-4">
    <input type="hidden" name="name_{{position.pos_nr}}" id="name_{{position.pos_nr}}" value="{{position.name}}">
    <input type="hidden" name="description_{{position.pos_nr}}" id="description_{{position.pos_nr}}" value="{{position.description}}">
    <div id = "itemtext_{{position.pos_nr}}">{{position.name}}<br>
      {% if position.description%}
        {{position.description}}
      {% endif %}

    </div>
    </td>
  <td class="col-sm-2 col-md-2"><input type="text" class="maxlength-input form-control price" data-placement="bottom-right-inside" id="price_{{position.pos_nr}}" name="price_{{position.pos_nr}}" placeholder="" value="{{position.price}}">
  </td>
  <td class="col-sm-1 col-md-1">
    <input type="text" class="maxlength-input form-control amount" data-placement="bottom-right-inside" id="amount_{{position.pos_nr}}" maxlength="3" name="amount_{{position.pos_nr}}" placeholder="" value="{{position.amount}}">

  </td>
  <td class="col-sm-2 col-md-2">
    <input type="text" class="maxlength-input form-control" data-placement="bottom-right-inside" id="total_{{position.pos_nr}}" name="total_{{position.pos_nr}}" placeholder="" value="{{position.total}}" readonly="readonly">
  </td>
  <td class="col-sm-1 col-md-1">
    <a href=""><i class="btn btn-xs btn-outline btn-danger icon wb-minus removeItemField" aria-hidden="true" id="removeItemField_{{position.pos_nr}}"></i></a>

  </td>
  <td class="col-sm-1 col-md-1">
    <a href=""><i class="btn btn-xs btn-outline btn-primary icon wb-plus addItemField" aria-hidden="true" id="addItemField_{{position.pos_nr}}"></i></a>

  </td>
  <td class="col-sm-1 col-md-1">
    <a href=""><i class="btn btn-xs btn-outline btn-primary icon fa-comment addCommentField" aria-hidden="true" id="addCommentField_{{position.pos_nr}}"></i></a>

  </td>
  <td class="col-sm-1 col-md-1">
    <a href=""><i class="btn btn-xs btn-outline btn-primary icon wb-edit editItemField" aria-hidden="true" id="editItemField_{{position.pos_nr}}"></i></a>

  </td>
  <td class="col-sm-1 col-md-1">
    <a href="" data-target="#searchItemModal" data-toggle="modal"><i class="btn btn-xs btn-outline btn-primary icon fa-refresh searchItemField" aria-hidden="true" id="searchItemField_{{position.pos_nr}}"></i></a>
  </td>
</tr>
{% if position.comment !='' %}
<tr id="commentRow_{{position.pos_nr}}">
  <td colspan="6">
  <textarea style="resize:None;" class="form-control" id="comment_{{position.pos_nr}}" name="comment_{{position.pos_nr}}" rows="3" placeholder="">{{position.comment}}</textarea>
  </td>
  <td>
    <a href=""><i class="btn btn-xs btn-outline btn-danger icon wb-minus removeComment" aria-hidden="true" id="removeComment_{{position.pos_nr}}"></i></a>
    </td>
</tr>
{% endif %}
{% endfor %}

```

## base/document/form.html

```
<!doctype html>
<html lang="en">
  {% include('/main/header.html') %}
  <body>
    {% include('/main/nav.html') %}

    <section class="bg-gray-50 p-4 flex items-center">
      <div class="max-w-screen-xl px-4 mx-auto lg:px-12 w-full">
        <!-- Start coding here -->
        <div class="relative bg-white shadow-md dark:bg-gray-800 sm:rounded-lg">
          <div class="flex items-center justify-center pt-4 px-4">
            <form
              method="POST"
              enctype="multipart/form-data"
              id="documentForm"
              class="w-full max-w-lg"
            >
              <input
                type="hidden"
                name="csrf_token"
                value="{{ csrf_token() }}"
              />
              <input type="hidden" name="id" value="{{document.id}}" />

              <div class="flex flex-wrap -mx-3 mb-6">
                {% include('/base/document/form_elements.html') %}
              </div>

              <!-- Save and Delete Buttons -->
              <div class="flex flex-wrap -mx-3 mb-6">
                <div
                  class="w-full px-3 mb-6 md:mb-0 flex justify-between space-x-3"
                >
                  <button
                    type="submit"
                    class="btn btn-primary w-1/2"
                    id="saveButton"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    class="btn btn-error w-1/2"
                    id="deleteButton"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </form>

            <div
              id="deleteModal"
              tabindex="-1"
              class="hidden overflow-y-auto overflow-x-hidden bg-gray-600 bg-opacity-65 backdrop-blur-sm fixed top-0 right-0 left-0 z-50 flex justify-center items-center w-full h-full"
            >
              <div
                id="modalContent"
                class="relative p-4 w-full max-w-md max-h-full"
              >
                <div class="relative bg-white rounded-lg shadow">
                  <button
                    type="button"
                    class="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center"
                    id="closeModal"
                  >
                    <svg
                      class="w-3 h-3"
                      aria-hidden="true"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 14 14"
                    >
                      <path
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                      />
                    </svg>
                    <span class="sr-only">Close modal</span>
                  </button>
                  <div class="p-4 md:p-5 text-center">
                    <svg
                      class="mx-auto mb-4 text-gray-400 w-12 h-12"
                      aria-hidden="true"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 20 20"
                    >
                      <path
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M10 11V6m0 8h.01M19 10a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                      />
                    </svg>
                    <h3 class="mb-5 text-lg font-normal text-gray-500">
                      Are you sure?
                    </h3>
                    <button
                      id="confirmDelete"
                      type="button"
                      class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center"
                    >
                      Yes, I'm sure
                    </button>
                    <button
                      id="cancelDelete"
                      type="button"
                      class="py-2.5 px-5 ms-3 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100"
                    >
                      No, cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    <script>
      document.addEventListener('DOMContentLoaded', function() {

        {% include 'base/document/js/delete_document.js' %}
        {% include 'base/document/js/checkbox.js' %}
        {% include 'base/document/js/search_field.js' %}

      });
    </script>
  </body>
</html>

```

## base/document/form_elements.html

```
{% for element in elements %}
<div
  class="{{ 'w-full' if element.full_width else 'w-full md:w-1/2' }} px-3 mb-6 md:mb-0"
>
  <label
    for="{{ element.id }}"
    class="block mt-3 mb-1 text-sm font-medium text-gray-900"
  >
    {{ element.label }}
  </label>

  {% if element.type == 'ButtonField' %}
  <a href="{{element.link}}/{{document.id}}"
    ><button
      type="button"
      class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 focus:outline-none"
    >
      {{element.label}}
    </button></a
  >
  {% endif %} {% if element.type == 'FileField' %}
  <input
    class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
    id="{{element.id}}"
    type="file"
    name="files_{{element.id}}"
    multiple
  />
  {% for file in element.value %} {% if file.element_id == element.id %}
  <div id="{{file.document_id}}" class="flex items-center justify-between mt-2">
    <span class="mt-1 text-sm text-gray-600">
      <a
        href="{{url_for('download_file',file_id=file.id)}}"
        class="text-blue-600 hover:text-blue-500"
        target="_blank"
      >
        {{ file.name }}
      </a>
    </span>
    <button
      id="{{file.id}}"
      document_id="{{file.document_id}}"
      class="delete_file bg-red-100 text-red-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded"
    >
      Delete
    </button>
  </div>
  {% endif %} {% endfor %} {% endif %} {% if element.type=='DocumentField' %}
  <!-- Search Field -->
  <input
    type="hidden"
    value="{{element.document_id}}"
    name="{{ element.name }}_hidden"
    id="{{ element.name }}_hidden"
  />
  <input
    id="{{element.id}}"
    name="{{element.name}}"
    value="{{element.value}}"
    module="{{element.module}}"
    document_field="{{element.document_field}}"
    type="text"
    placeholder="Search..."
    class="searchField bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
  />

  <!-- Dropdown Menu -->
  <div
    id="dropdownMenu"
    class="z-10 hidden bg-white rounded-lg shadow w-full mt-1 max-h-48 overflow-y-auto"
  >
    <ul id="userList" class="py-2 text-gray-700"></ul>
  </div>
  {% endif %} {% if element.type == 'IntField' or element.type =='FloatField' %}

  <div class="max-w-sm mx-auto">
    <input
      type="text"
      id="{{element.id}}"
      name="{{element.name}}"
      value="{{element.value}}"
      class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
    />
  </div>

  {% endif %} {% if element.type == 'Date' %}

  <div class="relative max-w-sm">
    <div
      class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none"
    >
      <svg
        class="w-4 h-4 text-gray-500 dark:text-gray-400"
        aria-hidden="true"
        xmlns="http://www.w3.org/2000/svg"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          d="M20 4a2 2 0 0 0-2-2h-2V1a1 1 0 0 0-2 0v1h-3V1a1 1 0 0 0-2 0v1H6V1a1 1 0 0 0-2 0v1H2a2 2 0 0 0-2 2v2h20V4ZM0 18a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8H0v10Zm5-8h10a1 1 0 0 1 0 2H5a1 1 0 0 1 0-2Z"
        />
      </svg>
    </div>
    <input
      datepicker
      datepicker-buttons
      datepicker-autoselect-today
      datepicker-autohide
      datepicker-format="dd.mm.yyyy"
      name="{{element.name}}"
      value="{{element.value}}"
      type="text"
      class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      placeholder="Select date"
    />
  </div>

  {% endif %} {% if element.type == 'CheckBox' %}
  <label class="inline-flex items-center mb-5 cursor-pointer">
    <input
      type="hidden"
      value="{{element.value}}"
      name="{{ element.name }}_hidden"
      id="{{ element.name }}_hidden"
    />
    <input
      type="checkbox"
      name="{{ element.name }}"
      class="sr-only peer checkbox-toggle"
      {% if element.value == "on" %}checked{% endif %}
    />
    <div
      class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:w-5 after:h-5 after:transition-all peer-checked:bg-blue-600"
    ></div>
  </label>
  {% endif %} {% if element.type =='SimpleListField' %}
  <select
    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
    id="{{element.id}}"
    name="{{element.name}}"
  >
    {% for item in element.SimpleListField %} {% if item.value == element.value
    %}
    <option value="{{item.value}}" selected="selected">{{item.name}}</option>
    {% else %}
    <option value="{{item.value}}">{{item.name}}</option>
    {% endif %} {% endfor %}
  </select>
  {% endif %} {% if element.type=='AdvancedListField' %}
  <select
    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
    id="{{element.id}}"
    name="{{element.name}}"
  >
    {% for item in element.AdvancedListField %} {% if item.value ==
    element.value %}
    <option value="{{item.value}}" selected="selected">{{item.name}}</option>
    {% else %}
    <option value="{{item.value}}">{{item.name}}</option>
    {% endif %} {% endfor %}
  </select>
  {% endif %} {% if element.type == 'SingleLine' %}
  <input
    id="{{ element.id }}"
    name="{{ element.name }}"
    type="text"
    value="{{ element.value }}"
    placeholder="{{ element.label }}"
    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
    {%
    if
    element.required
    %}required{%
    endif
    %}
  />
  {% elif element.type == 'MultiLine' %}
  <textarea
    id="{{ element.id }}"
    name="{{ element.name }}"
    rows="4"
    placeholder="{{ element.label }}"
    class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
    {%
    if
    element.required
    %}required{%
    endif
    %}
  >
{{ element.value }}</textarea
  >
  {% endif %} {% if element.required %}
  <p class="text-red-500 text-xs italic">Please fill out this field.</p>
  {% endif %}
</div>
{% endfor %}

```

## base/document/js/search_field.js

```
document.querySelectorAll('.searchField').forEach(searchField => {
    searchField.addEventListener('input', function() {
        const query = this.value;
        const module = this.getAttribute('module');  // Get the module attribute value
        const document_field = this.getAttribute('document_field'); 
        const dropdown = this.nextElementSibling;
        const userList = dropdown.querySelector('#userList');
        const document_field_hidden = document.getElementById(this.name + '_hidden');
        document_field_hidden.value = "";
        if (query.length > 3) {
            // Construct the URL using the module value
            const url = `{{ url_for("list", name="__MODULE__", mode="json") }}`.replace('__MODULE__', module);

            // Fetch users from the server based on the search query
            fetch(`${url}?search=${encodeURIComponent(query)}&limit=100`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === "ok" && data.message === "success") {
                        dropdown.classList.remove('hidden');
                        console.log(data);  // Log the result
                        userList.innerHTML = '';  // Clear the existing list

                        // Check if data.data is an array before iterating
                        if (Array.isArray(data.data)) {
                            // Append users to the list
                            data.data.forEach(user => {
                                const userItem = document.createElement('li');
                                userItem.innerHTML = `
                                    <a href="#" class="flex items-center px-4 py-2 hover:bg-gray-100">
                                        ${user[document_field]}
                                    </a>
                                `;
                                userItem.addEventListener('click', function(event) {
                                    event.preventDefault();
                                    searchField.value = user[document_field];
                                    document_field_hidden.value = user.id;
                                    dropdown.classList.add('hidden');
                                });
                                userList.appendChild(userItem);
                            });

                            // Log the length of the userList to verify
                            console.log(`Number of users appended: ${userList.children.length}`);

                        } else {
                            console.error('Error: data.data is not an array');
                        }
                    } else {
                        console.error('Error: Unexpected response format');
                    }
                })
                .catch(error => {
                    console.error('Error fetching user data:', error);  // Log error message
                });
        } else {
            
            dropdown.classList.add('hidden');
        }
    });
});

```

## base/document/js/checkbox.js

```
const checkboxes = document.querySelectorAll(".checkbox-toggle");
checkboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        const hiddenInput = document.getElementById(this.name + '_hidden');
        if (this.checked) {
            hiddenInput.value = 'on';
        } else {
            hiddenInput.value = 'off';
        }
    });
});
```

## base/document/js/delete_document.js

```
// Function to handle form submission for delete action
function submitDeleteForm() {
  var url =
    "{{url_for('delete_document')}}" +
    "?id=" +
    "{{document.id}}&type={{page.document_name}}";

  fetch(url)
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      if (result.status === "ok") {
        console.log("Document Deleted");
        window.location.href = "{{ page.collection_url }}";
      } else {
        console.log("Document not deleted");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

const modal = document.getElementById("deleteModal");
const deleteButton = document.getElementById("deleteButton");
const closeButton = document.getElementById("closeModal");
const confirmButton = document.getElementById("confirmDelete");
const cancelButton = document.getElementById("cancelDelete");
const modalContent = document.getElementById('modalContent');

function showModal() {
  modal.classList.remove("hidden");
}

function hideModal() {
  modal.classList.add("hidden");
}

deleteButton.addEventListener("click", showModal);
closeButton.addEventListener("click", hideModal);
cancelButton.addEventListener("click", hideModal);

confirmButton.addEventListener("click", function (ev) {
  ev.preventDefault();
  submitDeleteForm();
});

modal.addEventListener('click', function(event) {
  if (!modalContent.contains(event.target)) {
    hideModal();
  }
});


document.querySelectorAll('.delete_file').forEach(button => {
    button.addEventListener('click', function (event) {
        event.preventDefault();
        const documentId = this.getAttribute('document_id');
        const fileId = this.id;

        const url = "{{ url_for('delete_document') }}" + "?id="+fileId + "&type=files";
        console.log(url)

        fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status=='ok') {
                const fileElement = document.getElementById(documentId);
                if (fileElement) {
                    fileElement.remove();
                    console.log("File removed!")
                }
            } else {
                console.error('Failed to delete document:', data);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});


```

# core

## auth.py

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
                                message='All fields are required')
            
        if len(password) < 8:
            return render_template('register.html', status='error',
                                message='Password must be at least 8 characters')

        result = db_user.create_user(firstname, name, email, password)
        
        if result['status'] == 'error':
            return render_template('register.html', status='error',
                                message=result['message'])
            
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
            return render_template('login.html', status='error', message=status['message'])
    else:
        return render_template('login.html')

def do_logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

```

## db_user.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from core.db_document import *

import logging
from mongoengine.errors import NotUniqueError, ValidationError, OperationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            return {'status': 'error', 'message': 'user exists'}

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
        return {'status': 'ok', 'message': 'user created', 'id': str(user.id)}

    except ValidationError as e:
        logger.error(f"Validation error creating user {email}: {str(e)}")
        return {'status': 'error', 'message': 'Invalid user data provided'}
    except NotUniqueError as e:
        logger.error(f"Duplicate email error for {email}")
        return {'status': 'error', 'message': 'user exists'}
    except OperationError as e:
        logger.error(f"Database operation error creating user {email}: {str(e)}")
        return {'status': 'error', 'message': 'Database error occurred'}
    except Exception as e:
        logger.error(f"Unexpected error creating user {email}: {str(e)}")
        return {'status': 'error', 'message': 'An unexpected error occurred'}

def delete_user(email, password):
    try:
        user = User.objects(email=email).first()
        if not user:
            return {'status': 'error', 'message': 'user does not exist'}
        
        if not check_password_hash(user.pw_hash, password):
            return {'status': 'error', 'message': 'incorrect password'}
        
        user.delete()
        logger.info(f"User deleted successfully: {email}")
        return {'status': 'ok', 'message': 'user deleted'}
    except Exception as e:
        logger.error(f"Error deleting user {email}: {str(e)}")
        return {'status': 'error', 'message': 'Failed to delete user'}

def update_password(email, password, new_password):
    try:
        user = User.objects(email=email).first()
        if not user:
            return {'status': 'error', 'message': 'user does not exist'}

        if not check_password_hash(user.pw_hash, password):
            return {'status': 'error', 'message': 'incorrect password'}

        user.pw_hash = hash_password(new_password)
        user.save()
        logger.info(f"Password updated successfully for user: {email}")
        return {'status': 'ok', 'message': 'password updated'}
    except ValidationError as e:
        logger.error(f"Validation error updating password for {email}: {str(e)}")
        return {'status': 'error', 'message': 'Invalid password format'}
    except Exception as e:
        logger.error(f"Error updating password for {email}: {str(e)}")
        return {'status': 'error', 'message': 'Failed to update password'}

```

## db_modules.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_document import *

from flask import url_for

class Default():
    document_name = ''
    document_url = ''
    collection_name = ''
    collection_url = ''
    page_name_document = ''
    page_name_collection = ''
    collection_title = ''
    collection = None
    document = None
    menu = {}

def getDefaults(name):
    defaults = None
    
    if name == 'filter':
        defaults = ['filter', 'filter', 'Filter','Filter', Filter, Filter(), 'settings']
    elif name == 'user' or name == 'users':
        defaults = ['user', 'users', 'User','Users', User, User(), 'users']
    elif name == 'file' or name == 'files':
        defaults = ['file', 'files', 'File','Files', File, File(), 'files']
    elif name == 'testing':
        defaults = ['testing', 'testing', 'Testing','Testing', Testing, Testing(), 'testing']

    if defaults:
        d = Default()
        d.document_name = defaults[0]
        d.document_url = url_for('doc',name = defaults[0])
        d.collection_name = defaults[1]
        d.collection_url = url_for('list',name = defaults[1])
        d.page_name_document = defaults[2]
        d.page_name_collection = defaults[3]
        d.collection_title = defaults[3]
        d.collection = defaults[4]
        d.document = defaults[5]
        d.menu = {defaults[6] : 'open active',defaults[1] : 'open active'}
        return d
    else:
        return None

```

## db_helper.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *

from core.db_modules import *
from core.db_date import dbDates
import json

def searchDocuments(collection, searchFields,start = 0, limit = 10, search = '',filter='',product_name='',mode=''):
    searchAnd = []
    searchDict={}

    if (search != None and search !=''):
        searchArray = []
        for name in searchFields:
            #search contains string, option i means case insentive
            searchArray.append({name: {'$regex': search, '$options' : 'i'}})

        searchDict = {'$or': searchArray}

        if filter !='':
            searchAnd = getFilterDict(filter)

        if product_name!='':
            searchAnd.append({'name' : product_name})

        if searchAnd != []:
            searchDict['$and'] = searchAnd

        if mode =='channels':
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
        else:
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)
        return processDocuments(documents,recordsTotal,start,limit)
    else:
        if filter !='':
            searchDict = {}
            searchAnd = getFilterDict(filter)
            if searchAnd !=[]:
                if product_name!='':
                    searchAnd.append({'name' : product_name})
                searchDict['$and'] = searchAnd
                if mode =='channels':
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
                else:
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)
                return processDocuments(documents,recordsTotal,start,limit)
            else:
                return {'status' : 'error', 'message' : 'no filter found' }
        else:
            if product_name!='':
                searchDict['$and'] = [{'name' : product_name}]
                if mode =='channels':
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
                else:
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)
                return processDocuments(documents,recordsTotal,start,limit)
            else:
                if mode=='channels':
                    recordsTotal = collection.objects().count()
                    documents = collection.objects.order_by('category_id').skip(start).limit(limit)

                else:
                    recordsTotal = collection.objects().count()
                    documents = collection.objects.skip(start).limit(limit)
                return processDocuments(documents,recordsTotal,start,limit)




def getFile(file_id):
    file = File.objects(id=file_id).first()
    if file !=None:
        return {'status' : 'ok','message' :'', 'data' : file.to_json()}
    else:
        return {'status' : 'error', 'message' : 'no file found' }


def getDocumentsByID(collection,name, start=0, limit = 10,id=''):
    if id !='':
        recordsTotal = collection.objects(__raw__ = {name: {'$regex': id}}).count()
        documents = collection.objects(__raw__ = {name: {'$regex': id}}).skip(start).limit(limit)
        return processDocuments(documents,recordsTotal,start,limit)
    else:
        return processDocuments(None, recordsTotal,start,limit)

def getDocumentName(id, mode,field):
    default = getDefaults(mode)
    try:
        document = default.collection.objects(id = id).only(field).first()
        if document:
            return document[field]
        return ''
    except:
        return ''

def getFilter(category):
    data = []
    try:
        filters = Filter.objects(category = category)
        if filters != None :
            for filter in filters:
                #print filter
                name = filter.name
                filter_id = str(filter.id)
                data.append({'name' : name,'id' : filter_id})
            return data
    except:
        return []

def getMailTemplates(category):
    data = []
    try:
        templates = MailTemplate.objects(category = category)
        if templates != None :
            for template in templates:
                #print filter
                name = template.name
                template_id = str(template.id)
                data.append({'name' : name,'id' : template_id})
            return data
    except:
        return []

def processDocuments(documents, recordsTotal,start,limit):

    print ('processDocuments')

    prev = 0
    if start - limit > -1:
        prev = start - limit

    last = None

    i = start
    z = 0

    next = 0
    if start + limit < recordsTotal:
        next = start + limit
        last = recordsTotal - limit

    end = start + limit

    if recordsTotal > 0:
        start = start + 1
        if end > recordsTotal:
            end = recordsTotal


    if documents != None:
        return {'status' : 'ok','message' :'', 'data' : documents.to_json(),'recordsTotal' : recordsTotal, 'limit' : limit,'prev' : prev, 'next' : next, 'start' : start,'end' : end,'last' : last}
    return {'status' : 'error', 'message' : 'no documents found' }
def getFilterDict(filter_id):
    data = []
    try:
        filter = Filter.objects(id=filter_id).first()
        if 'filter' in filter:
            for x in filter['filter']:

                if x['field'].find('_date') == -1:
                    if x['operator'] =='is':
                        data.append({x['field'] : x['value']})
                    elif x['operator'] =='contains':
                        data.append({x['field'] : { '$regex' : x['value'],'$options' : 'i' }})
                    elif x['operator'] == 'is_not':
                        data.append({x['field'] : { '$ne' : x['value'] }})
                    elif x['operator'] == 'starts_with':
                        data.append({x['field'] : { '$regex' : '^'+x['value'] }})
                else:
                    if x['value'] =='current_week':
                        data.append({x['field'] : dbDates().thisWeek()})
                    elif x['value'] =='current_month':
                        data.append({x['field'] : dbDates().thisMonth()})
                    elif x['value'] =='current_year':
                        data.append({x['field'] : dbDates().thisYear()})
                    elif x['operator'] =='is_gte':
                        data.append({x['field'] : {'$gte': x['value']}})
                    elif x['operator'] =='is_lt':
                        data.append({x['field'] : {'$lt': x['value']}})
    except:
        pass
    return data

```

## __init__.py

```
# This file can be empty, it just marks the directory as a Python package 
```

## db_default.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_connect import *

import csv,json

from datetime import date

class Setting(DynamicDocument):
    name = StringField(required=True,min_length=4)
    description = StringField()
    type = StringField(required = True)

def initDefault():
    Setting.drop_collection()
    settings = []
    settings.append(Setting(name = 'salutation', lable_name='Anrede', type = 'SimpleListField', values = ['','Herr', 'Frau']))
   
    settings.append(Setting(name = 'ai_provider', lable_name='A.I. Provider', type = 'AdvancedListField',values = [{'' : ''},{'OpenAI' : 'open_ai'},{'Anthropic' :'anthropic'},{'Meta' :'meta'}]))
  
    languages = ['Deutsch', 'Englisch', 'Französich', 'Spanisch']
    #
    settings.append(Setting(name = 'language', lable_name = 'Sprachen', type = 'SimpleListField', values = languages))
   
    # my_number = Setting(name = 'My Number', lable_name = 'Rechnungs-Nr', type ='Counter', value=1000, year = year)
    # settings.append(my_number)

    for setting in settings:
        setting.save()
    #MultiLine, SingleLine, SingleSelection, MultiSelection, Date, Number, Counter, Label

def prepListField(db_values,type):
    array=[]
    for x in db_values:
        if type =='AdvancedListField':
            for key in x:
                array.append({'name' : key,'value' : x[key]})
        elif type == 'SimpleListField':
            array.append({'name' : x,'value' : x})
    return array

def getDefaultList(name, collection, type):
    if type == 'SimpleDocumentField':
        array=[]
        documents = collection.objects()
        #array.append({'name':document.name, 'value':0})
        for document in documents:
            array.append({'name':document.name, 'value':json.loads(document.to_json())['_id']['$oid']})
        return array
    document = collection.objects(name = name).first()
    if document != None:
        return prepListField(document.values,type)

def getCounter(name):
    document = Setting.objects(name = name).first()
    if document != None:
        if document.value != None:
            document.value = int(document.value) + 1
            document.save()
            return str(document.value)
    return 0

initDefault()

```

## helper.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json,os,csv
from core.db_helper import *
from core.db_crud import getDocument, updateDocument, createDocument, eraseDocument
from core.db_modules import getDefaults
from core.db_default import Setting, getDefaultList
    
import datetime

from core.db_document import File

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'temp'
DOCUMENT_FOLDER = 'documents'

import logging
current_path = os.path.dirname(os.path.realpath(__file__)) + '/'
# logging.basicConfig(format='%(asctime)s %(message)s\n\r',filename=current_path+'import_leads.log', level=logging.INFO,filemode='w')


from flask import render_template, redirect, url_for

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'])

def getRequestData(request):
    limit = request.args.get('limit')
    start = request.args.get('start')
    search = request.args.get('search')
    id = request.args.get('id')
    filter = request.args.get('filter')
    product_name = request.args.get('product_name')
    offer_id = request.args.get('offer_id')

    if product_name == None:
        product_name=''
    if search == None:
        search = ''
    if filter == None:
        filter = ''
    if id == None:
        id = ''
    if start == None:
        start = 0
    else:
        start = int(start)
    if limit == None:
        limit = 50
    else:
        limit = int(limit)

    end = start + limit

    if offer_id == None:
        offer_id=''



    return start,limit,end,search, id,filter,product_name,offer_id

def initData():
    data = []
    prev = None
    next = None
    last = None
    recordsTotal = None

    return data, prev, next, last, recordsTotal

def loadData(mydata):
    if (mydata['status'] == 'ok'):
        data = json.loads(mydata['data'])
        prev = mydata['prev']
        next = mydata['next']
        last = mydata['last']
        start = mydata['start']
        end = mydata['end']
        recordsTotal = mydata['recordsTotal']

        #pages = mydata['pages']
        i=0
        for x in data:
            data[i]['id'] = x['_id']['$oid']
            i=i+1
        return data,start,end,prev,next,recordsTotal,last
    return None

def getList(name, request,return_json=False):

    default = getDefaults(name)

    if default == None:
        return redirect(url_for('index'))

    data, prev, next, last, recordsTotal = initData()
    start,limit,end,search,id,filter,product_name,offer_id = getRequestData(request)

    filter_data = getFilter(default.document_name)

    #return json.dumps(filter_data)

    mode = default.collection_name

    if mode == 'products' and product_name !='':
        mydata = searchDocuments(default.collection,default.document.searchFields() ,start, limit, search,filter,product_name,mode)
    else:
        if id != '':
            mydata = getDocumentsByID(default.collection,'company_id' ,start, limit, id)
        else:
            mydata = searchDocuments(default.collection,default.document.searchFields() ,start, limit, search,filter,'',mode)

    processedData = loadData(mydata)

    if processedData:
        data,start,end,prev,next,recordsTotal,last = processedData
        if return_json:
            return json.dumps({'status' : 'ok','message' :'success', 'data' : data,'recordsTotal' : recordsTotal, 'prev': prev, 'next': next, 'last': last, 'start': start, 'end': end})


    

    table_header = default.document.fields(list_order = True)

    table_content = tableContent(data, table_header)

    try:
        table = request.args.get('table')
        if table:
            return render_template('/base/collection/table.html',menu = default.menu,documents = data, prev = prev, next=next,limit = limit,start = start, total = recordsTotal, end = end, search = search,id=id,offer_id=offer_id, last = last,page_name_collection=default.page_name_collection,collection_name=default.collection_name,collection_url=default.collection_url,document_url=default.document_url,mode=mode, table_header = table_header, table_content = table_content,filter = filter,filter_data = filter_data,product_name=product_name)
    except:
        pass
    return render_template('/base/collection/collection.html',menu = default.menu,documents = data, prev = prev, next=next,limit = limit,start = start, total = recordsTotal, end = end, search = search,id=id,offer_id=offer_id, last = last,page_name_collection=default.page_name_collection,collection_name=default.collection_name,collection_url=default.collection_url,document_url=default.document_url,mode=mode, table_header = table_header, table_content = table_content, filter=filter,filter_data = filter_data,product_name=product_name)

def handleDocument(name, id, request, return_json=False):
    try:
        print(f"[DEBUG] Starting handleDocument with name={name}, id={id}")
        data=[]
        page=[]
        default = getDefaults(name)

        if default == None:
            print(f"[DEBUG] No defaults found for name: {name}")
            return redirect(url_for('index'))

        print(f"[DEBUG] Got defaults: document_name={default.document_name}, collection_name={default.collection_name}")
        mode = default.document_name

        page = {'title' : default.page_name_document + 'add', 'collection_title' : default.collection_title, 'document_name' : default.document_name, 'document_url' : default.document_url, 'collection_url' : default.collection_url}

        file_status = upload_files(request, default.collection_name, id)
        print(f"[DEBUG] File status: {file_status}")
        
        form_data = htmlFormToDict(request.form)
        print(f"[DEBUG] Form data: {form_data}")
        category_fields = []

        if name=='filter':
            form_data = prepFilterData(form_data)

        if request.method == 'POST':
            print("[DEBUG] Processing POST request")
            if (form_data.get('id') and form_data['id'] not in ['', 'None', None]):
                print(f'[DEBUG] Updating Document with ID: {form_data["id"]}')
                data = updateDocument(form_data, default.document, default.collection)
            else:
                print('[DEBUG] Creating new Document')
                data = createDocument(form_data, default.document)

            if (data['status'] == 'ok'):
                data = json.loads(data['data'])
                data['id'] = data['_id']['$oid']
                if return_json:
                    return json.dumps(data)
                return redirect(url_for('doc', name=default.document_name) + '/' + data['id'])
            else:
                print(f"[DEBUG] Error in POST: {data.get('message', 'Unknown error')}")
                return json.dumps(data)

        elif request.method == 'GET':
            print(f"[DEBUG] Processing GET request with id={id}")
            if id:
                print(f'[DEBUG] Getting Document with ID: {id}')
                data = getDocument(id, default.document, default.collection)
                print(f"[DEBUG] getDocument result: {data}")
                if (data['status'] == 'ok'):
                    page = {'title': default.page_name_document + ' speichern', 'collection_title': default.collection_title, 'document_name': default.document_name, 'document_url': default.document_url, 'collection_url': default.collection_url, 'document_title': default.page_name_document}
                    data = json.loads(data['data'])
                    data['id'] = data['_id']['$oid']
                    
                    files = json.loads(File.objects(document_id=data['id']).to_json())
                    print(f"[DEBUG] Found files: {files}")
                    for file in files:
                        if not data.get(file['element_id']):
                            data[file['element_id']] = []
                        file['id'] = file['_id']['$oid']
                        file.pop('_id', None)
                        data[file['element_id']].append(file)
                    
                    if return_json:
                        return json.dumps(data)

                    if 'category' in data and name == 'filter':
                        category_fields = getFields(data['category'])
                else:
                    print(f"[DEBUG] Error getting document: {data.get('message', 'Unknown error')}")
                    print(f"[DEBUG] Redirecting to list with name={default.collection_name}")
                    return redirect(url_for('list', name=default.collection_name))

        print("[DEBUG] Getting elements")
        elements = getElements(data, default.document)
        print(f"[DEBUG] Elements: {elements}")
        return render_template('/base/document/form.html', elements=elements, menu=default.menu, page=page, document=data, mode=mode, category_fields=category_fields)
    except Exception as e:
        print(f"[DEBUG] Error in handleDocument: {str(e)}")
        if return_json:
            return json.dumps({'status': 'error', 'message': str(e)})
        return redirect(url_for('list', name=default.collection_name))

def deleteDocument(request):
    type = request.args.get('type')
    id = request.args.get('id')
    if id:
        default = getDefaults(type)
        if default == []:
            return {'status' : 'error', 'message' : 'no document found'}
        data = eraseDocument(id,default.document,default.collection)
        if (data['status'] == 'ok'):
            return {'status' : 'ok','message' : 'document deleted'}
        else:
            return {'status' : 'error','message' : 'document not deleted'}
    return {'status' : 'error','message' : 'no id'}
def tableContent(documents, table_header):
    tableContent=[]

    for document in documents:
        tableRow = []
        for field in table_header:
            if field['name'] in document.keys() and 'id' in document.keys():
                if field['name'].find('_date') !=-1:
           
                    date= document[field['name']]['$date']
                    document[field['name']] = datetime.datetime.fromtimestamp(date/1000).strftime('%d.%m.%Y')
                if 'link' in field.keys():
                    tableRow.append({'name': field['name'], 'value' : document[field['name']], 'class' : field['class'], 'id' : document['id'],'type':field['type'],'link':field['link'],'label':field['label']})
                else:
                    tableRow.append({'name': field['name'], 'value' : document[field['name']], 'class' : field['class'], 'id' : document['id'],'type':field['type'],'label':field['label']})
                    

            else:
                tableRow.append('')
        tableContent.append(tableRow)

    return tableContent
def getElements(data, document):
    elements=[]
    fields = document.fields()
    for field in fields:
        if not 'required' in field:
            required = False
        else:
            required = True
        if field['type'] == 'SimpleDocumentField':
            elements.append({'type' : getDefaultList(field['name'], Category, 'SimpleDocumentField'), 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'SimpleListField':
            elements.append({'type' : 'SimpleListField', 'SimpleListField':getDefaultList(field['name'], Setting, 'SimpleListField'), 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'AdvancedListField':
            elements.append({'type' : 'AdvancedListField','AdvancedListField': getDefaultList(field['name'], Setting, 'AdvancedListField'), 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'DocumentField':
            elements.append({'type' : 'DocumentField', 'name' : field['name'], 'value' : '' , 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width'],'module':field['module'],'document_field':field['document_field']})
        elif field['type'] == 'EditorField':
            elements.append({'type' : 'EditorField', 'name' : field['name'], 'value' : '' , 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})

        elif field['type'] == 'DateInfo':
            pass
        elif field['type'] == 'CheckBox':
            elements.append({'type' : field['type'], 'name' : field['name'], 'value' : 0, 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'ButtonField':
            elements.append({'type': field['type'], 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width'],'link':field['link']})
        else:
            elements.append({'type': field['type'], 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})

    return fillElements(elements,data)

def fillElements(elements,data):
    
    if data != []:
        for element in elements:
            for key in data.keys():
                if key == element['name']:
                    element['value'] = data[key]
                    if element['type'] == 'DocumentField':
                        id = data [key]
                        if id!='0815':
                            element['value'] = getDocumentName(element['value'],element['module'],element['document_field'])
                            element['document_id'] = id
                            element['url'] = url_for('doc',name=element['module'],id=id)
                        else:
                            element['value'] = ''


    return elements
    
def htmlFormToDict(form_data):
    data = {}
    for key in form_data.keys():
        data[key] = form_data.getlist(key)[0]
    return data
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_files(request, category='', document_id=''):
    status = {'status': 'ok', 'files': []}

    if request.method == 'POST':
        # Extract element IDs directly from the file input names
        element_ids = [key.split('files_', 1)[1] for key in request.files.keys()]

        for element_id in element_ids:
            files = request.files.getlist(f'files_{element_id}')
            if not files or files[0].filename == '':
                continue  # Skip if no files are selected

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    try:
                        if category != '':
                            filepath = os.path.join(current_path + DOCUMENT_FOLDER + '/' + category + '/')
                        else:
                            filepath = os.path.join(current_path + UPLOAD_FOLDER + '/')

                        if not os.path.exists(filepath):
                            os.makedirs(filepath)

                        file_type = filename.rsplit('.', 1)[1]
                        fileDB = File(name=filename, path=filepath, category=category, file_type=file_type, document_id=document_id, element_id=element_id)
                        fileDB.save()
                        fileID = getDocumentID(fileDB)

                        file.save(os.path.join(filepath, f"{fileID}.{file_type}"))

                        status[element_id].append({'id': fileID, 'name': filename, 'path': os.path.join(filepath, f"{fileID}.{file_type}")})

                    except Exception as e:
                        status = {'status': 'error', 'message': f'Error while saving File! / {str(e)}'}
                        return json.dumps(status)
                else:
                    status = {'status': 'error', 'message': 'Filetype not allowed!'}
                    return json.dumps(status)

    return json.dumps(status)

def getDocumentID(document):
    document = json.loads(document.to_json())
    id = document['_id']['$oid']
    return id

def prepFilterData(form_data):
    fields = []
    db_fields = []
    i=0
    for key in form_data:
        if 'field_' in key:
            fieldNumber = key.split('_')[1]
            fields.append(fieldNumber)
    for fieldNumber in fields:
        try:
            value = form_data['value_' + str(fieldNumber)]
            del(form_data['value_' + str(fieldNumber)])
        except:
            value = form_data['date_value_' + str(fieldNumber)]
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
            del(form_data['date_value_' + str(fieldNumber)])

        operator = form_data['operator_' + str(fieldNumber)]
        field = form_data['field_' + str(fieldNumber)]
        db_fields.append({'field' : field,'operator':operator,'value':value,'nr':str(i)})

        del(form_data['field_' + str(fieldNumber)])
        del(form_data['operator_' + str(fieldNumber)])
        i=i+1

    form_data['filter'] = db_fields
    return form_data

def combine_pdfs_to_text(files):
    result = {
        "status": "",
        "data": "",
        "character_count": 0
    }
    combined_text = ""
    try:
        for file in files:
            if file['file_type'].lower() == 'pdf':
                file_id = file['_id']['$oid']
                file_path = f"{file['path']}{file_id}.{file['file_type'].lower()}"
                try:
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        combined_text += f"Content of File: {file['name']}.{file['file_type'].lower()}\n"
                        combined_text += "-" * 50 + "\n"
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text = page.extract_text()
                            if text:
                                combined_text += text
                            else:
                                combined_text += "[No text found on this page]\n"
                            combined_text += "\n"
                        combined_text += "-" * 50 + "\n\n"
                except Exception as e:
                    result["status"] = "error"
                    result["data"] = f"Error reading {file['document_id']}.{file['file_type'].lower()}: {e}"
                    return result
        result["status"] = "ok"
        result["data"] = combined_text
        result["character_count"] = len(combined_text)
    except Exception as e:
        result["status"] = "error"
        result["data"] = str(e)

    return result



```

## db_document.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from bson import json_util, ObjectId
from flask_login import UserMixin

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

class User(DynamicDocument, UserMixin):
    firstname = StringField()
    name = StringField()
    email = StringField()
    pw_hash = StringField()
    role = StringField()
    csrf_token = StringField()
    modified_by = StringField()
    modified_date = DateTimeField()
    salutation = StringField()
    meta = {
        'collection': 'user',
        'queryset_class': CustomQuerySet
    }
    def searchFields(self):
        return ['email','firstname','name']
    def fields(self, list_order = False):
        email = {'name' :  'email', 'label' : 'Email', 'class' : '', 'type' : 'SingleLine', 'required' : True,'full_width':True}
        salutation = {'name' :  'salutation', 'label' : 'Anrede', 'class' : '', 'type' : 'SimpleListField','full_width':False}
        firstname = {'name' :  'firstname', 'label' : 'Vorname', 'class' : '', 'type' : 'SingleLine', 'full_width':False}
        name = {'name' :  'name', 'label' : 'Nachname', 'class' : '', 'type' : 'SingleLine','full_width':False}
       
        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [firstname,name,email]
        return [email,salutation,firstname,name]
    def to_json(self):
        return mongoToJson(self)
    def get_id(self):
        return str(self.email)

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


class Testing(DynamicDocument):
    name = StringField(required=True, min_length=1)
    email = StringField(required=True, min_length=1)
    salutation = StringField(default='')
    firstname = StringField(default='')
    comment = StringField(default='')
    active = StringField(default='off')
    newsletter = StringField(default='off')
    event_date = DateField(default=None)
    age_int = IntField(default=None)
    salary_float = FloatField(default=None)
    ai_provider = StringField(default='')
    user = StringField(default='')
    files = StringField(default='')
    more_files = StringField(default='')
    link = StringField(default='')
    
    meta = {'queryset_class': CustomQuerySet}
    
    def searchFields(self):
        return ['name', 'email', 'firstname']
        
    def fields(self, list_order = False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        email = {'name': 'email', 'label': 'Email', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        salutation = {'name': 'salutation', 'label': 'Anrede', 'class': '', 'type': 'SimpleListField', 'full_width': False}
        firstname = {'name': 'firstname', 'label': 'Vorname', 'class': '', 'type': 'SingleLine', 'full_width': False}
        comment = {'name': 'comment', 'label': 'Kommentar', 'class': '', 'type': 'MultiLine', 'full_width': True}
        active = {'name': 'active', 'label': 'Aktiv', 'class': '', 'type': 'CheckBox', 'full_width': False}
        newsletter = {'name': 'newsletter', 'label': 'Newsletter', 'class': '', 'type': 'CheckBox', 'full_width': False}
        event_date = {'name': 'event_date', 'label': 'Event-Datum', 'class': 'hidden-xs', 'type': 'Date', 'full_width': False}
        age_int = {'name': 'age_int', 'label': 'Alter', 'class': 'hidden-xs', 'type': 'IntField', 'full_width': False}
        salary_float = {'name': 'salary_float', 'label': 'Gehalt', 'class': 'hidden-xs', 'type': 'FloatField', 'full_width': False}
        ai_provider = {'name': 'ai_provider', 'label': 'Firma', 'class': 'hidden-xs', 'type': 'AdvancedListField', 'full_width': False}
        user = {'name': 'user', 'label': 'User', 'class': '', 'type': 'DocumentField', 'full_width': False, 'module': 'user', 'document_field': 'email'}
        files = {'name': 'files', 'label': 'Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}
        more_files = {'name': 'more_files', 'label': 'More Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}
        link = {'name': 'link', 'label': 'Link', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/d/testing'}

        if list_order:
            return [name, email, firstname]
        return [name, email, salutation, firstname, comment, active, newsletter, event_date, 
                age_int, salary_float, ai_provider, user, files, more_files, link]

    def to_json(self):
        return mongoToJson(self)

```

## db_connect.py

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

## db_date.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, datetime

#dont write pyc files!
sys.dont_write_bytecode = True

#returns isoDates
class dbDates():
    now = datetime.datetime.now()
    #print now.weekday()
    today = datetime.datetime(now.year,now.month,now.day)
    def firstDayThisMonth(self):
        date = self.today.replace(day=1)
        return date
    def firstDayLastMonth(self):
        date = self.today.replace(day=1,month=self.now.month-1)
        return date
    def firstDayNextMonth(self):
        date = self.today.replace(month=self.now.month+1, day=1)
        return date
    def firstDayThisYear(self):
        date = self.today.replace(month=1,day=1)
        return date
    def firstDayNextYear(self):
        date = self.today.replace(year=self.now.year+1,month=1,day=1)
        return date
    def thisYear(self):
        return {'$gte': self.firstDayThisYear(), '$lt': self.firstDayNextYear()}
    def thisMonth(self):
        return {'$gte': self.firstDayThisMonth(), '$lt': self.firstDayNextMonth()}
    def lastMonth(self):
        return {'$gte': self.firstDayLastMonth(), '$lt': self.firstDayThisMonth()}
    def thisWeek(self):
        start = self.today - datetime.timedelta(days=self.today.weekday())
        end = start + datetime.timedelta(days=7)
        return {'$gte': start, '$lt': end}
    def thisDay(self):
        return self.today
    def yesterDay(self):
        return self.today - datetime.timedelta(days=1)
    def tomorrow(self):
        return self.today + datetime.timedelta(days=1)

```

## db_crud.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('core')
from core.db_document import File
from core.db_connect import *
import os

import json,datetime
from flask import session

from db_default import getCounter
from bson import ObjectId

def createDocument(form_data,document):
    #print json.dumps(form_data)
    try:
        for key in form_data.keys():
            #print key
            if '_date' in key:
                try:
                    if form_data[key] !='':
                        document[key] = datetime.datetime.strptime(form_data[key], "%d.%m.%Y")
                    else:
                        document[key] = ''
                except:
                    return {'status' : 'error', 'message' : 'error preparing form date field'}
            elif not '_hidden' in key and key !='id' :
                document[key] = form_data[key]
    except:
        return {'status' : 'error', 'message' : 'error preparing form data'}

    try:
        counter_name = document.getCounterName()
        counter = getCounter(counter_name)
        document[counter_name] = counter
    except:
        pass

    try:
        created_by = 'Admin'#session['user_name']
        document['created_date'] = datetime.datetime.now()
        document['created_by'] = created_by
    except:
        return {'status' : 'error', 'message' : 'user_name not in session'}

    try:
        document.save()
        return {'status' : 'ok','message' :'', 'data' : document.to_json()}
    except ValidationError as e:
        print((str(e)))
        return {'status' : 'error', 'message' : 'validation error','data':document.to_json()}
    except:
        return {'status' : 'error', 'message' : 'contact not created' }

def updateDocument(form_data, document, collection):
    try:
        print(f"[DEBUG] Updating document with id={form_data['id']}")
        # Convert string id to ObjectId
        object_id = ObjectId(form_data['id'])
        document = collection.objects(_id=object_id).first()
        
        if document is None:
            print(f"[DEBUG] Document not found with id={form_data['id']}")
            return {'status': 'error', 'message': 'document not found'}

        print(f"[DEBUG] Found document to update: {document.to_json()}")
        
        try:
            for key in form_data.keys():
                #workaround for checkbox fields, checkbox fields are not in the form data if they are unchecked. check value is 'on', on check value should be 'off'
                if '_hidden' in key:
                    new_key = key.replace('_hidden', '')
                    if new_key in form_data:
                        document[new_key] = form_data[key]
                    else:
                        document[new_key] = ''
                elif '_int' in key:
                    if form_data[key] !='':
                        if form_data[key].find('.') != -1:
                            form_data[key]=form_data[key].split('.')[0]
                        if form_data[key].find(',') != -1:
                            form_data[key]=form_data[key].split(',')[0]
                        document[key] = int(form_data[key])
                    else:
                        document[key] = None
                elif '_float' in key:
                    if form_data[key] !='':
                        form_data[key] = form_data[key].replace(',','.')
                        document[key] = float(form_data[key])
                    else:
                        document[key] = None
                elif '_date' in key:
                    try:
                        if form_data[key] !='':
                            document[key] = datetime.datetime.strptime(form_data[key], "%d.%m.%Y")
                        else:
                            document[key] = None
                    except:
                        return {'status': 'error', 'message': 'error preparing form date field'}
                else:
                    hidden_key = key + '_hidden'
                    if not hidden_key in form_data and key != 'id':  # Skip the id field
                        document[key] = form_data[key]
        except Exception as e:
            print(f"[DEBUG] Error preparing form data: {str(e)}")
            return {'status': 'error', 'message': f'error preparing form data: {str(e)}'}

        try:
            modified_by = 'Admin'  # session['user_name']
            document['modified_date'] = datetime.datetime.now()
            document['modified_by'] = modified_by
        except Exception as e:
            print(f"[DEBUG] Error setting modified info: {str(e)}")
            return {'status': 'error', 'message': 'error setting modified info'}

        try:
            document.save()
            print(f"[DEBUG] Document updated successfully")
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
        except Exception as e:
            print(f"[DEBUG] Error saving document: {str(e)}")
            return {'status': 'error', 'message': f'error saving document: {str(e)}'}
            
    except Exception as e:
        print(f"[DEBUG] Error in updateDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error updating document: {str(e)}'}

def eraseDocument(id, document, collection):
    try:
        print(f"[DEBUG] Attempting to delete document with id={id}")
        # Convert string id to ObjectId
        object_id = ObjectId(id)
        document = collection.objects(_id=object_id).first()
        
        if document is not None:
            print(f"[DEBUG] Found document to delete: {document.to_json()}")
            if collection == File:
                try:
                    file_path = document.path + id + "." + document.file_type
                    os.remove(file_path)
                    print(f"[DEBUG] Deleted associated file: {file_path}")
                except FileNotFoundError:
                    print('[DEBUG] File not found, continuing with document deletion')
                    
            document.delete()
            print(f"[DEBUG] Document deleted successfully")
            return {'status': 'ok', 'message': 'deleted'}
        else:
            print(f"[DEBUG] No document found with id={id}")
            return {'status': 'error', 'message': 'document not found'}
    except Exception as e:
        print(f"[DEBUG] Error in eraseDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error deleting document: {str(e)}'}

def getDocument(id, document, collection):
    try:
        print(f"[DEBUG] Querying collection {collection.__name__} for document with id={id}")
        # Convert string id to ObjectId
        object_id = ObjectId(id)
        print(f"[DEBUG] Using ObjectId: {object_id}")
        
        # Try direct query first
        document = collection.objects(_id=object_id).first()
        
        if document is None:
            # Try alternate query structure
            document = collection.objects(__raw__={'_id': {'$oid': id}}).first()
        
        if document is not None:
            print(f"[DEBUG] Found document: {document.to_json()}")
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
        else:
            # Let's print all documents in collection to debug
            all_docs = collection.objects().limit(1)
            print(f"[DEBUG] Sample document from collection: {[doc.to_json() for doc in all_docs]}")
            print(f"[DEBUG] No document found with id={id} in collection {collection.__name__}")
            return {'status': 'error', 'message': f'Document not found in {collection.__name__}'}
    except Exception as e:
        print(f"[DEBUG] Error in getDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error retrieving document: {str(e)}'}

```

