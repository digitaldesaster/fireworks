# app.py

```
from flask import Flask, render_template, request, session, jsonify, send_from_directory, abort, flash, redirect, url_for
from core import auth
from datetime import timedelta, datetime
import os
from flask_login import LoginManager, current_user, login_required
from core.db_user import User
from flask_wtf.csrf import CSRFProtect
import json
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

# Import functions from helper.py and db_helper.py
from core.helper import getList, handleDocument, deleteDocument, upload_file
from core.db_helper import getFile
from core.db_document import File, Prompt, getDefaults

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Add format_time_ago filter
@app.template_filter('format_time_ago')
def format_time_ago(date):
	if not date:
		return ""
	
	now = datetime.now()
	diff = now - date
	
	minutes = diff.total_seconds() / 60
	hours = minutes / 60
	days = diff.days
	
	if minutes < 1:
		return "just now"
	elif minutes < 60:
		return f"{int(minutes)}m ago"
	elif hours < 24:
		return f"{int(hours)}h ago"
	elif days == 1:
		return "yesterday"
	elif days < 7:
		return f"{days}d ago"
	else:
		return date.strftime('%d.%m.%Y')

# Import and register the chat blueprint
from ai.ai_chat import dms_chat
app.register_blueprint(dms_chat, url_prefix='/chat')

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
	try:
		return User.objects(id=user_id).first()
	except:
		return None

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
	# Add special handling for history documents
	if name == 'history' and id:
		# Get the history document
		default = getDefaults('history')
		if default:
			try:
				doc = default.collection.objects(_id=ObjectId(id)).first()
				if not doc or doc.user_id != str(current_user.id):
					flash('Access denied. You can only view your own history.', 'error')
					return redirect(url_for('list', collection='history'))
			except Exception as e:
				print(f"[DEBUG] Error accessing history document: {str(e)}")
				flash('Error accessing history document', 'error')
				return redirect(url_for('list', collection='history'))

	if return_format == 'json':
		result = handleDocument(name, id, request, return_json=True)
		# Ensure we're returning valid JSON
		if isinstance(result, str):
			return result
		return jsonify(result)
	else:
		return handleDocument(name, id, request)

# Route to delete a document
@app.route('/document/delete')
@login_required
def delete_document():
	print(f"[DEBUG] Delete request received with args: {request.args}")
	result = deleteDocument(request)
	print(f"[DEBUG] Delete result: {result}")
	return jsonify(result)

# Route to return a list of documents
@app.route('/list/<collection>')
@login_required
def list(collection):
	mode = request.args.get('mode')
	
	# Handle special collections
	if collection == 'history':
		# History is always filtered by current user
		return getList('history', request, return_json=(mode == 'json'))
	elif collection in ['user', 'users']:
		if not current_user.is_admin:
			flash('Access denied. Only administrators can view the user list.', 'error')
			return redirect(url_for('index'))
		return getList('user', request, return_json=(mode == 'json'))
		
	return getList(collection, request, return_json=(mode == 'json'))

# Route to download a file
@app.route('/download_file/<file_id>')
@login_required
def download_file(file_id):
	try:
		data = getFile(file_id)
		if data['status'] == 'ok':
			file_data = json.loads(data['data'])
			file_obj = File.objects(id=file_id).first()
			
			# Check if user has permission to access this file
			if not file_obj.can_access(current_user):
				flash('Access denied. You can only access your own files.', 'error')
				return redirect(url_for('index'))
				
			path = file_data['path']
			filename = f"{file_id}.{file_data['file_type'].lower()}"
			original_filename = file_data['name']
			
			print(f"[DEBUG] Attempting to send file: {path}/{filename}")
			return send_from_directory(
				path, 
				filename,
				as_attachment=True,
				download_name=original_filename
			)
		else:
			print(f"[DEBUG] File not found: {file_id}")
			abort(404)
	except Exception as e:
		print(f"[DEBUG] Error in download_file: {str(e)}")
		abort(500)

@app.route('/d/<collection>/<id>')
@login_required
def view_document(collection, id):
	if collection == 'user':
		if not current_user.can_view_user(id):
			flash('Access denied. You can only view your own profile.', 'error')
			return redirect(url_for('list', collection='user'))
	return handleDocument(collection, id, request)

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
    "./node_modules/flatpickr/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flyonui"),
    require("flyonui/plugin"), // For FlyonUI JS components
    require("tailwindcss-motion"), // Added motion plugin
  ],
  flyonui: {
    themes: ["light", "dark", "gourmet"],
    vendors: true, // Enable vendor-specific CSS generation
  },
  safelist: [
    'list-inside',
    'list-disc',
    'list-decimal',
    'marker:text-purple-500',
    'mb-2',
    {
      pattern: /^list-/,
      variants: ['hover', 'focus'],
    },
    {
      pattern: /^marker:/,
      variants: ['hover', 'focus'],
    }
  ]
};
```

## login.html

```
<!doctype html>
<html lang="en" data-theme="light" class="overflow-y-scroll">
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
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
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
              <span
                >{{ message if message else 'Invalid email or password' }}</span
              >
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

## index.html

```
<!doctype html>
<html lang="en" data-theme="light" class="h-full overflow-y-scroll">
  {% include('main/header.html') %}
  <body class="min-h-full flex flex-col bg-gray-50">
    {% include('main/nav.html') %}
    <main class="flex-1 lg:pl-64">
      <div class="h-full flex items-center justify-center p-4">
        <div class="card max-w-2xl mx-auto">
          <div class="card-body text-center">
            <h5 class="card-title mb-2.5">
              Welcome back, {{ current_user.firstname }} {{ current_user.name
              }}!
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
    </main>

    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>
```

## base/document/form.html

```
<!doctype html>
<html lang="en" class="overflow-y-scroll">
  {% include('/main/header.html') %}
  <body class="bg-gray-50 min-h-screen">
    {% include('/main/nav.html') %}

    <section class="p-6 flex items-center lg:ml-64">
      <div class="max-w-screen-xl mx-auto px-4 lg:px-12 w-full">
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

              <h1 class="text-2xl font-bold">{{page.title}}</h1>
              <hr class="my-4" />
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
                    data-modal-target="confirm_modal"
                    data-action="{{url_for('delete_document')}}?id={{document.id}}&type={{page.document_name}}"
                    data-redirect="{{ page.collection_url }}"
                    data-message="Are you sure you want to delete this {{page.document_name}}? This action cannot be undone."
                    data-title="Confirm Deletion"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
    <script>
      window.addEventListener("load", function () {
        // Basic
        flatpickr("#flatpickr-date", {
          monthSelectorType: "static",
          locale: "de",
          dateFormat: "d.m.Y",
        });
      });
    </script>
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        // We're now using the global confirm modal, so we don't need delete_document.js
        {% include 'base/document/js/search_field.js' %}
      });
    </script>
    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
    <script src="{{ url_for('static', filename='js/lib/flatpickr.min.js') }}"></script>
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
    class="label label-text"
  >
    {{ element.label }}
  </label>

  {% if element.type == 'ButtonField' %}
  <a href="{{element.link}}/{{document.id}}"
    ><button
      type="button"
      class="btn btn-primary"
    >
      {{element.label}}
    </button></a
  >
  {% endif %} {% if element.type == 'FileField' %}
  <input
    class="input max-w-sm"
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
      type="button"
      data-modal-target="confirm_modal"
      data-action="/delete_document?id={{file.id}}&type=files"
      data-document-id="{{file.document_id}}"
      data-message="Are you sure you want to delete this file? This action cannot be undone."
      data-title="Delete File"
      class="bg-red-100 text-red-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded"
    >
      Delete
    </button>
  </div>
  {% endif %} {% endfor %} {% endif %} {% if element.type=='DocumentField' %}
  <!-- Search Field -->
  <input
    type="hidden"
    value="{{element.value_id if element.value_id else document.get(element.name + '_id', '')}}"
    name="{{ element.name }}_hidden"
    id="{{ element.name }}_hidden"
  />
  <input
    id="{{element.id}}"
    name="{{element.name}}"
    value="{{element.value if element.value else document.get(element.name, '')}}"
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
      value="{{element.value if element.value is not none else ''}}"
      class="input"
    />
  </div>

  {% endif %} {% if element.type == 'Date' %}

  <input
    type="text"
    class="input max-w-sm"
    placeholder="DD.MM.YYYY"
    id="flatpickr-date"
    name="{{element.name}}"
    value="{{element.value if element.value is not none else ''}}"
  />

  {% endif %} {% if element.type == 'CheckBox' %}
  <label class="inline-flex items-center mb-5 cursor-pointer">
    <input
      type="hidden"
      name="{{ element.name }}_hidden"
      value="Off"
    />
    <input
      type="checkbox"
      name="{{ element.name }}"
      class="switch switch-primary"
      value="On"
      {% if element.value == "On" %}checked{% endif %}
    />
  </label>
  {% endif %} {% if element.type =='SimpleListField' %}
  <select
    class="select max-w-sm appearance-none"
    aria-label="select"
    id="{{element.id}}"
    name="{{element.name}}"
  >
    {% for item in element.SimpleListField %} {% if item.value == element.value %}
    <option value="{{item.value}}" selected="selected">{{item.name}}</option>
    {% else %}
    <option value="{{item.value}}">{{item.name}}</option>
    {% endif %} {% endfor %}
  </select>
  {% endif %} {% if element.type=='AdvancedListField' %}
  <select class="select max-w-sm appearance-none" aria-label="select" id="{{element.id}}" name="{{element.name}}">
    {% for item in element.AdvancedListField %} {% if item.value == element.value %}
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
    class="input"
    {% if element.required %}required{% endif %}
  />
  {% elif element.type == 'MultiLine' %}
  <textarea
    id="{{ element.id }}"
    name="{{ element.name }}"
    rows="4"
    placeholder="{{ element.label }}"
    class="textarea"
    {% if element.required %}required{% endif %}
  >{{ element.value if element.value is not none else '' }}</textarea>
  {% endif %}
    <!-- {% if element.required %}
    <p class="text-red-500 text-xs italic">Please fill out this field.</p>
    {% endif %} -->
</div>
{% endfor %}
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

## base/document/js/search_field.js

```
document.querySelectorAll(".searchField").forEach((searchField) => {
  searchField.addEventListener("input", function () {
    const query = this.value;
    const module = this.getAttribute("module"); // Get the module attribute value
    const document_field = this.getAttribute("document_field");
    const dropdown = this.nextElementSibling;
    const userList = dropdown.querySelector("#userList");
    const document_field_hidden = document.getElementById(
      this.name + "_hidden",
    );

    // Clear hidden field if search field is empty
    if (!query || query.length === 0) {
      document_field_hidden.value = "";
      document_field.value = "";
      dropdown.classList.add("hidden");
      return;
    }

    if (query.length > 3) {
      // Construct the URL using the module value
      const url =
        `{{ url_for("list", collection="__MODULE__", mode="json") }}`.replace(
          "__MODULE__",
          module,
        );

      // Fetch users from the server based on the search query
      fetch(`${url}&search=${encodeURIComponent(query)}&limit=100`)
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "ok" && data.message === "success") {
            dropdown.classList.remove("hidden");
            console.log(data); // Log the result
            userList.innerHTML = ""; // Clear the existing list

            // Check if data.data is an array before iterating
            if (Array.isArray(data.data)) {
              // Append users to the list
              data.data.forEach((user) => {
                const userItem = document.createElement("li");
                userItem.innerHTML = `
                                    <a href="#" class="flex items-center px-4 py-2 hover:bg-gray-100">
                                        ${user[document_field]}
                                    </a>
                                `;
                userItem.addEventListener("click", function (event) {
                  event.preventDefault();
                  searchField.value = user[document_field];
                  document_field_hidden.value = user.id;
                  dropdown.classList.add("hidden");
                });
                userList.appendChild(userItem);
              });

              // Log the length of the userList to verify
              console.log(
                `Number of users appended: ${userList.children.length}`,
              );
            } else {
              console.error("Error: data.data is not an array");
            }
          } else {
            console.error("Error: Unexpected response format");
          }
        })
        .catch((error) => {
          console.error("Error fetching user data:", error); // Log error message
        });
    } else {
      dropdown.classList.add("hidden");
    }
  });
});
```

## base/collection/pagination.html

```
{% if total != null %}
<div class="flex flex-wrap items-center justify-between gap-2">
  <div class="flex flex-wrap items-center gap-2 sm:gap-4">
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

    <div class="text-sm text-gray-500">
      {% if total != None and total > 0 %} Showing
      <span class="font-medium">{{start}}</span>
      to
      <span class="font-medium">{{end}}</span>
      of
      <span class="font-medium">{{total}}</span>
      results {% else %} No results found {% endif %}
    </div>
  </div>

  <!-- Limit dropdown -->
  <div class="dropdown relative inline-flex rtl:[--placement:bottom-end]">
    <button
      id="dropdown-default"
      type="button"
      class="dropdown-toggle btn btn-primary btn-outline"
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
{% endif %}
```

## base/collection/collection.html

```
<!doctype html>
<html lang="en" class="overflow-y-scroll">
  {% include('/main/header.html') %}
  <body class="bg-gray-50 min-h-screen">
    {% include('/main/nav.html') %}

    <section class="p-4 sm:p-6 flex items-center lg:ml-64">
      <div class="max-w-screen-xl mx-auto px-2 sm:px-4 lg:px-12 w-full">
        <div
          class="relative bg-white shadow-md dark:bg-gray-800 sm:rounded-lg p-3 sm:p-4"
        >
          <div class="flex flex-col gap-4">
            <div
              class="flex flex-row justify-between items-center gap-2 sm:gap-4"
            >
              <div class="flex-1">
                <form
                  method="GET"
                  action="{{ url_for('list', collection=collection_name, start=start, limit=limit, filter=filter) }}"
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
                      class="w-full max-w-md pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Search"
                      value="{{ search }}"
                    />
                  </div>
                </form>
              </div>

              <div class="flex-none">
                {% if show_new_button %}
                <a
                  href="{{ url_for('doc',name = collection_name) }}"
                  class="btn btn-primary whitespace-nowrap"
                >
                  New
                </a>
                {% endif %}
              </div>
            </div>

            {% include('/base/collection/table.html') %}
          </div>
        </div>
      </div>
    </section>

    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>
```

## base/collection/table.html

```
<div class="flex flex-col gap-4">
  {% include('/base/collection/pagination.html') %}
  <div
    class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700"
  >
    <table class="table border-collapse w-full">
      <thead>
        <tr>
          {% for header in table_header %}
          <th
            class="font-bold {{header.class}} px-4 py-3 border-b border-r border-slate-200 dark:border-slate-700 last:border-r-0"
          >
            {{header.label}}
          </th>
          {% endfor %}
          <th
            class="w-16 px-4 py-3 text-right border-b border-r border-slate-200 dark:border-slate-700 last:border-r-0 sticky right-0 bg-white z-10"
          >
            Actions
          </th>
        </tr>
      </thead>
      <tbody>
        {% for document in table_content %}
        <tr
          id="tr-{{document[0].id}}"
          class="{% if not loop.last %}border-b border-slate-200 dark:border-slate-700{% endif %}"
        >
          {% for field in document %}
          <td
            class="font-normal leading-normal px-4 py-2 border-r border-slate-200 dark:border-slate-700 last:border-r-0 {% if field.name == 'first_message' %}max-w-md truncate line-clamp-2{% endif %}"
          >
            {% if field.type == 'ButtonField' %}
            <div class="flex justify-start items-center">
              <a href="{{field.link}}" class="w-full">
                <button
                  type="button"
                  class="btn btn-primary btn-outline btn-sm {{field.class}} truncate"
                >
                  {{field.label}}
                </button>
              </a>
            </div>
            {% else %} 
              <div class="{% if field.name == 'first_message' %}max-w-md truncate line-clamp-2{% endif %}">
                {{field.value}}
              </div>
            {% endif %}
          </td>
          {% endfor %}
          <td class="w-16 px-4 py-2 text-right sticky right-0 bg-white">
            <div class="flex gap-2 justify-end">
              <a
                href="{{document_url}}/{{document[0].id}}"
                class="btn btn-primary btn-sm btn-outline"
              >
                <span class="icon-[tabler--edit] size-4"></span>
              </a>
              <button
                type="button"
                class="btn btn-error btn-sm btn-outline"
                data-modal-target="confirm_modal"
                data-action="{{ url_for('delete_document') }}?id={{document[0].id}}&type={{collection_name}}"
                data-document-id="tr-{{document[0].id}}"
                data-message="Are you sure you want to delete this {{collection_name}}? This action cannot be undone."
                data-title="Delete {{collection_name|capitalize}}"
              >
                <span class="icon-[tabler--trash] size-4"></span>
              </button>
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% include('/base/collection/pagination.html') %}
</div>
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

## components/confirm_modal.html

```
<div
  id="confirm_modal"
  tabindex="-1"
  class="hidden overflow-y-auto overflow-x-hidden bg-gray-600 bg-opacity-65 backdrop-blur-sm fixed top-0 right-0 left-0 z-50 flex justify-center items-center w-full h-full"
>
  <div
    class="modal-content relative p-4 w-full max-w-md max-h-full"
  >
    <div class="relative bg-white rounded-lg shadow">
      <button
        type="button"
        class="close-modal absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center"
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
        <h3 class="mb-2 text-lg font-medium text-gray-900">Confirm Action</h3>
        <p class="mb-5 text-gray-500">Are you sure?</p>
        <button
          type="button"
          class="confirm-action text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center"
        >
          Yes, I'm sure
        </button>
        <button
          type="button"
          class="cancel-action py-2.5 px-5 ms-3 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100"
        >
          No, cancel
        </button>
      </div>
    </div>
  </div>
</div>
```

## components/confirm_modal.js

```
// Generic confirmation modal handler
class ConfirmModal {
  constructor(modalId) {
    this.modal = document.getElementById(modalId);
    if (!this.modal) {
      console.error(`Modal with ID ${modalId} not found`);
      return;
    }
    
    console.log(`Initializing modal: ${modalId}`);
    
    this.modalContent = this.modal.querySelector('.modal-content');
    this.confirmButton = this.modal.querySelector('button.confirm-action');
    this.cancelButton = this.modal.querySelector('button.cancel-action');
    this.closeButton = this.modal.querySelector('button.close-modal');
    
    // Elements for dynamic content
    this.titleElement = this.modal.querySelector('h3');
    this.messageElement = this.modal.querySelector('p');
    
    // Store modal ID for reference
    this.modalId = modalId;
    
    // Initialize with default data attributes
    this.actionUrl = '';
    this.redirectUrl = '';
    this.documentId = '';
    this.documentType = '';
    
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Close modal when clicking cancel or close buttons
    if (this.cancelButton) {
      this.cancelButton.addEventListener('click', (e) => {
        console.log('Cancel button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.hideModal();
      });
    }
    
    if (this.closeButton) {
      this.closeButton.addEventListener('click', (e) => {
        console.log('Close button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.hideModal();
      });
    }
    
    // Close modal when clicking outside
    this.modal.addEventListener('click', (event) => {
      if (this.modalContent && !this.modalContent.contains(event.target)) {
        console.log('Clicked outside modal');
        this.hideModal();
      }
    });
    
    // Handle confirm action
    if (this.confirmButton) {
      this.confirmButton.addEventListener('click', (e) => {
        console.log('Confirm button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.handleConfirmAction();
      });
    } else {
      console.error('Confirm button not found in modal');
    }
  }

  showModal(triggerElement) {
    console.log('Showing modal');
    
    // Update modal content based on trigger element's data attributes
    if (triggerElement) {
      this.updateModalFromTrigger(triggerElement);
    }
    
    this.modal.classList.remove('hidden');
  }

  hideModal() {
    console.log('Hiding modal');
    this.modal.classList.add('hidden');
  }
  
  updateModalFromTrigger(triggerElement) {
    // Get data attributes from trigger element
    this.actionUrl = triggerElement.dataset.action || '';
    this.redirectUrl = triggerElement.dataset.redirect || '';
    this.documentId = triggerElement.dataset.documentId || '';
    this.documentType = triggerElement.dataset.documentType || '';
    
    // Update modal content
    if (this.titleElement && triggerElement.dataset.title) {
      this.titleElement.textContent = triggerElement.dataset.title;
    }
    
    if (this.messageElement && triggerElement.dataset.message) {
      this.messageElement.textContent = triggerElement.dataset.message;
    }
    
    // Update modal data attributes (for backward compatibility)
    this.modal.dataset.action = this.actionUrl;
    this.modal.dataset.redirect = this.redirectUrl;
  }

  handleConfirmAction() {
    // Use the action URL from object property
    const url = this.actionUrl;
    
    if (!url) {
      console.error('No action URL specified for modal');
      this.hideModal();
      return;
    }
    
    console.log(`Making request to: ${url}`);
    
    // Determine if we should use POST method
    const usePost = this.modal.dataset.method === 'post' || url.includes('delete_all_history');
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    
    // Prepare fetch options
    const fetchOptions = {
      method: usePost ? 'POST' : 'GET',
      headers: {}
    };
    
    // Add CSRF token for POST requests
    if (usePost && csrfToken) {
      fetchOptions.headers['X-CSRFToken'] = csrfToken;
    }
    
    fetch(url, fetchOptions)
      .then(response => response.json())
      .then(result => {
        console.log('Response:', result);
        if (result.status === 'ok') {
          // Handle document/element removal if document ID is provided
          if (this.documentId) {
            const element = document.getElementById(this.documentId);
            if (element) {
              console.log(`Removing element with ID: ${this.documentId}`);
              element.remove();
            }
          }
          
          // Handle redirect if URL provided
          if (this.redirectUrl) {
            console.log(`Redirecting to: ${this.redirectUrl}`);
            window.location.href = this.redirectUrl;
          }
          
          // Trigger success event
          const event = new CustomEvent('confirmAction:success', { 
            detail: { 
              modalId: this.modalId, 
              result, 
              documentType: this.documentType,
              action: url.split('?')[0].split('/').pop() // Extract action name from URL
            } 
          });
          document.dispatchEvent(event);
        } else {
          console.error('Action failed:', result);
          // Trigger error event
          const event = new CustomEvent('confirmAction:error', { 
            detail: { modalId: this.modalId, result } 
          });
          document.dispatchEvent(event);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      })
      .finally(() => {
        this.hideModal();
      });
  }
}

// Initialize the global confirm modal when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing modals');
  
  // Find all confirm modals
  const modals = document.querySelectorAll('[id$="_modal"]');
  console.log(`Found ${modals.length} modals`);
  
  // Store modal instances in a global object for reference
  window.modalInstances = {};
  
  // Initialize each modal
  modals.forEach(modal => {
    console.log(`Creating ConfirmModal for ${modal.id}`);
    window.modalInstances[modal.id] = new ConfirmModal(modal.id);
  });
  
  // Add trigger handlers for buttons that should open modals
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  console.log(`Found ${modalTriggers.length} modal triggers`);
  
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', function(event) {
      event.preventDefault();
      const modalId = this.dataset.modalTarget;
      console.log(`Trigger clicked for modal: ${modalId}`);
      
      const modalInstance = window.modalInstances[modalId];
      if (modalInstance) {
        modalInstance.showModal(this);
      } else {
        console.error(`Modal instance for ID ${modalId} not found`);
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.classList.remove('hidden');
        } else {
          console.error(`Modal with ID ${modalId} not found`);
        }
      }
    });
  });
});
```

## chat/chat_messages_rendered.html

```
<div
  id="chat_messages"
  class="ml-2 mr-2 mt-3 mb-2 md:ml-16 md:mr-16 md:mt-6 overflow-auto flex flex-col space-y-2"
>
  {% for message in config.messages %} {% if message.role =='user' %}
  <div class="flex space-x-4 mb-4">
    <div
      class="flex justify-center items-center w-10 h-10 bg-gray-500 text-white rounded-full"
    >
      {{ config.firstname[0] if config.firstname else '' }}{{ config.name[0] if
      config.name else '' }}
    </div>
    <div
      class="message content bg-neutral-content rounded-lg p-4 flex-1 min-w-0 break-words"
      id="message-{{ loop.index }}"
    ></div>
  </div>
  {% endif %} {% if message.role =='assistant' %}
  <div class="flex space-x-4 mb-4">
    <div
      class="flex justify-center items-center w-10 h-10 bg-gray-600 text-white rounded-full"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="w-6 h-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"
        />
      </svg>
    </div>
    <div
      class="message content bg-secondary-content rounded-lg p-4 flex-1 min-w-0 break-words"
      id="message-{{ loop.index }}"
    ></div>
  </div>
  {% endif %} {% endfor %}
</div>

<script>
  // Process all messages after the page loads
  document.addEventListener('DOMContentLoaded', function() {
    {% for message in config.messages %}
      const messageContent = {{message.content|tojson}};
      const container = document.getElementById('message-{{ loop.index }}');
      if (container) {
        appendData(messageContent, container);
      }
    {% endfor %}
  });
</script>
```

## chat/user_message_template.html

```
<div class="flex space-x-4 mb-6">
  <div
    class="flex justify-center items-center w-10 h-10 bg-gray-500 text-white rounded-full flex-shrink-0"
  >
    {{ config.firstname[0] if config.firstname else '' }}{{ config.name[0] if
    config.name else '' }}
  </div>
  <div
    class="message content bg-neutral-content rounded-lg p-4 flex-1 min-w-0 break-words"
  ></div>
</div>
```

## chat/code_block_template.html

```
<div class="flex flex-col w-full">
    <div class="h-8 bg-gray-800 w-full flex rounded-t justify-between items-center px-4">
      <!-- Language Info Placeholder -->
      <span class="text-sm text-white language-info"></span>

      <div class="flex flex-row items-center gap-2">
        <span class="copied hidden text-sm font-extralight text-green-400">copied!</span>
        <!-- Copy Button -->
      <button class="h-4 w-4 copy-btn flex items-center justify-center text-white hover:text-green-400">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
        </svg>
      </button>
      </div>
      
    </div>
    <div class="w-full">
      <pre class="bg-gray-700 text-sm text-white rounded-b p-2 overflow-x-auto whitespace-pre-wrap">
      </pre>
    </div>
  </div>
```

## chat/chat_prompts.html

```
{% if config.messages | length == 0 %}
<div
  id="prompts"
  class="ml-2 mr-2 mb-2 md:ml-16 md:mr-16 flex flex-col gap-4 mt-8"
>
  {% if config.history %}
  <h3
    class="text-center text-xl font-semibold text-gray-700 dark:text-gray-300"
  >
    Last Chats
  </h3>
  <div class="flex flex-row flex-wrap justify-center gap-4">
    {% for item in config.history %}
    <a href="/chat/history/{{ item.id }}" class="no-underline">
      <div
        id="history_{{ loop.index }}"
        class="relative h-12 w-64 flex items-center justify-center bg-indigo-500 hover:bg-indigo-700 text-white rounded-xl cursor-pointer px-4"
      >
        <span class="truncate">{{ item.first_message }}</span>
      </div>
    </a>
    {% endfor %}
  </div>
  <hr class="h-px my-2 bg-gray-200 border-0 dark:bg-gray-700" />
  {% endif %} {% if config.latest_prompts %}
  <h3
    class="text-center text-xl font-semibold text-gray-700 dark:text-gray-300"
  >
    Latest Prompts
  </h3>
  <div class="flex flex-row flex-wrap justify-center gap-4">
    {% for prompt in config.latest_prompts %}
    <a href="/chat/prompt/{{ prompt.id }}" class="no-underline">
      <div
        id="prompt_{{ loop.index }}"
        class="relative h-12 w-64 flex items-center justify-center bg-indigo-500 hover:bg-indigo-700 text-white rounded-xl cursor-pointer px-4"
      >
        <span class="truncate">{{ prompt.name }}</span>
      </div>
    </a>
    {% endfor %}
  </div>
  {% endif %} {% if not config.history and not config.latest_prompts %}
  <div class="flex flex-row flex-wrap justify-center gap-4">
    <div
      class="prompt relative h-12 w-64 flex items-center justify-center bg-indigo-500 hover:bg-indigo-700 text-white rounded-xl cursor-pointer px-4"
    >
      <span class="truncate">Wer war Ada Lovelace?</span>
    </div>
    <div
      class="group relative prompt h-12 w-64 flex items-center justify-center bg-indigo-500 hover:bg-indigo-700 text-white rounded-xl cursor-pointer px-4"
    >
      <span class="truncate">Schreibe eine index.html</span>
    </div>
  </div>
  {% endif %}
</div>
{% endif %}
```

## chat/bot_message_template.html

```
<div class="flex space-x-4 mb-6">
  <div
    class="flex justify-center items-center w-10 h-10 bg-gray-600 text-white rounded-full flex-shrink-0"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="1.5"
      stroke="currentColor"
      class="w-6 h-6"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"
      />
    </svg>
  </div>
  <div class="flex-1 min-w-0">
    <div
      class="message content bg-secondary-content rounded-lg p-4 break-words"
    ></div>
    <div class="flex justify-start mt-2">
      <button
        class="copy-btn flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 active:scale-95 transition-all duration-100 rounded px-2 py-1 hover:bg-gray-100"
      >
        <svg
          class="w-4 h-4 copy-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"
          />
        </svg>
        <svg
          class="w-4 h-4 check-icon hidden"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M4.5 12.75l6 6 9-13.5"
          />
        </svg>
        <span class="copy-text">Copy</span>
        <span class="check-text hidden">Copied!</span>
      </button>
    </div>
  </div>
</div>
```

## chat/chat_messages.html

```
<div
  id="chat_messages"
  class="mt-4 mb-4 overflow-auto flex flex-col min-h-[200px]"
></div>
```

## chat/chat_ui.html

```
<div
  id="chat_ui"
  class="fixed bottom-0 left-0 lg:left-64 lg:w-[calc(100%-16rem)] w-full h-40 bg-base-100"
>
  <div
    class="flex flex-col absolute bottom-0 left-0 right-0 h-32 ml-2 mr-2 mb-2 md:ml-10 md:mr-10 md:mb-4 rounded-xl bg-white shadow-[0_-2px_15px_-3px_rgba(0,0,0,0.1)] border border-gray-100"
  >
    <div class="p-3 pr-16 overflow-hidden">
      <textarea
        id="chat_input"
        placeholder="Type your message and press Command or Strg + Enter"
        rows="3"
        class="border-none ring-0 w-full rounded-lg focus:outline-none focus:ring-0 resize-none"
      ></textarea>
    </div>
    <div class="ml-6 mb-4 flex items-center gap-2">
      <div
        class="dropdown relative inline-flex [--placement:top]"
        data-dropdown
      >
        <button
          id="modelSelectorButton"
          class="badge badge-outline dropdown-toggle"
          data-model-badge
        >
          <span id="selected_model"></span>
        </button>
        <div
          class="dropdown-menu min-w-44 dropdown-open:opacity-100 hidden"
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="modelSelectorButton"
        >
          {% for model in config.models %}
          <button
            id="{{ model.model }}"
            data-name="{{ model.name }}"
            class="model dropdown-item w-full text-left px-4 py-2 hover:bg-gray-100"
          >
            {{ model.name }}
          </button>
          {% endfor %}
        </div>
      </div>

      <label for="file-upload" class="cursor-pointer">
        <div
          class="badge badge-outline badge-secondary flex items-center gap-1"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-4 h-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13"
            />
          </svg>
          <span id="file-name-display">Upload</span>
        </div>
      </label>
      <input type="file" id="file-upload" class="hidden" />
    </div>

    <div class="absolute bottom-0 right-0 p-3 flex flex-col gap-2">
      <button
        id="reset_button"
        class="bg-slate-800 hover:bg-slate-600 text-white font-extralight p-2.5 rounded"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 4.5v15m7.5-7.5h-15"
          />
        </svg>
      </button>

      <button
        id="chat_button"
        class="bg-slate-800 hover:bg-slate-600 text-white font-extralight p-2.5 rounded"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
          />
        </svg>
      </button>
      <button
        id="stop_button"
        class="hidden bg-red-500 hover:bg-red-400 text-white font-extralight p-2.5 rounded"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M5.25 7.5A2.25 2.25 0 0 1 7.5 5.25h9a2.25 2.25 0 0 1 2.25 2.25v9a2.25 2.25 0 0 1-2.25 2.25h-9a2.25 2.25 0 0 1-2.25-2.25v-9Z"
          />
        </svg>
      </button>
    </div>
  </div>
</div>
```

## chat/chat.html

```
<!doctype html>
<html lang="en" class="h-full">
  {% include('/main/header.html') %}
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="csrf-token" content="{{ csrf_token() }}" />
    <title>Chat</title>
  </head>
  <body class="min-h-full flex flex-col bg-base-100">
    {% include('/main/nav.html') %}

    <section class="flex-1 flex items-start overflow-y-auto lg:ml-64">
      <div class="px-4 md:px-10 w-full">
        <div class="relative min-h-[calc(100vh-8rem)] pb-32">
          <main id="main" class="flex flex-col h-full">
            {% if config.messages|length == 0 %}
            <!-- Show prompts and history first in a fresh chat -->
            <div id="selected_prompts_container" class="flex-1">
              {% include '/chat/chat_prompts.html' %}
            </div>
            <div id="chat_messages_container" class="pb-40">
              {% include '/chat/chat_messages.html' %}
            </div>
            {% else %}
            <!-- Show messages first in an existing chat -->
            <div id="chat_messages_container" class="pb-40">
              {% include '/chat/chat_messages.html' %}
            </div>
            <div id="selected_prompts_container">
              {% include '/chat/chat_prompts.html' %}
            </div>
            {% endif %}

            <div id="chat_history_container" class="hidden"></div>
            <div id="prompts_container" class="hidden"></div>
            <div id="create_prompt_container" class="hidden"></div>
            <div id="chat_ui_container">{% include '/chat/chat_ui.html' %}</div>
          </main>

          <!-- Bot Message Template -->
          <template id="bot-message-template">
            {% include '/chat/bot_message_template.html' %}
          </template>

          <!-- User Message Template -->
          <template id="user-message-template">
            {% include '/chat/user_message_template.html' %}
          </template>

          <!-- File Banner Template -->
          <template id="file-banner-template">
            <div class="mb-6">
              <div class="bg-blue-50 border-l-4 border-blue-400 p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg
                      class="h-5 w-5 text-blue-400"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                  <div class="ml-3 flex items-center gap-3">
                    <p class="text-sm text-blue-700">
                      Using context from file: <span class="filename"></span>
                    </p>
                    <a
                      href="#"
                      class="download-link text-blue-700 hover:text-blue-900"
                    >
                      <svg
                        class="w-4 h-4"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
                        />
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <template id="code_template">
            {% include '/chat/code_block_template.html' %}
          </template>
        </div>
      </div>
    </section>

    <script>
      // Global variables
      const messages = {{ config.messages | tojson | safe }};
      const systemMessage = {{ config.system_message|tojson }};
      const welcomeMessage = {{ config.welcome_message|tojson }};
      const models = {{ config.models | tojson | safe}};
      const use_prompt_template = {{ config.use_prompt_template|tojson }};
      const username = {{ config.username|tojson }};
      const chat_started = {{ config.chat_started|tojson }};

      // Model selection
      var selected_model = models[0]['model'];
      var selected_model_name = models[0]['name'];
      var selectedModelElement = document.getElementById('selected_model');
      var modelBadgeElement = document.querySelector('[data-model-badge]');

      // Function to update badge color based on model name
      function updateModelBadgeColor(modelName) {
        if (modelBadgeElement) {
          // Remove any existing badge color classes
          modelBadgeElement.classList.remove('badge-primary', 'badge-success', 'badge-error');
          
          // Add appropriate class based on model name
          if (modelName.includes('Azure')) {
            modelBadgeElement.classList.add('badge-success');
          } else {
            modelBadgeElement.classList.add('badge-error');
          }
        }
      }

      // Check localStorage for saved model
      if (localStorage.getItem('selected_model') !== null) {
        selected_model = localStorage.getItem('selected_model');
        const model = models.find(m => m.model === selected_model);
        if (model) {
          selected_model_name = model.name;
        }
      }

      selectedModelElement.innerText = selected_model_name;
      // Set initial badge color
      updateModelBadgeColor(selected_model_name);

      document.addEventListener('click', function (e) {
        if (e.target.closest('#prompts .prompt')) {
          var chatInput = document.getElementById('chat_input');
          if (chatInput) {
            chatInput.value = e.target.textContent;
          }

          var chatButton = document.getElementById('chat_button');
          if (chatButton) {
            chatButton.click();
          }

          var promptsDiv = document.getElementById('prompts');
          if (promptsDiv) {
            promptsDiv.remove();
          }
        }

        if (event.target.classList.contains('model')) {
          selected_model = event.target.id;
          selected_model_name = event.target.dataset.name;
          localStorage.setItem('selected_model', selected_model);
          selectedModelElement.innerText = selected_model_name;
          // Update badge color when model changes
          updateModelBadgeColor(selected_model_name);
          const modelSelectorButton = document.getElementById('modelSelectorButton');
          if (modelSelectorButton) {
            modelSelectorButton.click();
          }
        }
      });
    </script>

    <script src="{{ url_for('static', filename='/chat/chat_core.js') }}"></script>
    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
  </body>
</html>
```

## main/header.html

```
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="csrf-token" content="{{ csrf_token() }}" />
  <title>Fireworks</title>
  <link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/output.css') }}"
  />
  <link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/flatpickr.min.css') }}"
  />
  <script src="{{ url_for('static', filename='js/confirm_modal.js') }}" defer></script>
</head>
```

## main/nav.html

```
<!-- Sticky Navigation -->
<nav
  class="navbar bg-base-100 flex items-center justify-between p-4 sticky top-0 z-[60] shadow-sm"
>
  <div class="navbar-start">
    <a
      href="{{ url_for('index') }}"
      class="link text-base-content/90 text-xl font-semibold no-underline flex items-center gap-2"
    >
      Fireworks
    </a>
  </div>
  <div class="navbar-end flex items-center gap-2">
    <!-- User Avatar Dropdown for Desktop -->
    <div
      class="dropdown relative inline-flex max-lg:hidden [--auto-close:inside] [--offset:8] [--placement:bottom-end]"
    >
      <button
        type="button"
        class="dropdown-toggle avatar placeholder"
        aria-haspopup="menu"
        aria-expanded="false"
        aria-label="User menu"
      >
        <div class="bg-primary text-primary-content rounded-full w-10">
          <span class="text-lg"
            >{{ current_user.firstname[0] }}{{ current_user.name[0] }}</span
          >
        </div>
      </button>
      <ul
        class="dropdown-menu dropdown-open:opacity-100 hidden min-w-48"
        role="menu"
      >
        <div class="dropdown-header">
          <h6 class="text-base-content/90 text-base">
            {{ current_user.firstname }} {{ current_user.name }}
          </h6>
        </div>
        <a
          href="{{ url_for('doc', name='user', id=current_user.id) }}"
          class="dropdown-item"
        >
          <span class="icon-[tabler--user] size-5"></span>
          Edit Profile
        </a>
        <form action="{{ url_for('logout') }}" method="post">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
          <button type="submit" class="dropdown-item w-full text-left">
            <span class="icon-[tabler--logout-2] size-5"></span>
            Sign Out
          </button>
        </form>
      </ul>
    </div>
    <!-- Mobile Menu Button -->
    <button
      type="button"
      class="btn btn-text max-lg:btn-square lg:hidden"
      aria-haspopup="dialog"
      aria-expanded="false"
      aria-controls="mobile-menu-overlay"
      data-overlay="#mobile-menu-overlay"
    >
      <span class="icon-[tabler--menu-2] size-5"></span>
    </button>
  </div>
</nav>

<aside
  id="mobile-menu-overlay"
  class="overlay drawer drawer-start w-64 max-w-64 lg:fixed lg:top-[57px] lg:bottom-0 lg:left-0 lg:z-40 lg:flex lg:translate-x-0 overlay-open:translate-x-0 -translate-x-full transition-transform duration-300"
  tabindex="-1"
>
  <div class="drawer-body w-64 bg-white h-full flex flex-col overflow-hidden">
    <!-- Fixed Header Section -->
    <div class="px-2 pt-4 pb-2 border-b border-base-200 flex-none">
      <ul class="menu w-full space-y-0.5 p-0">
        <li class="w-full">
          <a
            href="{{ url_for('index') }}"
            class="flex items-center gap-2 px-4 py-2 w-full"
          >
            <span class="icon-[tabler--dashboard] size-5 shrink-0"></span>
            <span class="truncate">Dashboard</span>
          </a>
        </li>
        <li class="w-full">
          <a
            href="{{ url_for('dms_chat.chat') }}"
            class="flex items-center gap-2 px-4 py-2 w-full"
          >
            <span class="icon-[tabler--message] size-5 shrink-0"></span>
            <span class="truncate">Chat</span>
          </a>
        </li>
      </ul>
    </div>

    <!-- Scrollable Content Section -->
    <div
      class="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-base-300 scrollbar-track-transparent px-2 py-2"
    >
      <ul
        class="menu w-full space-y-0.5 [&_.nested-collapse-wrapper]:space-y-0.5 [&_ul]:space-y-0.5 p-0 pb-6"
      >
        {% if current_user.is_admin %}
        <li class="w-full space-y-0.5">
          <button
            type="button"
            class="collapse-toggle w-full flex items-center gap-2 px-4 py-2 collapse-open:bg-base-content/10"
            id="admin-collapse"
            aria-expanded="false"
            aria-controls="admin-collapse-content"
            data-collapse="#admin-collapse-content"
          >
            <span class="icon-[tabler--shield-lock] size-5 shrink-0"></span>
            <span class="truncate flex-1">Admin</span>
            <span
              class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 shrink-0 transition-transform duration-300"
            ></span>
          </button>
          <div
            id="admin-collapse-content"
            class="collapse hidden w-full overflow-hidden transition-[height] duration-300"
            role="menu"
            aria-labelledby="admin-collapse"
          >
            <div>
              <ul class="menu w-full space-y-0.5">
                <li class="w-full">
                  <a
                    href="{{ url_for('list', collection='user') }}"
                    class="text-xs w-full px-4 py-2 hover:bg-base-200 flex items-center gap-2 rounded-lg"
                  >
                    <span class="icon-[tabler--users] size-5 shrink-0"></span>
                    <span class="truncate">Manage Users</span>
                  </a>
                </li>
                <li class="w-full">
                  <a
                    href="{{ url_for('list', collection='models') }}"
                    class="text-xs w-full px-4 py-2 hover:bg-base-200 flex items-center gap-2 rounded-lg"
                  >
                    <span class="icon-[tabler--brain] size-5 shrink-0"></span>
                    <span class="truncate">Manage Models</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </li>
        {% endif %}
        <li class="w-full space-y-0.5">
          <button
            type="button"
            class="collapse-toggle w-full flex items-center gap-2 px-4 py-2 collapse-open:bg-base-content/10"
            id="prompts-collapse"
            aria-expanded="false"
            aria-controls="prompts-collapse-content"
            data-collapse="#prompts-collapse-content"
          >
            <span class="icon-[tabler--app-window] size-5 shrink-0"></span>
            <span class="truncate flex-1">Prompts</span>
            <span
              class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 shrink-0 transition-transform duration-300"
            ></span>
          </button>
          <div
            id="prompts-collapse-content"
            class="collapse hidden w-full overflow-hidden transition-[height] duration-300"
            aria-labelledby="prompts-collapse"
          >
            <div>
              <ul class="menu space-y-0.5 w-full" id="prompts-list">
                <li class="w-full">
                  <a
                    href="{{ url_for('list', collection='prompts') }}"
                    class="text-xs view-all w-full px-4 py-2 hover:bg-base-200 flex items-center rounded-lg"
                  >
                    <span class="truncate">View All Prompts</span>
                  </a>
                </li>
                <li class="w-full">
                  <a
                    href="{{ url_for('doc', name='prompt') }}"
                    class="text-xs w-full px-4 py-2 hover:bg-base-200 flex items-center gap-2 text-primary rounded-lg group"
                  >
                    <span class="icon-[tabler--plus] size-3.5 shrink-0"></span>
                    <span class="truncate">New Prompt</span>
                  </a>
                </li>
                <li class="w-full border-t border-base-200 my-1"></li>
                {% for prompt in prompts %}
                <li class="w-full">
                  <div
                    class="flex items-center gap-2 w-full px-4 py-2 hover:bg-base-200 group rounded-lg"
                  >
                    <a
                      href="{{ url_for('chat.prompt', id=prompt.id) }}"
                      class="flex-1 min-w-0"
                      title="{{ prompt.name }}"
                    >
                      <span class="truncate text-xs block"
                        >{{ prompt.name }}</span
                      >
                    </a>
                    <span
                      class="text-[10px] text-gray-500 whitespace-nowrap shrink-0"
                      >{{ format_time_ago(prompt.modified_date) }}</span
                    >
                    <a
                      href="{{ url_for('prompt.edit', id=prompt.id) }}"
                      class="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      aria-label="Edit prompt"
                      title="Edit prompt"
                    >
                      <span
                        class="icon-[tabler--edit] size-3.5 text-primary"
                      ></span>
                    </a>
                  </div>
                </li>
                {% endfor %}
              </ul>
            </div>
          </div>
        </li>
        <li class="w-full space-y-0.5">
          <button
            type="button"
            class="collapse-toggle w-full flex items-center gap-2 px-4 py-2 collapse-open:bg-base-content/10"
            id="history-collapse"
            aria-expanded="false"
            aria-controls="history-collapse-content"
            data-collapse="#history-collapse-content"
          >
            <span class="icon-[tabler--clock] size-5 shrink-0"></span>
            <span class="truncate flex-1">History</span>
            <span
              class="icon-[tabler--chevron-down] collapse-open:rotate-180 size-4 shrink-0 transition-transform duration-300"
            ></span>
          </button>
          <div
            id="history-collapse-content"
            class="collapse hidden w-full overflow-hidden transition-[height] duration-300"
            aria-labelledby="history-collapse"
          >
            <div>
              <ul class="menu space-y-0.5 w-full" id="history-list">
                <li class="w-full">
                  <a
                    href="{{ url_for('list', collection='history') }}"
                    class="text-xs view-all w-full px-4 py-2 hover:bg-base-200 flex items-center rounded-lg"
                  >
                    <span class="truncate">View All History</span>
                  </a>
                </li>
                <li class="w-full">
                  <button
                    type="button"
                    class="text-xs w-full px-4 py-2 hover:bg-base-200 flex items-center gap-2 text-error rounded-lg group"
                    data-modal-target="confirm_modal"
                    data-action="{{ url_for('dms_chat.delete_all_history') }}"
                    data-message="Are you sure you want to delete all history documents? This action cannot be undone."
                    data-title="Delete All History"
                  >
                    <span class="icon-[tabler--trash] size-3.5 shrink-0"></span>
                    <span class="truncate">Delete History </span>
                  </button>
                </li>
                <li class="w-full border-t border-base-200 my-1"></li>
                {% for item in history %}
                <li class="w-full">
                  <a
                    href="{{ url_for('chat.history', id=item.id) }}"
                    class="flex items-center gap-2 w-full px-4 py-2 hover:bg-base-200 rounded-lg"
                    title="{{ item.first_message or 'Untitled Chat' }}"
                  >
                    <span class="truncate flex-1 text-xs"
                      >{{ item.first_message or "Untitled Chat" }}</span
                    >
                    <span
                      class="text-[10px] text-gray-500 whitespace-nowrap shrink-0"
                      >{{ format_time_ago(item.modified_date) }}</span
                    >
                  </a>
                </li>
                {% endfor %}
              </ul>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Fixed Footer Section -->
    <div class="flex-none border-t border-base-200 px-2 pt-4 pb-2 lg:hidden">
      <form action="{{ url_for('logout') }}" method="post" class="w-full">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
        <button
          type="submit"
          class="btn btn-ghost w-full justify-start gap-2 text-error"
        >
          <span class="icon-[tabler--logout-2] size-5 shrink-0"></span>
          <span class="truncate">Sign Out</span>
        </button>
      </form>
    </div>
  </div>
</aside>

<script>
  // Add error notification function
  function showErrorNotification(message) {
    console.error(message);
  }

  // Function to format date
  function formatDate(dateString) {
    let date;
    if (typeof dateString === "string") {
      // Try to parse the formatted date string from mongoToJson (DD.MM.YYYY HH:MM)
      const parts = dateString.split(" ");
      if (parts.length === 2) {
        const [datePart, timePart] = parts;
        const [day, month, year] = datePart.split(".");
        const [hours, minutes] = timePart.split(":");
        date = new Date(year, month - 1, day, hours, minutes);
      } else {
        date = new Date(dateString);
      }
    } else if (dateString?.$date) {
      // Handle MongoDB ISODate format
      date = new Date(dateString.$date);
    } else {
      return "";
    }

    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) {
      return "just now";
    } else if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays === 1) {
      return "yesterday";
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  // Function to fetch and update nav items with improved error handling
  async function updateNavItems() {
    try {
      const response = await fetch("{{ url_for('dms_chat.get_nav_items') }}");
      if (!response.ok) {
        throw new Error(`Failed to fetch nav items: ${response.status}`);
      }

      const data = await response.json();
      console.log("Total history items received:", data.history.length);

      // Validate data structure
      if (
        !data ||
        !Array.isArray(data.prompts) ||
        !Array.isArray(data.history)
      ) {
        throw new Error("Invalid navigation data structure");
      }

      // Update prompts list
      const promptsList = document.getElementById("prompts-list");
      if (promptsList) {
        // Keep the view all and new prompt links
        const staticLinks = promptsList.querySelectorAll("li:nth-child(-n+3)");
        promptsList.innerHTML = "";
        staticLinks.forEach((link) =>
          promptsList.appendChild(link.cloneNode(true)),
        );

        // Add prompts with error handling
        data.prompts.forEach((prompt) => {
          try {
            if (!prompt?._id?.$oid || !prompt?.name) {
              console.warn("Invalid prompt data:", prompt);
              return;
            }

            console.log("Prompt modified date:", prompt.modified_date);
            const formattedDate = formatDate(prompt.modified_date);
            console.log("Formatted date:", formattedDate);

            const li = document.createElement("li");
            li.className = "w-full";
            li.innerHTML = `
              <div class="flex items-center gap-2 w-full px-4 py-2 hover:bg-base-200 group rounded-lg">
                <a href="/chat/prompt/${prompt._id.$oid}" class="flex-1 min-w-0" title="${prompt.name}">
                  <span class="truncate text-xs block">${prompt.name}</span>
                </a>
                <span class="text-[10px] text-gray-500 whitespace-nowrap shrink-0">${formattedDate}</span>
                <a href="/d/prompt/${prompt._id.$oid}" class="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" aria-label="Edit prompt" title="Edit prompt">
                  <span class="icon-[tabler--edit] size-3.5 text-primary"></span>
                </a>
              </div>
            `;
            promptsList.appendChild(li);
          } catch (itemError) {
            console.warn("Error adding prompt item:", itemError);
          }
        });
      }

      // Update history list
      const historyList = document.getElementById("history-list");
      if (historyList) {
        // Keep the view all link and delete button
        const staticLinks = historyList.querySelectorAll("li:nth-child(-n+3)");
        historyList.innerHTML = "";
        staticLinks.forEach((link) =>
          historyList.appendChild(link.cloneNode(true)),
        );

        let addedCount = 0;
        // Add history items with error handling
        data.history.forEach((item) => {
          try {
            if (!item?._id?.$oid) {
              return;
            }

            const li = document.createElement("li");
            li.className = "w-full";
            li.innerHTML = `
              <a href="/chat/history/${item._id.$oid}" 
                 class="flex items-center gap-2 w-full px-4 py-2 hover:bg-base-200 rounded-lg"
                 title="${item.first_message || "Untitled Chat"}">
                <span class="truncate flex-1 text-xs">${item.first_message || "Untitled Chat"}</span>
                <span class="text-[10px] text-gray-500 whitespace-nowrap shrink-0">${formatDate(item.modified_date)}</span>
              </a>
            `;
            historyList.appendChild(li);
            addedCount++;
          } catch (itemError) {
            console.warn("Error adding history item:", itemError);
          }
        });
        console.log("Actually added history items:", addedCount);
      }
    } catch (error) {
      console.error("Error updating navigation:", error);
      showErrorNotification(
        "Failed to update navigation. Please refresh the page.",
      );
    }
  }

  // Function to handle history deletion
  async function handleDeleteHistory() {
    // This function is kept for backward compatibility
    // but is no longer directly called by the button click
    console.log("Legacy handleDeleteHistory called");
  }

  // Listen for the confirmAction:success event from our confirm modal
  document.addEventListener('confirmAction:success', async function(event) {
    const { modalId, result, documentType } = event.detail;
    
    // If this is from delete all history action
    if (result && result.action === 'delete_all_history') {
      // Check if we're on a history page or list history page
      const currentPath = window.location.pathname;
      if (
        currentPath.includes("/chat/history/") ||
        currentPath.includes("/list/history")
      ) {
        // Redirect to index page
        window.location.href = "/";
        return;
      }

      // Update the navigation items
      await updateNavItems();
    }
  });

  // Initialize nav items when the page loads
  document.addEventListener("DOMContentLoaded", updateNavItems);

  // Update nav items periodically with a debounce
  let updateTimeout = null;
  function debouncedUpdate() {
    if (updateTimeout) {
      clearTimeout(updateTimeout);
    }
    updateTimeout = setTimeout(updateNavItems, 500);
  }

  // Update every 30 seconds, but use debouncing to prevent overlapping calls
  setInterval(debouncedUpdate, 30000);
</script>

{% include 'components/confirm_modal.html' %}
```

## db_helper.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from core.db_date import dbDates
from core.db_document import File, getDefaults, Filter
import json
import os

def searchDocuments(collection, searchFields, start=0, limit=10, search='', filter=None, product_name='', mode=''):
    print(f"[DEBUG] searchDocuments called with filter={filter}")
    searchDict = {}

    # Handle search term if provided
    if search and search.strip():
        searchArray = []
        for name in searchFields:
            searchArray.append({name: {'$regex': search, '$options': 'i'}})
        searchDict = {'$or': searchArray}

    # Handle filter
    if filter:
        if isinstance(filter, str):
            # For string filters, use getFilterDict
            filter_dict = getFilterDict(filter)
            print(f"[DEBUG] Filter string converted to: {filter_dict}")
            if filter_dict:
                if searchDict:
                    if '$and' not in searchDict:
                        searchDict = {'$and': [searchDict]}
                    searchDict['$and'].extend(filter_dict)
                else:
                    searchDict = {'$and': filter_dict}
        else:
            # For direct dictionary filters (like user_id filter)
            print(f"[DEBUG] Using direct filter: {filter}")
            if searchDict:
                if '$and' not in searchDict:
                    searchDict = {'$and': [searchDict, filter]}
                else:
                    searchDict['$and'].append(filter)
            else:
                searchDict.update(filter)

    # Handle product name
    if product_name:
        product_filter = {'name': product_name}
        if searchDict:
            if '$and' not in searchDict:
                searchDict = {'$and': [searchDict, product_filter]}
            else:
                searchDict['$and'].append(product_filter)
        else:
            searchDict = product_filter

    print(f"[DEBUG] Final search dict: {searchDict}")

    try:
        # Test the query first
        test_count = collection.objects(__raw__=searchDict).count()
        print(f"[DEBUG] Test query found {test_count} documents")
        
        # Apply the query
        if mode == 'channels':
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
        else:
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)

        return processDocuments(documents, recordsTotal, start, limit)
    except Exception as e:
        print(f"[DEBUG] Error in searchDocuments: {str(e)}")
        print(f"[DEBUG] Collection: {collection}")
        print(f"[DEBUG] Search dict: {searchDict}")
        return {'status': 'error', 'message': str(e)}




def getFile(file_id):
    try:
        file = File.objects(id=file_id).first()
        if file is not None:
            # Verify file exists on disk
            file_path = os.path.join(file.path, f"{file_id}.{file.file_type}")
            if os.path.exists(file_path):
                return {'status': 'ok', 'message': '', 'data': file.to_json()}
            else:
                print(f"[DEBUG] Physical file not found at: {file_path}")
                return {'status': 'error', 'message': 'Physical file not found'}
        else:
            print(f"[DEBUG] No file record found for id: {file_id}")
            return {'status': 'error', 'message': 'File record not found'}
    except Exception as e:
        print(f"[DEBUG] Error in getFile: {str(e)}")
        return {'status': 'error', 'message': f'Error retrieving file: {str(e)}'}


def getDocumentsByID(collection, name, start=0, limit=10, id=''):
    if not id:
        # Return empty result set when no id is provided
        return {
            'status': 'ok',
            'message': '',
            'data': '[]',
            'recordsTotal': 0,
            'limit': limit,
            'prev': 0,
            'next': None,
            'start': 0,
            'end': 0,
            'last': None
        }
        
    try:
        recordsTotal = collection.objects(__raw__={name: {'$regex': id}}).count()
        documents = collection.objects(__raw__={name: {'$regex': id}}).skip(start).limit(limit)
        return processDocuments(documents, recordsTotal, start, limit)
    except Exception as e:
        print(f"[DEBUG] Error in getDocumentsByID: {str(e)}")
        return {'status': 'error', 'message': 'Error retrieving documents'}

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

# def getMailTemplates(category):
#     data = []
#     try:
#         templates = MailTemplate.objects(category = category)
#         if templates != None :
#             for template in templates:
#                 #print filter
#                 name = template.name
#                 template_id = str(template.id)
#                 data.append({'name' : name,'id' : template_id})
#             return data
#     except:
#         return []

def processDocuments(documents, recordsTotal, start, limit):
    print('processDocuments')
    
    # Handle case where documents is None
    if documents is None:
        return {'status': 'error', 'message': 'no documents found'}

    # Calculate pagination values
    prev = max(0, start - limit) if start - limit > -1 else 0
    next = start + limit if start + limit < recordsTotal else None
    last = recordsTotal - limit if recordsTotal > limit else None
    
    # Adjust start and end values
    end = min(start + limit, recordsTotal)
    display_start = start + 1 if recordsTotal > 0 else start

    # Return successful response even if no documents found (empty list is valid)
    return {
        'status': 'ok',
        'message': '',
        'data': documents.to_json(),
        'recordsTotal': recordsTotal,
        'limit': limit,
        'prev': prev,
        'next': next,
        'start': display_start,
        'end': end,
        'last': last
    }

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
            if not user:
                return render_template('login.html', status='error', message='User not found')
            
            login_user(user, remember=remember, duration=timedelta(days=30) if remember else None)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):  # Ensure the next URL is relative
                return redirect(next_page)
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

## db_default.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_connect import *
from core.db_document import getDefaults

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
   
    #settings.append(Setting(name = 'ai_provider', lable_name='A.I. Provider', type = 'AdvancedListField',values = [{'' : ''},{'OpenAI' : 'open_ai'},{'Anthropic' :'anthropic'},{'Meta' :'meta'}]))
  
    languages = ['Deutsch', 'Englisch', 'Französich', 'Spanisch']
    settings.append(Setting(name = 'language', lable_name = 'Sprachen', type = 'SimpleListField', values = languages))
   
    # Add roles
    roles = ['admin', 'user']
    settings.append(Setting(name = 'role', lable_name = 'Rollen', type = 'SimpleListField', values = roles))

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

#initDefault()
```

## db_crud.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('core')
from core.db_document import File, Prompt
from core.db_connect import *
import os

import json,datetime
from flask import session
from flask_login import current_user

from db_default import getCounter
from bson import ObjectId

def createDocument(form_data, document, request=None):
    print(f"[DEBUG] Starting createDocument with form_data keys: {form_data.keys()}")
    # Remove csrf_token before processing
    form_data = {k: v for k, v in form_data.items() if k != 'csrf_token'}
    
    try:
        # Initialize document with default values if it's a new document
        if isinstance(document, type):
            document = document()
        
        # Handle counter if needed
        try:
            counter_name = document.getCounterName()
            counter = getCounter(counter_name)
            document[counter_name] = counter
        except Exception as e:
            print(f"[DEBUG] Counter error: {str(e)}")

        # Process all non-file fields
        for key in form_data.keys():
            if key.startswith('files_'):
                continue
                
            if form_data[key] is None or (isinstance(form_data[key], list) and not form_data[key]):
                continue

            if key.endswith('_hidden'):
                base_key = key.replace('_hidden', '')
                if form_data[key]:
                    document[f"{base_key}_id"] = form_data[key]
                continue

            if form_data[key] == '':
                continue

            if '_date' in key:
                try:
                    document[key] = datetime.datetime.strptime(form_data[key], "%d.%m.%Y") if form_data[key] else None
                except ValueError as e:
                    return {'status': 'error', 'message': f'Invalid date format for field {key}'}
            elif '_int' in key:
                try:
                    document[key] = int(form_data[key]) if form_data[key] else None
                except ValueError:
                    return {'status': 'error', 'message': f'Invalid integer value for field {key}'}
            elif '_float' in key:
                try:
                    document[key] = float(form_data[key]) if form_data[key] else None
                except ValueError:
                    return {'status': 'error', 'message': f'Invalid float value for field {key}'}
            elif key != 'id':
                document[key] = form_data[key]

        # Save document
        try:
            document.save()
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
            
        except ValidationError as e:
            print(f"[DEBUG] Validation error: {str(e)}")
            return {'status': 'error', 'message': f'validation error: {str(e)}', 'data': document.to_json()}
        except Exception as e:
            print(f"[DEBUG] Save error: {str(e)}")
            return {'status': 'error', 'message': f'document not created: {str(e)}'}

    except Exception as e:
        print(f"[DEBUG] Error in createDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error creating document: {str(e)}'}

def updateDocument(form_data, document, collection):
    # Remove csrf_token before processing
    form_data = {k: v for k, v in form_data.items() if k != 'csrf_token'}
    
    try:
        print(f"[DEBUG] Updating document with id={form_data['id']}")
        object_id = ObjectId(form_data['id'])
        document = collection.objects(_id=object_id).first()
        
        if document is None:
            return {'status': 'error', 'message': 'document not found'}

        for key in form_data.keys():
            if key == 'id':  # Skip id field
                continue

            # Handle document search fields
            if key.endswith('_hidden'):
                base_key = key.replace('_hidden', '')
                if '_search' in base_key:
                    # Clear both the search field and its ID if hidden field is empty
                    if not form_data[key]:
                        document[base_key] = ''
                        document[f"{base_key}_id"] = ''
                    else:
                        document[f"{base_key}_id"] = form_data[key]
                else:
                    if base_key in form_data:
                        document[base_key] = form_data[base_key]  # Will be "On" if checked
                    else:
                        document[base_key] = "Off"  # Default to Off if unchecked
                continue

            # Handle different field types
            if '_date' in key:
                try:
                    document[key] = datetime.datetime.strptime(form_data[key], "%d.%m.%Y") if form_data[key] else None
                except:
                    return {'status': 'error', 'message': 'error preparing form date field'}
            elif '_int' in key:
                document[key] = int(form_data[key]) if form_data[key] else None
            elif '_float' in key:
                document[key] = float(form_data[key].replace(',','.')) if form_data[key] else None
            else:
                document[key] = form_data[key]

        # Save document
        try:
            document.save()
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
        except ValidationError as e:
            print(f"Validation error: {str(e)}")
            return {'status': 'error', 'message': f'validation error: {str(e)}', 'data': document.to_json()}
        except Exception as e:
            print(f"Error saving document: {str(e)}")
            return {'status': 'error', 'message': f'error saving document: {str(e)}'}
            
    except Exception as e:
        print(f"[DEBUG] Error in updateDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error updating document: {str(e)}'}

def eraseDocument(id, document, collection):
    try:
        print(f"[DEBUG] eraseDocument called with id={id}, collection={collection.__name__}")
        object_id = ObjectId(id)
        document = collection.objects(_id=object_id).first()
        
        if document is not None:
            print(f"[DEBUG] Found document to delete: {document.to_json()}")
            
            # Get base path for constructing absolute paths
            base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            print(f"[DEBUG] Base path: {base_path}")
            
            # Handle file deletion for both File collection and associated files
            if collection == File:
                # Check if user has permission to delete this file
                if not document.can_access(current_user):
                    print(f"[DEBUG] Access denied for file deletion: {id}")
                    return {'status': 'error', 'message': 'Access denied. You can only delete your own files.'}
                
                # Check if file is used by any prompt
                prompts_using_file = Prompt.objects(document_id=str(id))
                if prompts_using_file:
                    print(f"[DEBUG] File {id} is used by prompts, cannot delete")
                    return {'status': 'error', 'message': 'File is used by one or more prompts and cannot be deleted'}
                    
                # Direct file document deletion
                try:
                    # Use the same path construction as upload_files
                    file_path = os.path.join(base_path, document.path, f"{id}.{document.file_type}")
                    print(f"[DEBUG] Attempting to delete file at: {file_path}")
                    print(f"[DEBUG] File exists: {os.path.exists(file_path)}")
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"[DEBUG] Successfully deleted file: {file_path}")
                    else:
                        print(f'[DEBUG] Physical file not found at: {file_path}')
                except Exception as e:
                    print(f'[DEBUG] Error deleting physical file: {str(e)}')
                    return {'status': 'error', 'message': f'Error deleting physical file: {str(e)}'}
                
                try:
                    document.delete()
                    print(f"[DEBUG] Successfully deleted file document from database")
                    return {'status': 'ok', 'message': 'deleted'}
                except Exception as e:
                    print(f'[DEBUG] Error deleting file document: {str(e)}')
                    return {'status': 'error', 'message': f'Error deleting file document: {str(e)}'}
            else:
                # For non-File collections, handle associated files
                file_ids = []
                
                # Check for files linked by document_id
                associated_files = File.objects(document_id=str(id))
                file_ids.extend([str(f.id) for f in associated_files])
                
                # Check for files in file_ids array (used by History documents)
                if hasattr(document, 'file_ids') and document.file_ids:
                    file_ids.extend(document.file_ids)
                
                # Remove duplicates
                file_ids = list(set(file_ids))
                print(f"[DEBUG] Found {len(file_ids)} associated files")
                print(f"[DEBUG] File IDs to process: {file_ids}")
                
                deleted_files = []
                failed_files = []
                
                for file_id in file_ids:
                    try:
                        print(f"[DEBUG] Processing associated file: {file_id}")
                        file_doc = File.objects(id=file_id).first()
                        if not file_doc:
                            print(f"[DEBUG] File document not found: {file_id}")
                            failed_files.append(file_id)
                            continue
                            
                        # Check if file is used by any prompt
                        prompts_using_file = Prompt.objects(document_id=str(file_id))
                        if prompts_using_file:
                            print(f"[DEBUG] File {file_id} is used by prompts, skipping")
                            failed_files.append(file_id)
                            continue
                        
                        # Check if user has permission to delete this file
                        if not file_doc.can_access(current_user):
                            print(f"[DEBUG] Access denied for associated file deletion: {file_id}")
                            failed_files.append(file_id)
                            continue
                            
                        # Delete physical file
                        # Use the same path construction as upload_files
                        file_path = os.path.join(base_path, file_doc.path, f"{file_id}.{file_doc.file_type}")
                        print(f"[DEBUG] Attempting to delete associated file at: {file_path}")
                        print(f"[DEBUG] File exists: {os.path.exists(file_path)}")
                        
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"[DEBUG] Successfully deleted associated file: {file_path}")
                        else:
                            print(f'[DEBUG] Physical file not found at: {file_path}')
                        
                        # Delete file document
                        file_doc.delete()
                        deleted_files.append(file_id)
                        print(f"[DEBUG] Successfully deleted associated file document: {file_id}")
                    except Exception as e:
                        print(f'[DEBUG] Error deleting associated file {file_id}: {str(e)}')
                        failed_files.append(file_id)
                
                try:
                    document.delete()
                    status_msg = 'deleted'
                    if failed_files:
                        status_msg += f' (some associated files could not be deleted: {", ".join(map(str, failed_files))})'
                    print(f"[DEBUG] Successfully deleted main document with status: {status_msg}")
                    return {'status': 'ok', 'message': status_msg}
                except Exception as e:
                    print(f'[DEBUG] Error deleting main document: {str(e)}')
                    return {'status': 'error', 'message': f'Error deleting document: {str(e)}'}
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
            #print(f"[DEBUG] Found document: {document.to_json()}")
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

## __init__.py

```
# This file can be empty, it just marks the directory as a Python package
```

## db_document.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from bson import json_util
from flask_login import UserMixin, current_user
from flask import url_for
from datetime import datetime
from mongoengine import *

class AuditMixin:
    created_date = DateTimeField(default=lambda: datetime.now())
    created_by = StringField()
    modified_date = DateTimeField()
    modified_by = StringField()

    def save(self, *args, **kwargs):
        try:
            user = current_user.get_id() if current_user and current_user.is_authenticated else 'system'
        except:
            user = 'system'
            
        if not self.id:
            # Document is being created
            self.created_date = datetime.now()
            self.created_by = user
        
        # Always update modified info on save
        self.modified_date = datetime.now()
        self.modified_by = user
        
        return super().save(*args, **kwargs)

#Date Fields must be named name_date, e.g. contact_date
#This is to make sure that string dates like 01.01.2016 are saved as date objects
#functions to convert strings to date objects are in crud.py (create / update)

#every document needs a required name field !!!

#converts mongo to Json and formats _date properly
def mongoToJson(document):
    data = document.to_mongo()
    
    # Format all date fields (including audit fields)
    for key, value in data.items():
        if key in ['created_date', 'modified_date'] or key.find('_date') != -1:
            try:
                data[key] = document[key].strftime('%d.%m.%Y %H:%M')
            except:
                pass
        elif key.find('filter') != -1:
            try:
                i = 0
                for filter in document[key]:
                    if '_date' in filter['field']:
                        data[key][i]['value'] = document[key][i]['value'].strftime('%d.%m.%Y')
                    i += 1
            except:
                pass

    return json_util.dumps(data)

class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))

class Default(DynamicDocument):
    document_name = StringField(default='')
    document_url = StringField(default='')
    collection_name = StringField(default='')
    collection_url = StringField(default='')
    page_name_document = StringField(default='')
    page_name_collection = StringField(default='')
    collection_title = StringField(default='')
    menu = DictField(default={})
    
    def to_json(self):
        return mongoToJson(self)
    
def getDefaults(name):
    print(f"[DEBUG] getDefaults called with name={name}")
    defaults = None
    
    def create_document(doc_class):
        try:
            return doc_class()
        except Exception as e:
            print(f"[DEBUG] Error creating document instance: {str(e)}")
            return None
    
    if name == 'filter':
        defaults = ['filter', 'filter', 'Filter','Filter', Filter, create_document(Filter), 'filters']
    elif name == 'user' or name == 'users':
        defaults = ['user', 'users', 'User','Users', User, create_document(User), 'users']
    elif name == 'file' or name == 'files':
        defaults = ['file', 'files', 'File','Files', File, create_document(File), 'files']
    elif name == 'example' or name == 'examples':
        defaults = ['example', 'examples', 'Example','Example', Example, create_document(Example), 'examples']
    elif name == 'model' or name == 'models':
        defaults = ['model', 'models', 'Model','Models', Model, create_document(Model), 'models']
    elif name == 'history':
        defaults = ['history', 'history', 'History','Histories', History, create_document(History), 'history']
    elif name == 'prompt' or name == 'prompts':
        print("[DEBUG] Found prompt match")
        defaults = ['prompt', 'prompts', 'Prompt','Prompts', Prompt, create_document(Prompt), 'prompts']

    print(f"[DEBUG] defaults={defaults}")
    if defaults:
        try:
            d = Default()
            d.document_name = defaults[0]
            d.document_url = url_for('doc', name=defaults[0])
            d.collection_name = defaults[1]
            d.collection_url = url_for('list', collection=defaults[1])
            d.page_name_document = defaults[2]
            d.page_name_collection = defaults[3]
            d.collection_title = defaults[3]
            d.collection = defaults[4]
            d.document = defaults[5]
            if d.document is None:
                print("[DEBUG] Failed to create document instance")
                return None
            d.menu = {defaults[6]: 'open active', defaults[1]: 'open active'}
            print("[DEBUG] Created Default object successfully")
            return d
        except Exception as e:
            print(f"[DEBUG] Error creating Default object: {str(e)}")
            return None
    else:
        print("[DEBUG] No defaults found")
        return None

class AccessControlMixin:
    def can_access(self, user):
        """Default access control - allows access to all users"""
        return True
        
    def can_list(self, user):
        """Default list access control - allows listing to all users"""
        return True
        
    @classmethod
    def get_list_filter(cls, user):
        """Default list filter - no filtering"""
        return None

class User(UserMixin, AccessControlMixin, DynamicDocument):
    firstname = StringField(required=True)
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    pw_hash = StringField(required=True)
    csrf_token = StringField()
    salutation = StringField()
    comment = StringField()
    role = StringField(default='user')
    created_date = DateTimeField(default=datetime.now)
    modified_date = DateTimeField(default=datetime.now)
    created_by = StringField()
    modified_by = StringField()
    
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
        comment = {'name' :  'comment', 'label' : 'Kommentar', 'class' : '', 'type' : 'MultiLine','full_width':True}
        role = {'name' :  'role', 'label' : 'Rolle', 'class' : '', 'type' : 'SimpleListField','full_width':False}
        
        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [firstname,name,email,role] if current_user.is_admin else [firstname,name,email]
            
        #fields in the form
        fields = [email,salutation,firstname,name,comment]
        if current_user.is_admin:
            fields.append(role)
        return fields
    def to_json(self):
        return mongoToJson(self)
    def get_id(self):
        """Return the unique identifier for Flask-Login"""
        return str(self.id)

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def can_access(self, user):
        """Check if a user can access this specific user profile"""
        return user.is_admin or str(user.id) == str(self.id)

    def can_list(self, user):
        """Only admins can list all users"""
        return user.is_admin
        
    @classmethod
    def get_list_filter(cls, user):
        """Regular users can only see themselves"""
        if not user.is_admin:
            return {'_id': user.id}
        return None

class File(AccessControlMixin, AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=4)
    owner_id = StringField(required=True)
    category = StringField(default='')  # 'prompt' or 'history' or other categories
    meta = {'queryset_class': CustomQuerySet}
    
    def searchFields(self):
        return ['name']
    
    def fields(self, list_order=False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, "full_width": False}
        category = {'name': 'category', 'label': 'Kategorie', 'class': 'hidden-xs', 'type': 'TextField', "full_width": False}
        if list_order:
            return [name, category]
        return [name, category]
    
    def can_access(self, user):
        """Check if a user can access this file"""
        # Admin can access all files
        if user.is_admin:
            return True
            
        # If file is part of a prompt, anyone can access
        if self.category == 'prompt':
            return True
            
        # For history files or other categories, only owner can access
        return str(user.id) == str(self.owner_id)
    
    def can_list(self, user):
        """Users can list files"""
        return True
        
    @classmethod
    def get_list_filter(cls, user):
        """Filter logic for file listing"""
        if user.is_admin:
            return None  # Admins see all files
            
        # Regular users see:
        # 1. Their own files (including history files)
        # 2. Files associated with prompts
        return {
            '$or': [
                {'owner_id': str(user.id)},
                {'category': 'prompt'}
            ]
        }

    def save(self, *args, **kwargs):
        if not self.owner_id and current_user and current_user.is_authenticated:
            self.owner_id = str(current_user.id)
        return super().save(*args, **kwargs)

    def to_json(self):
        return mongoToJson(self)

class Filter(AccessControlMixin, AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=4)
    meta = {'queryset_class': CustomQuerySet}
    
    def searchFields(self):
        return ['name']
        
    def fields(self, list_order=False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True}
        category = {'name': 'category', 'label': 'Kategorie', 'class': '', 'type': 'SingleLine'}

        if list_order:
            return [name, category]
        return [name, category]

    def can_access(self, user):
        """Only admins can access filters"""
        return user.is_admin
        
    def can_list(self, user):
        """Only admins can list filters"""
        return user.is_admin
        
    @classmethod
    def get_list_filter(cls, user):
        """No additional filtering needed since access is already admin-only"""
        return None

    def to_json(self):
        return mongoToJson(self)

#example of a DynamicDocument with all available fields
#fields are then used in the form_elements.html to create the form
#the fields are then used in the db_crud.py to create the document
class Example(AccessControlMixin, AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=1)
    email = StringField(required=True, min_length=1)
    salutation = StringField(default='')
    firstname = StringField(default='')
    comment = StringField(default='')
    active = StringField(default='Off')
    newsletter = StringField(default='Off')
    event_date = DateField(default=None, null=True)
    age_int = IntField(default=None, null=True)
    salary_float = FloatField(default=None, null=True)
    ai_provider = StringField(default='')
    user_search = StringField(default='')
    files = StringField(default='')
    more_files = StringField(default='')
    link = StringField(default='')
    
    meta = {'queryset_class': CustomQuerySet}
    
    #these are the search fields for the search field in the document list overview page
    def searchFields(self):
        return ['name', 'email', 'firstname']
        
    def fields(self, list_order = False):
        # Field Types Documentation needs these corrections:
        
        # SingleLine: Text input field with 'input' class
        # MultiLine: Textarea field with 'textarea' class
        # CheckBox: Switch toggle with 'switch switch-primary' class
        # SimpleListField: Select dropdown with 'select max-w-sm' class
        # AdvancedListField: Enhanced select dropdown with 'select max-w-sm' class
        # Date: Flatpickr date picker with 'input max-w-sm' class (format: DD.MM.YYYY)
        # IntField: Number input with 'input' class
        # FloatField: Number input with 'input' class
        # FileField: File upload with 'input max-w-sm' class
        # ButtonField: Button with 'btn btn-primary' class
        # DocumentField: Search field with 'searchField' class and dropdown functionality

        # Additional Field Properties:
        # id: Used for element identification (required for all fields)
        # value: Current field value
        # value_id: (DocumentField only) ID of selected document
        # SimpleListField: (SimpleListField only) Array of {value, name} objects
        # AdvancedListField: (AdvancedListField only) Array of {value, name} objects

        #full_width is used to create a full width field in the form
        #if full_width is set to True, the field will take up the full width of the form
        #if full_width is set to False, the field will take up half the width of the form
        #required is used to make the field required in the form

        #list of fields for the form
        #SingleLine is a single line text field (input type text)
        #MultiLine is a multi line text field (input type textarea)
        #CheckBox is a checkbox field (input type checkbox, we are using a switch in the frontend)
        #SimpleListField is a simple list field (input type select)
        #AdvancedListField is a advanced list field (input type select with search)
        #DateField is a date field (input type date, this uses Flatpickr and flatpickr.js needs to be included in the frontend)
        #IntField is a integer field (input type number)
        #FloatField is a float field (input type number)
        #FileField is a file field (input type file)

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
        user_search = {'name': 'user_search', 'label': 'User', 'class': '', 'type': 'DocumentField', 'full_width': False, 'module': 'user', 'document_field': 'email'}
        files = {'name': 'files', 'label': 'Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}
        more_files = {'name': 'more_files', 'label': 'More Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}
        link = {'name': 'link', 'label': 'Link', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/d/testing'}

        #fields in the overview table of the collection
        if list_order:
            return [name, email, firstname]
        #fields in the form
        return [name, email, salutation, firstname, comment, active, newsletter, event_date, 
                age_int, salary_float, ai_provider, user_search, files, more_files, link]

    def to_json(self):
        return mongoToJson(self)

    def can_access(self, user):
        """Only admins can access examples"""
        return user.is_admin
        
    def can_list(self, user):
        """Only admins can list examples"""
        return user.is_admin
        
    @classmethod
    def get_list_filter(cls, user):
        """No additional filtering needed since access is already admin-only"""
        return None

#AI Documents
#AI Chat Bot Code
class Model(AccessControlMixin, AuditMixin, DynamicDocument):
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

    def can_access(self, user):
        """Only admins can access models"""
        return user.is_admin
        
    def can_list(self, user):
        """Only admins can list models"""
        return user.is_admin
        
    @classmethod
    def get_list_filter(cls, user):
        """No additional filtering needed since access is already admin-only"""
        return None

    def to_json(self):
        return mongoToJson(self)

class History(AccessControlMixin, AuditMixin, DynamicDocument):
    user_id = StringField(required=True)
    chat_started = IntField()
    messages = StringField()
    first_message = StringField()
    link = StringField(default='')
    file_ids = ListField(StringField())
    
    meta = {'queryset_class': CustomQuerySet}
    
    def searchFields(self):
        return ['messages', 'first_message']
    
    def fields(self, list_order=False):
        user_id = {'name': 'user_id', 'label': 'User ID', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': False}
        created_date = {'name': 'created_date', 'label': 'Date', 'class': '', 'type': 'Date', 'full_width': False}
        first_message = {'name': 'first_message', 'label': 'First Message', 'class': '', 'type': 'SingleLine', 'required': False, 'full_width': True}
        messages = {'name': 'messages', 'label': 'Messages', 'class': '', 'type': 'MultiLine', 'required': False, 'full_width': True}
        link = {'name': 'link', 'label': 'Chat', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/chat/history'}
        chat_started = {'name': 'chat_started', 'label': 'Chat Started', 'class': '', 'type': 'IntField', 'full_width': False}
        
        if list_order:
            # Show these fields in the list view
            return [created_date, first_message, link]
        # Show these fields in the edit form
        return [user_id, first_message, chat_started, messages, link]
    
    def can_access(self, user):
        """Check if a user can access this specific history entry"""
        return user.is_admin or str(user.id) == str(self.user_id)
    
    def can_list(self, user):
        """Users can always list their own history"""
        return True
        
    @classmethod
    def get_list_filter(cls, user):
        """Filter to only show user's own history"""
        print(f"[DEBUG] Getting list filter for user {user.id}")
        filter_dict = {'user_id': str(user.id)}
        print(f"[DEBUG] Returning filter: {filter_dict}")
        return filter_dict
    
    def save(self, *args, **kwargs):
        if not self.user_id and current_user and current_user.is_authenticated:
            self.user_id = str(current_user.id)
        return super().save(*args, **kwargs)

    def to_json(self):
        return mongoToJson(self)

class Prompt(AccessControlMixin, AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=1)
    welcome_message = StringField(required=True, min_length=1)
    system_message = StringField(required=True, min_length=1)
    prompt = StringField(required=True, min_length=1)
    link = StringField(default='')
    files = StringField(default='')

    meta = {
        'collection': 'prompts',
        'queryset_class': CustomQuerySet
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.link:
            self.link = '/chat/prompt'

    def searchFields(self):
        return ['name', 'system_message', 'prompt']

    def fields(self, list_order=False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        welcome_message = {'name': 'welcome_message', 'label': 'Welcome Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        system_message = {'name': 'system_message', 'label': 'System Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        prompt = {'name': 'prompt', 'label': 'Prompt', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        link = {'name': 'link', 'label': 'Use Prompt', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/chat/prompt'}
        files = {'name': 'files', 'label': 'Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}

        if list_order:
            return [link, name, prompt]
        return [name, welcome_message, system_message, prompt, files, link]

    def can_access(self, user):
        """Check if user can access this prompt"""
        return True  # All users can access prompts
        
    def can_list(self, user):
        """Check if user can list prompts"""
        return True  # All users can list prompts
        
    @classmethod
    def get_list_filter(cls, user):
        """No filtering needed for prompts"""
        return None  # No filtering - everyone sees all prompts

    def to_json(self):
        return mongoToJson(self)
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
            role=role,
            created_by='system',
            modified_by='system'
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

## helper.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json,os,csv,base64
from core.db_helper import searchDocuments, getFile, getDocumentsByID, getFilter, processDocuments, getFilterDict, getDocumentName
from core.db_crud import getDocument, updateDocument, createDocument, eraseDocument
from core.db_default import Setting, getDefaultList
from core.db_document import File, getDefaults

from pypdf import PdfReader
    
import datetime

from werkzeug.utils import secure_filename

from flask_login import current_user

import sys
sys.path.append('core')
from flask import redirect, url_for, flash
from bson import ObjectId

UPLOAD_FOLDER = 'temp'
DOCUMENT_FOLDER = 'documents'

import logging
current_path = os.path.dirname(os.path.realpath(__file__)) + '/'
# logging.basicConfig(format='%(asctime)s %(message)s\n\r',filename=current_path+'import_leads.log', level=logging.INFO,filemode='w')


from flask import render_template, redirect, url_for, jsonify, flash

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv','md'])

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
    recordsTotal = 0  # Initialize to 0 instead of None

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

def getList(name, request, filter=None, return_json=False):
    print(f"[DEBUG] getList called for {name}")
    default = getDefaults(name)
    if default == None:
        print("[DEBUG] No defaults found")
        return redirect(url_for('index'))
        
    # Check if user can list this collection
    if not default.document.can_list(current_user):
        print("[DEBUG] User cannot list this collection")
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
        
    data, prev, next, last, recordsTotal = initData()
    start,limit,end,search,id,filter_param,product_name,offer_id = getRequestData(request)
    
    filter_data = getFilter(default.document_name)
    mode = default.collection_name
    
    # Get access control filter for this document type
    access_filter = default.document.get_list_filter(current_user)
    print(f"[DEBUG] Access filter: {access_filter}")
    
    # Combine all filters
    combined_filter = {}
    if access_filter:
        combined_filter.update(access_filter)
    if filter:
        combined_filter.update(filter)
    if filter_param:
        filter_dict = getFilterDict(filter_param)
        combined_filter.update(filter_dict)
    
    print(f"[DEBUG] Combined filter: {combined_filter}")

    # Process the search query with combined filters
    # Pass empty dict if no filter to avoid "no filter found" error
    filter_to_use = combined_filter if combined_filter else {}
    mydata = searchDocuments(default.collection, default.document.searchFields(), 
                           start, limit, search, filter_to_use, product_name, mode)
    print(f"[DEBUG] Search results: {mydata}")

    processedData = loadData(mydata)
    if processedData:
        data, start, end, prev, next, recordsTotal, last = processedData
        print(f"[DEBUG] Found {recordsTotal} records")
        recordsTotal = int(recordsTotal) if recordsTotal is not None else 0
        if return_json:
            return jsonify({
                'status': 'ok',
                'message': 'success',
                'data': data,
                'recordsTotal': recordsTotal,
                'prev': prev,
                'next': next,
                'last': last,
                'start': start,
                'end': end
            })

    table_header = default.document.fields(list_order = True)
    table_content = tableContent(data, table_header)

    try:
        table = request.args.get('table')
        if table:
            return render_template('/base/collection/table.html',
                                 menu=default.menu,
                                 documents=data,
                                 prev=prev,
                                 next=next,
                                 limit=limit,
                                 start=start,
                                 total=recordsTotal,
                                 end=end,
                                 search=search,
                                 id=id,
                                 offer_id=offer_id,
                                 last=last,
                                 page_name_collection=default.page_name_collection,
                                 collection_name=default.collection_name,
                                 collection_url=default.collection_url,
                                 document_url=default.document_url,
                                 mode=mode,
                                 table_header=table_header,
                                 table_content=table_content,
                                 filter=filter_param,
                                 filter_data=filter_data,
                                 show_new_button=True,
                                 product_name=product_name)
    except:
        pass

    return render_template('/base/collection/collection.html',
                         menu=default.menu,
                         documents=data,
                         prev=prev,
                         next=next,
                         limit=limit,
                         start=start,
                         total=recordsTotal,
                         end=end,
                         search=search,
                         id=id,
                         offer_id=offer_id,
                         last=last,
                         page_name_collection=default.page_name_collection,
                         collection_name=default.collection_name,
                         collection_url=default.collection_url,
                         document_url=default.document_url,
                         mode=mode,
                         table_header=table_header,
                         table_content=table_content,
                         filter=filter_param,
                         filter_data=filter_data,
                         show_new_button=True,
                         product_name=product_name)

def handleDocument(name, id, request, return_json=False):
    try:
        default = getDefaults(name)
        if default is None:
            flash('Invalid document type', 'error')
            return redirect(url_for('index'))

        # For existing documents, verify access
        if id:
            doc = default.collection.objects(_id=ObjectId(id)).first()
            if not doc or not doc.can_access(current_user):
                flash('Access denied.', 'error')
                return redirect(url_for('list', collection=default.collection_name))

        # For new documents
        else:
            # Check if user can list (create new) documents of this type
            if not default.document.can_list(current_user):
                flash('Access denied.', 'error')
                return redirect(url_for('index'))
                
            # Set user_id for new documents if they use it
            if request.method == 'POST' and hasattr(default.document, 'user_id'):
                form_data = htmlFormToDict(request.form)
                form_data['user_id'] = str(current_user.id)
                request.form = form_data

        print(f"[DEBUG] Got defaults: document_name={default.document_name}, collection_name={default.collection_name}")
        mode = default.document_name

        # Initialize empty document data for new documents
        data = {}
        if not id:
            print("[DEBUG] Creating new document")
            try:
                # Get the document instance that was already created in getDefaults
                doc = default.document
                if doc is None:
                    raise Exception("Failed to get document instance")
                data = json.loads(doc.to_json())
                data['id'] = ''  # Empty ID for new document
                # Set user_id for new history documents
                if name == 'history':
                    data['user_id'] = str(current_user.id)
            except Exception as e:
                print(f"[DEBUG] Error initializing new document: {str(e)}")
                flash('Error creating new document', 'error')
                return redirect(url_for('index'))

        page = {
            'title': f"{'Add' if not id else 'Edit'} {default.page_name_document}",
            'collection_title': default.collection_title,
            'document_name': default.document_name,
            'document_url': default.document_url,
            'collection_url': default.collection_url,
            'document_title': default.page_name_document
        }
        
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
                data = createDocument(form_data, default.document, request)

            if (data['status'] == 'ok'):
                data = json.loads(data['data'])
                data['id'] = data['_id']['$oid']
                file_status = upload_files(request, default.collection_name, data['id'])
                print(f"[DEBUG] File status: {file_status}")
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
                    page = {'title': 'Edit ' + default.page_name_document, 'collection_title': default.collection_title, 'document_name': default.document_name, 'document_url': default.document_url, 'collection_url': default.collection_url, 'document_title': default.page_name_document}
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
                    return redirect(url_for('list', collection=default.collection_name))

        print("[DEBUG] Getting elements")
        elements = getElements(data, default.document)
        #print(f"[DEBUG] Elements: {elements}")
        return render_template('/base/document/form.html', elements=elements, menu=default.menu, page=page, document=data, mode=mode, category_fields=category_fields)
    except Exception as e:
        print(f"[DEBUG] Error in handleDocument: {str(e)}")
        flash('An error occurred while processing your request', 'error')
        return redirect(url_for('index'))

def deleteDocument(request):
    type = request.args.get('type')
    id = request.args.get('id')
    print(f"[DEBUG] deleteDocument called with type={type}, id={id}")
    
    if not id:
        print("[DEBUG] No ID provided")
        return {'status': 'error', 'message': 'no id'}
        
    # Special handling for file deletions
    if type == 'files':
        print(f"[DEBUG] Handling file deletion for id={id}")
        data = eraseDocument(id, File, File)
        print(f"[DEBUG] File deletion result: {data}")
    else:
        print(f"[DEBUG] Handling document deletion for type={type}, id={id}")
        default = getDefaults(type)
        if default == []:
            print(f"[DEBUG] No defaults found for type={type}")
            return {'status': 'error', 'message': 'no document found'}
        data = eraseDocument(id, default.document, default.collection)
        print(f"[DEBUG] Document deletion result: {data}")
        
    if data['status'] == 'ok':
        print("[DEBUG] Deletion successful")
        return {'status': 'ok', 'message': 'document deleted'}
    else:
        print(f"[DEBUG] Deletion failed: {data.get('message', 'unknown error')}")
        return {'status': 'error', 'message': data.get('message', 'document not deleted')}

def tableContent(documents, table_header):
    print(f"[DEBUG] Creating table content for {len(documents)} documents")
    tableContent = []

    for document in documents:
        print(f"[DEBUG] Processing document: {document}")
        tableRow = []
        for field in table_header:
            if field['name'] in document.keys() and 'id' in document.keys():
                value = document[field['name']]
                
                # Handle date fields
                if field['name'].find('_date') != -1:
                    if isinstance(value, dict) and '$date' in value:
                        date = value['$date']
                        value = datetime.datetime.fromtimestamp(date/1000).strftime('%d.%m.%Y')
                
                # Handle link fields for history
                if field['type'] == 'ButtonField':
                    link = f"{field['link']}/{document['id']}"
                    tableRow.append({
                        'name': field['name'],
                        'value': value,
                        'class': field['class'],
                        'id': document['id'],
                        'type': field['type'],
                        'link': link,
                        'label': field['label']
                    })
                else:
                    tableRow.append({
                        'name': field['name'],
                        'value': value,
                        'class': field['class'],
                        'id': document['id'],
                        'type': field['type'],
                        'label': field.get('label', field['name'])
                    })
            else:
                print(f"[DEBUG] Field {field['name']} not found in document or no id")
                tableRow.append('')
        
        if tableRow:  # Only add rows that have content
            tableContent.append(tableRow)
            
    print(f"[DEBUG] Created {len(tableContent)} table rows")
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

def fillElements(elements, data):
    # Check if data is empty or None
    if not data or not isinstance(data, dict):
        return elements
        
    for element in elements:
        if element['name'] in data:
            element['value'] = data[element['name']]
            if element['type'] == 'DocumentField':
                id = data.get(f"{element['name']}_id", '')  # Get ID with fallback to empty string
                if id and id != '0815':
                    element['value'] = getDocumentName(data[element['name']], element['module'], element['document_field'])
                    element['document_id'] = id
                    element['url'] = url_for('doc', name=element['module'], id=id)
                else:
                    element['value'] = ''

    return elements
    
def htmlFormToDict(form_data):
    if not form_data:
        return {}
        
    try:
        # Handle ImmutableMultiDict from Flask
        if hasattr(form_data, 'getlist'):
            return {key: form_data.getlist(key)[0] for key in form_data.keys()}
        # Handle regular dict
        elif isinstance(form_data, dict):
            return form_data
        # Handle list of dicts with name/value pairs
        elif isinstance(form_data, list):
            return {item['name']: item['value'] for item in form_data if 'name' in item and 'value' in item}
        else:
            print(f"[DEBUG] Unexpected form_data type: {type(form_data)}")
            return {}
    except Exception as e:
        print(f"[DEBUG] Error in htmlFormToDict: {str(e)}")
        return {}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_files(request, category='', document_id=''):
    status = {'status': 'ok', 'files': []}

    if request.method == 'POST':
        # Get base path for consistent path handling
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # Extract element IDs directly from the file input names
        element_ids = [key.split('files_', 1)[1] for key in request.files.keys()]

        for element_id in element_ids:
            status[element_id] = []  # Initialize list for this element_id
            files = request.files.getlist(f'files_{element_id}')
            if not files or files[0].filename == '':
                continue  # Skip if no files are selected

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    try:
                        # Use consistent path structure
                        relative_path = os.path.join('core', 'documents', category) if category else os.path.join('core', UPLOAD_FOLDER)
                        absolute_path = os.path.join(base_path, relative_path)
                        
                        print(f"[DEBUG] Upload path (absolute): {absolute_path}")
                        print(f"[DEBUG] Upload path (relative): {relative_path}")

                        if not os.path.exists(absolute_path):
                            print(f"[DEBUG] Creating directory: {absolute_path}")
                            os.makedirs(absolute_path)

                        file_type = filename.rsplit('.', 1)[1]
                        fileDB = File(
                            name=filename, 
                            path=relative_path,  # Store relative path
                            category=category, 
                            file_type=file_type, 
                            document_id=document_id, 
                            element_id=element_id,
                            user_id=str(current_user.id)  # Set the user_id to current user's ID
                        )
                        fileDB.save()
                        fileID = getDocumentID(fileDB)

                        file_save_path = os.path.join(absolute_path, f"{fileID}.{file_type}")
                        print(f"[DEBUG] Saving file to: {file_save_path}")
                        file.save(file_save_path)

                        status[element_id].append({
                            'id': fileID, 
                            'name': filename, 
                            'path': os.path.join(relative_path, f"{fileID}.{file_type}")
                        })

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

#only pdf/txt files are supported for now
def prepare_context_from_files(files):
    result = {
        "status": "error",
        "data": "",
        "character_count": 0
    }
    
    print(f"[DEBUG] prepare_context_from_files called with {len(files)} files")
    
    if not files:
        print("[DEBUG] No files provided")
        result["status"] = "error"
        result["data"] = "No files provided"
        return result

    try:
        combined_text = []
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        print(f"[DEBUG] Base path for file reading: {base_path}")
        
        for file in files:
            try:
                print(f"[DEBUG] Processing file: {file.get('name', 'Unknown')}")
                # Convert MongoDB document to dict if needed
                if hasattr(file, 'to_mongo'):
                    file = file.to_mongo().to_dict()
                    print("[DEBUG] Converted MongoDB document to dict")
                
                # Get file ID consistently
                if isinstance(file.get('_id'), dict) and '$oid' in file['_id']:
                    file_id = file['_id']['$oid']
                elif isinstance(file.get('_id'), str):
                    file_id = file['_id']
                else:
                    file_id = str(file['_id'])
                print(f"[DEBUG] File ID: {file_id}")
                
                # Build full file path
                file_path = os.path.join(base_path, file['path'], f"{file_id}.{file['file_type'].lower()}")
                print(f"[DEBUG] Full file path: {file_path}")
                
                if not os.path.exists(file_path):
                    print(f"[DEBUG] File not found at path: {file_path}")
                    continue
                
                print(f"[DEBUG] Reading file: {file['name']}")
                file_content = f"\nContent of File: {file['name']}\n{'='*50}\n"
                
                if file['file_type'].lower() == 'pdf':
                    try:
                        with open(file_path, 'rb') as pdf_file:
                            pdf_reader = PdfReader(pdf_file)
                            print(f"[DEBUG] PDF has {len(pdf_reader.pages)} pages")
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                text = page.extract_text()
                                if text:
                                    print(f"[DEBUG] Extracted text from page {page_num + 1}")
                                    text = ' '.join(text.split())
                                    text = text.replace(' .', '.').replace(' ,', ',')
                                    paragraphs = text.split('\n')
                                    formatted_text = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
                                    file_content += formatted_text + "\n\n"
                                else:
                                    print(f"[DEBUG] No text found on page {page_num + 1}")
                                    file_content += "[No text found on this page]\n\n"
                    except Exception as e:
                        print(f"[DEBUG] Error reading PDF {file['name']}: {str(e)}")
                        continue
                        
                elif file['file_type'].lower() == 'txt':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as txt_file:
                            text = txt_file.read()
                            print(f"[DEBUG] Read {len(text)} characters from text file")
                            file_content += text
                    except Exception as e:
                        print(f"[DEBUG] Error reading TXT {file['name']}: {str(e)}")
                        continue
                        
                file_content += f"\n{'='*50}\n"
                print(f"[DEBUG] Added {len(file_content)} characters of content")
                combined_text.append(file_content)
                
            except Exception as e:
                print(f"[DEBUG] Error processing file: {str(e)}")
                continue
            
        if combined_text:
            result["status"] = "ok"
            result["data"] = "\n".join(combined_text)
            result["character_count"] = len(result["data"])
            print(f"[DEBUG] Successfully combined {len(combined_text)} files with total {result['character_count']} characters")
        else:
            print("[DEBUG] No content could be extracted from files")
            result["status"] = "error"
            result["data"] = "No content could be extracted from files"
            
    except Exception as e:
        print(f"[DEBUG] Error in prepare_context_from_files: {str(e)}")
        result["status"] = "error"
        result["data"] = f"Error processing files: {str(e)}"

    return result

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_file(file, category='history'):
    """Handle file upload for chat functionality and return file context"""
    try:
        if not file:
            print("[DEBUG] No file object provided")
            return {'status': 'error', 'message': 'No file provided'}
            
        if not hasattr(file, 'filename'):
            print("[DEBUG] File object has no filename attribute")
            return {'status': 'error', 'message': 'Invalid file object'}
            
        if not file.filename:
            print("[DEBUG] Empty filename")
            return {'status': 'error', 'message': 'No file selected'}
            
        print(f"[DEBUG] Processing file: {file.filename}")
        filename = secure_filename(file.filename)
        
        # More robust file type extraction
        try:
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
            if not file_type:
                print("[DEBUG] Could not extract file type")
                return {'status': 'error', 'message': 'Could not determine file type'}
        except Exception as e:
            print(f"[DEBUG] Error extracting file type: {str(e)}")
            return {'status': 'error', 'message': 'Invalid file type'}
            
        if not allowed_file(filename):
            print(f"[DEBUG] File type {file_type} not allowed")
            return {'status': 'error', 'message': f'File type {file_type} not allowed'}
        
        if file_type not in ['pdf', 'txt', 'jpeg', 'jpg', 'png']:
            print(f"[DEBUG] Unsupported file type: {file_type}")
            return {'status': 'error', 'message': 'Only PDF, TXT, and image files are supported'}
            
        # Get base path and construct relative/absolute paths consistently
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        relative_path = os.path.join('core', 'documents', category)
        absolute_path = os.path.join(base_path, relative_path)
        
        print(f"[DEBUG] Upload base path: {base_path}")
        print(f"[DEBUG] Upload relative path: {relative_path}")
        print(f"[DEBUG] Upload absolute path: {absolute_path}")
        
        if not os.path.exists(absolute_path):
            print(f"[DEBUG] Creating directory: {absolute_path}")
            os.makedirs(absolute_path)
            
        fileDB = File(
            name=filename,
            path=relative_path,
            category=category,
            file_type=file_type,
            user_id=str(current_user.id)
        )
        fileDB.save()
        fileID = str(fileDB.id)
        
        file_save_path = os.path.join(absolute_path, f"{fileID}.{file_type}")
        print(f"[DEBUG] Saving file to: {file_save_path}")
        file.save(file_save_path)
        
        response = {
            'status': 'ok',
            'file_id': fileID,
            'filename': filename,
            'name': filename,
            'file_type': file_type,
            'type': file_type,
            'path': relative_path
        }
        
        # Always get context for text-based files
        if file_type in ['pdf', 'txt']:
            try:
                # Convert fileDB to dict format expected by prepare_context_from_files
                file_dict = {
                    '_id': fileID,
                    'name': filename,
                    'path': relative_path,
                    'file_type': file_type
                }
                
                print(f"[DEBUG] Getting context for file: {file_dict}")
                context = prepare_context_from_files([file_dict])
                
                if context['status'] == 'ok':
                    print(f"[DEBUG] Successfully extracted context with {context['character_count']} characters")
                    response['content'] = context['data']
                    response['character_count'] = context['character_count']
                else:
                    print(f"[DEBUG] Context extraction failed: {context['data']}")
                    response['content'] = f"[Error extracting content from {filename}]"
            except Exception as e:
                print(f"[DEBUG] Error getting file context: {str(e)}")
                response['content'] = f"[Error processing {filename}: {str(e)}]"
                
        # Add base64 for images
        elif file_type in ['jpeg', 'jpg', 'png']:
            try:
                response['base64_image'] = encode_image(file_save_path)
            except Exception as e:
                print(f"[DEBUG] Error encoding image: {str(e)}")
                response['base64_image'] = None
                
        print(f"[DEBUG] Upload successful, returning response: {response}")
        return response
        
    except Exception as e:
        print(f"[DEBUG] Upload error: {str(e)}")
        return {'status': 'error', 'message': str(e)}
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
mongodb_uri = os.getenv('MONGODB_URI')

# Connect to your MongoDB database with SSL certificate verification
#connect(host=mongodb_uri, tlsCAFile=certifi.where())
connect(host=mongodb_uri)

# class User(DynamicDocument):
#   user_name = StringField()
#   email = StringField(required=True)

# user = User(user_name="John Doe", email="mynbi@example.com")

# user.save()
```

## ai_insert_models.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_document import Model
from core.db_connect import *

models = [
  # {'provider':'openai','model':'gpt-4o','name':'OpenAI - GPT-4o'},
  # {'provider':'openai','model':'gpt-4o-mini','name':'OpenAI - GPT-4o Mini'},
  {'provider':'perplexity','model':'sonar-deep-research','name':'US - Perplexity - Sonar Deep Research'},
  {'provider':'perplexity','model':'sonar-reasoning-pro','name':'US - Perplexity - Sonar Reasoning Pro'},
  {'provider':'perplexity','model':'sonar-reasoning','name':'US - Perplexity - Sonar Reasoning'},
  {'provider':'perplexity','model':'sonar-pro','name':'US - Perplexity - Sonar Pro'},
  {'provider':'perplexity','model':'sonar','name':'US - Perplexity - Sonar'},
  {'provider':'perplexity','model':'r1-1776','name':'US - Perplexity - DeepSeek R1'},
  {'provider':'azure','model':'gpt-4o-sweden-02','name':'EU - Azure - GPT-4o - Sweden'},
  {'provider':'azure','model':'gpt-4o-mini-sweden-02','name':'EU - Azure - GPT-4o Mini - Sweden'},
  # {'provider':'azure','model':'o1-mini','name':'EU Azure - o1-mini Sweden'},
  ]

# Delete existing models
Model.objects.delete()

# Current timestamp for creation date
now = datetime.datetime.now()

# Insert models with only creation audit fields
for model_data in models:
    model = Model(
        provider=model_data['provider'],
        model=model_data['model'],
        name=model_data['name'],
        created_date=now,
        created_by='system'
    )
    # Use save(force_insert=True) to ensure it's treated as a new document
    model.save(force_insert=True)

print("Models inserted successfully with creation audit fields.")
```

## __init__.py

```
# This file can be empty, it just marks the directory as a Python package
```

## ai_search.py

```
import os
import requests
from datetime import datetime
import dotenv

from dotenv import load_dotenv
load_dotenv()

def search(question, num_results=10, days=5, start=0):
    # Read API key and cx from environment variables
    google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")

    # API endpoint and parameters
    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {
        "q": question,
        "key": google_search_api_key,
        "cx": google_cse_id,
        "lr": "lang_de",
        "gl": "de",
        "dateRestrict" : "d" + str(days),
        "num": num_results,  # Get the specified number of search results
        "googlehost": "google.de",  # Search on google.de domain
        "cr": "countryDE",  # Restrict search to Germany
        "start": start  # The index to start the search results from
    }

    # Make request to API and extract news results
    response = requests.get(url, params=params).json()

    # Check if the "items" key exists in the response
    if "items" in response:
        results = response["items"]
    else:
        results = []

    # Extract article URL, title, snippet, source, and image URL for each search result and store in list
    news_results = []
    for result in results:
        news_result = {
            "url": result["link"],
            "title": result["title"],
            "snippet": result["snippet"],
            "source": result["displayLink"]
        }

        print (news_result['title'])

        # Extract image URL if available
        if "pagemap" in result and "cse_image" in result["pagemap"]:
            news_result["image_url"] = result["pagemap"]["cse_image"][0]["src"]

        news_results.append(news_result)

    return news_results

search("Wann spielt der FCBayern?")
```

## Readme.md

```
# AI Chat System Documentation

## Prerequisites

- OpenAI API key or Anthropic API key required for operation
- Set your API keys in the `.env` file

## System Architecture

### Backend Components (`/ai`)

- `ai_chat.py`: Main chat blueprint and route handlers
- `ai_llm_helper.py`: LLM integration and response processing
- `ai_insert_models.py`: Database models initialization
- `__init__.py`: Package initialization

### Frontend Components

#### Templates (`/templates/chat/`)

- `chat.html`: Main chat interface layout
- `chat_ui.html`: Chat UI components and structure
- `chat_messages.html`: Message container template
- `chat_messages_rendered.html`: Rendered messages view
- `bot_message_template.html`: AI response formatting
- `user_message_template.html`: User message formatting
- `code_block_template.html`: Code snippet display
- `chat_prompts.html`: System prompts management

#### JavaScript (`/static/chat/`)

- `chat_core.js`: Core chat functionality, HTMX interactions, and UI handlers

## Database Integration

- Chat models and schemas defined in `core/db_document.py`
- Stores message history, prompts, and system configurations

## Setup Instructions

1. Configure your environment variables in `.env`
2. Import the chat blueprint in `app.py`:
   ```python
   from ai.ai_chat import dms_chat
   app.register_blueprint(dms_chat, url_prefix='/chat')
   ```

## Features

- Real-time chat interface with AI models
- Code snippet highlighting and formatting
- Message history persistence
- Custom prompt management
- HTMX-powered dynamic updates
```

## ToDo.md

```
check the chat.html and the chat_core.js file for things that are not neccesary anymore
enable the model selection
```

## ai_chat.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, render_template, Response, jsonify
import time, sys, json
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user

# Append the db directory to the system path for module imports
sys.path.append('db')

from core.helper import handleDocument, prepare_context_from_files, upload_file
from core.db_document import File, History, Model, Prompt

from core.db_connect import *

from ai.ai_llm_helper import llm_call

# Import the getConfig function from db_chat.py
#from db.db_chat import getConfig

# Create a Blueprint for the chat functionality
dms_chat = Blueprint('dms_chat', __name__)

# Initialize CSRF protection for the blueprint
csrf = CSRFProtect()


def getConfig():
    system_message = """Du bist ein hilfreicher Assistent! Antworte immer auf Deutsch! 

Formatiere deine Antworten mit Markdown:
- Überschriften mit # für Haupttitel und ## für Untertitel
- **Fettschrift** für wichtige Begriffe
- *Kursivschrift* für Betonungen
- Listen mit * für Aufzählungen
- Nummerierte Listen mit 1. 2. 3.
- Verschachtelte Listen durch Einrücken mit 2 Leerzeichen:
  * Hauptpunkt
    * Unterpunkt
    * Weiterer Unterpunkt
  * Nächster Hauptpunkt
- Verschachtelte nummerierte Listen:
  1. Erster Punkt
     1. Unterpunkt 1.1
     2. Unterpunkt 1.2
  2. Zweiter Punkt
- Gemischte verschachtelte Listen:
  * Hauptpunkt
    1. Nummerierter Unterpunkt
    2. Weiterer nummerierter Unterpunkt
  * Nächster Hauptpunkt
    * Unnummerierter Unterpunkt
- `Inline-Code` für kurze Codebeispiele
- Links mit [Text](URL)
- ~~Durchgestrichen~~ für nicht mehr gültiges

Beispiel einer formatierten Antwort:
# Haupttitel
## Untertitel
Dies ist ein Absatz mit **wichtigen** und *betonten* Worten.
* Erster Listenpunkt
* Zweiter Listenpunkt mit `Code`
  * Ein Unterpunkt
  * Noch ein Unterpunkt
* Dritter Punkt mit [Link](https://example.com)

1. Erster nummerierter Punkt
   1. Nummerierter Unterpunkt
   2. Weiterer nummerierter Unterpunkt
2. Zweiter nummerierter Punkt

Wenn du längeren Code generierst, dann setze den Code in dreifache Backticks."""

    welcome_message = "Hallo wie kann ich helfen?"
    messages = []
    models = json.loads(Model.objects().to_json())
    print (models)

    return {
        "system_message": system_message,
        "welcome_message": welcome_message,
        'messages': messages,
        'models': models,
        'use_prompt_template': 'False'
    }


# Define the chat route
@dms_chat.route('/prompt/<prompt_id>')
@dms_chat.route('/history/<history_id>')
@dms_chat.route('/', methods=['GET', 'POST'])
@login_required
def chat(prompt_id=None, history_id=None):
    config = getConfig()

    # Add user information to config
    config['username'] = current_user.email
    config['user_id'] = str(current_user.id)
    config['is_admin'] = current_user.is_admin
    config['firstname'] = current_user.firstname
    config['name'] = current_user.name

    config['chat_started'] = int(time.time())
    config['history'] = []
    config['latest_prompts'] = []
    config['using_context'] = False
    config['context_files'] = []
    config['file_ids'] = []

    if prompt_id:
        prompt = json.loads(
            handleDocument('prompt', prompt_id, request, return_json=True))
        files = json.loads(File.objects(document_id=prompt['id']).to_json())
        
        #only pdf/txt files are supported for now
        context = prepare_context_from_files(files)
        if context['status'] == "ok":
            if prompt['system_message'].find("{context}") != -1:
                prompt['system_message'] = prompt['system_message'].replace(
                    "{context}", context['data'])
                config['using_context'] = True
                config['context_files'] = [f['name'] for f in files]
                config['file_ids'] = [f['_id']['$oid'] for f in files]

        config['messages'] = []
        
        # Add system message with file attachments if files exist
        system_message = {
            'role': 'system',
            'content': prompt['system_message']
        }
        if files:
            system_message['attachments'] = [{
                'type': 'file',
                'id': f['_id']['$oid'],
                'name': f['name'],
                'file_type': f['file_type'],
                'timestamp': int(time.time())
            } for f in files]
        config['messages'].append(system_message)
        
        # Add user prompt message
        config['messages'].append({
            'role': 'user',
            'content': prompt['prompt']
        })
        
        config['use_prompt_template'] = 'True'
        config['welcome_message'] = prompt['welcome_message']

    elif history_id:
        history = json.loads(
            handleDocument('history', history_id, request, return_json=True))
        config['chat_started'] = history['chat_started']
        config['messages'] = json.loads(history['messages'])
    else:
        chat_history = History.objects(user_id=str(current_user.id)).order_by('-id').limit(3)
        if chat_history:
            config['history'] = chat_history
        latest_prompts = Prompt.objects().order_by('-id').limit(3)
        if latest_prompts:
            config['latest_prompts'] = latest_prompts

    return render_template('/chat/chat.html', config=config)


@dms_chat.route('/stream', methods=['POST'])
def stream():
    data = request.get_json()
    response_stream = llm_call(data['messages'], data['model'])
    return Response(response_stream, mimetype='text/event-stream')


@dms_chat.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    chat_started = request.form.get('chat_started')
    messages = request.form.get('messages')
    
    print(f"[DEBUG] Saving chat for user {current_user.id} started at {chat_started}")
    print(f"[DEBUG] Messages to save: {messages}")

    chat_history = History.objects(user_id=str(current_user.id),
                                 chat_started=chat_started)
    print(f"[DEBUG] Found {len(chat_history)} existing chat(s)")
    
    if len(chat_history) == 1:
        print("[DEBUG] Updating existing chat")
        chat_history = chat_history[0]
        chat_history.messages = messages
        
        # Parse messages once
        parsed_messages = json.loads(messages)
        
        # Update first message if we find a user message and current first message is default
        if chat_history.first_message == "Neuer Chat":
            for msg in parsed_messages:
                if msg.get('role') == 'user' and isinstance(msg.get('content'), str):
                    chat_history.first_message = msg['content']
                    print(f"[DEBUG] Updated first message to: {msg['content']}")
                    break
        
        # Collect file IDs
        file_ids = []
        for msg in parsed_messages:
            if 'attachments' in msg:
                for attachment in msg['attachments']:
                    file_ids.append(attachment['id'])
        chat_history.file_ids = file_ids
        chat_history.save()
        return 'Chat aktualisiert!'
    else:
        print("[DEBUG] Creating new chat")
        chat_history = History()
        chat_history.user_id = str(current_user.id)
        chat_history.chat_started = chat_started
        chat_history.messages = messages
        chat_history.first_message = "Neuer Chat"  # Set default title
        
        # Parse messages once
        parsed_messages = json.loads(messages)
        
        # Set first message to first user message if one exists
        for msg in parsed_messages:
            if msg.get('role') == 'user' and isinstance(msg.get('content'), str):
                chat_history.first_message = msg['content']
                print(f"[DEBUG] Set first message to: {msg['content']}")
                break
        
        # Collect file IDs
        file_ids = []
        for msg in parsed_messages:
            if 'attachments' in msg:
                for attachment in msg['attachments']:
                    file_ids.append(attachment['id'])
        chat_history.file_ids = file_ids
        
        chat_history.save()
        print(f"[DEBUG] New chat created with first message: {chat_history.first_message}")
        return 'Neuer Chat erstellt!'


# @dms_chat.route('/chat/list_chat_history', methods=['GET'])
# def list_chat_history_endpoint():
#     chat_history = list_chat_history()
#     print(chat_history)
#     return render_template('/chat/chat_history.html',
#                            chat_history=chat_history)


@dms_chat.route('/load_ui/<template>')
def load_ui(template):
    return render_template(template)

@dms_chat.route('/upload', methods=['POST'])
@login_required
def upload_chat_file():
    try:
        if 'file' not in request.files:
            print("[DEBUG] No file part in request")
            return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            print("[DEBUG] No file selected")
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
            
        print(f"[DEBUG] Processing upload for file: {file.filename}")
        result = upload_file(file)
        print(f"[DEBUG] Upload result: {result}")
        
        if result.get('status') == 'ok':
            # Add file metadata to the response
            result['attachment'] = {
                'type': 'file',
                'id': result['file_id'],
                'name': result['filename'],  # Use filename from response
                'file_type': result['file_type'],  # Use file_type from response
                'timestamp': int(time.time())
            }
            print(f"[DEBUG] Returning successful response: {result}")
            return jsonify(result)
        else:
            print(f"[DEBUG] Upload failed: {result.get('message', 'Unknown error')}")
            return jsonify(result), 400
            
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        return jsonify({'status': 'error', 'message': error_msg}), 500

@dms_chat.route('/nav_items', methods=['GET'])
def get_nav_items():
    # Get latest history items for current user only, ordered by last modified date
    history = History.objects(user_id=str(current_user.id)).order_by('-modified_date', '-id').limit(15)
    # Get latest prompts
    prompts = Prompt.objects().order_by('-id').limit(5)
    
    return jsonify({
        'history': json.loads(history.to_json()),
        'prompts': json.loads(prompts.to_json())
    })

@dms_chat.route('/delete_all_history', methods=['POST'])
@login_required
def delete_all_history():
    try:
        # Get base path for constructing absolute paths
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        print(f"[DEBUG] Base path for deletion: {base_path}")
        
        # Get all prompts' file IDs to preserve them
        all_prompts = Prompt.objects()
        preserved_file_ids = set()
        for prompt in all_prompts:
            # Get files associated with this prompt
            prompt_files = File.objects(document_id=str(prompt.id))
            for file in prompt_files:
                preserved_file_ids.add(str(file.id))
        print(f"[DEBUG] Found {len(preserved_file_ids)} files to preserve from prompts")
        
        # Delete all history documents for the current user
        histories = History.objects(user_id=str(current_user.id))
        print(f"[DEBUG] Found {histories.count()} history documents for user {current_user.id}")
        deleted_count = 0
        failed_count = 0
        preserved_count = 0
        
        for history in histories:
            try:
                print(f"[DEBUG] Processing history document: {history.id}")
                print(f"[DEBUG] File IDs to process: {history.file_ids}")
                
                # Process associated files first
                for file_id in history.file_ids:
                    try:
                        # Skip if file is used by a prompt
                        if file_id in preserved_file_ids:
                            print(f"[DEBUG] Preserving file {file_id} as it's used by a prompt")
                            preserved_count += 1
                            continue
                            
                        file_doc = File.objects(id=file_id).first()
                        if file_doc:
                            # Check if user has permission to delete this file
                            if not file_doc.can_access(current_user):
                                print(f"[DEBUG] Access denied for file deletion: {file_id}")
                                continue
                                
                            # Construct absolute path using the relative path stored in DB
                            file_path = os.path.join(base_path, file_doc.path, f"{str(file_id)}.{file_doc.file_type}")
                            print(f"[DEBUG] Attempting to delete file: {file_path}")
                            
                            # Delete file from disk if it exists
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"[DEBUG] Successfully deleted file from disk: {file_path}")
                            
                            # Delete file document from database
                            file_doc.delete()
                            print(f"[DEBUG] Successfully deleted file document from database: {file_id}")
                    except Exception as e:
                        print(f"[DEBUG] Error deleting file {file_id}: {str(e)}")
                        failed_count += 1
                
                # Delete the history document
                history.delete()
                deleted_count += 1
                print(f"[DEBUG] Successfully deleted history: {history.id}")
                
            except Exception as e:
                print(f"[DEBUG] Error processing history {history.id}: {str(e)}")
                failed_count += 1
                continue
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully deleted {deleted_count} history documents. Preserved {preserved_count} prompt files. Failed to delete {failed_count} items.',
            'deleted_count': deleted_count,
            'preserved_count': preserved_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        print(f"[DEBUG] Error in delete_all_history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error deleting history: {str(e)}'
        }), 500
```

## ai_llm_helper.py

```
import os,json,sys
from openai import OpenAI
from openai import AzureOpenAI
import anthropic

from dotenv import load_dotenv
load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
together_api_key=os.getenv("TOGETHER_API_KEY")
anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
perplexity_api_key=os.getenv("PERPLEXITY_API_KEY")

azure_api_version = os.getenv('AZURE_API_VERSION_SE_02')
azure_api_key = os.getenv('AZURE_API_KEY_MN_SE_02')
azure_endpoint = os.getenv('AZURE_API_BASE_MN_SE_02')
azure_deployment = os.getenv('AZURE_API_MODEL_MN_SE_02')

#Notice: I was not able to have a function with streaming (using yield) and no streaming (return) at the same time.

def llm_call_stream(messages, model):
    if model['provider'] == 'anthropic':
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=model['model'],
            max_tokens=1000,
            temperature=0,
            system=messages[0]['content'],
            messages=messages[1:],
            stream=True
        )
        input_tokens = 0
        output_tokens = 0
        accumulated_text = ""
        for line in response:
            print(line.type)
            if line.type == 'message_start':
                input_tokens = line.message.usage.input_tokens
            elif line.type == 'message_delta':
                output_tokens = line.usage.output_tokens
            elif line.type == 'content_block_delta':
                if line.delta.text:
                    accumulated_text += line.delta.text
                    yield line.delta.text.encode('utf-8')
        if accumulated_text:
            yield " ".encode('utf-8')
        yield f"###STOP###{json.dumps({'prompt_tokens': input_tokens, 'completion_tokens': output_tokens, 'total_tokens': input_tokens + output_tokens})}".encode('utf-8')
    else:
        if model['provider']=='together':
            client = OpenAI(api_key=together_api_key,base_url='https://api.together.xyz/v1')
        elif model['provider']=='deepseek':
            client = OpenAI(api_key=deepseek_api_key,base_url='https://api.deepseek.com')
        elif model['provider']=='perplexity':
            client = OpenAI(api_key=perplexity_api_key,base_url='https://api.perplexity.ai')
        elif model['provider']=='openai':
            client = OpenAI(api_key=openai_api_key)
        elif model['provider']=='azure':
            client = AzureOpenAI(azure_endpoint=azure_endpoint,api_key=azure_api_key,api_version=azure_api_version)

        response = client.chat.completions.create(
            model=model['model'],
            messages=messages,
            stream=True
        )

        accumulated_text = ""
        citations = []
        for line in response:
            # Skip empty chunks or chunks without choices
            if not hasattr(line, 'choices') or len(line.choices) == 0:
                continue
                
            # Handle content if present
            if hasattr(line.choices[0], 'delta') and hasattr(line.choices[0].delta, 'content'):
                if line.choices[0].delta.content:
                    accumulated_text += line.choices[0].delta.content
                    yield line.choices[0].delta.content.encode('utf-8')
            
            # Handle completion
            if hasattr(line.choices[0], 'finish_reason') and line.choices[0].finish_reason in ['eos', 'stop']:
                if accumulated_text:
                    yield " ".encode('utf-8')
                try:
                    response_data = line.model_dump()
                    if 'citations' in response_data:
                        citations = response_data['citations']
                        print("Citations found:", citations)  # Print citations when found
                    usage_data = line.usage.model_dump()
                    usage_data['citations'] = citations
                    yield f"###STOP###{json.dumps(usage_data)}".encode('utf-8')
                except:
                    yield "###STOP###null".encode('utf-8')

def llm_call_no_stream(messages, model):
    if model['provider'] == 'anthropic':
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=model['model'],
            max_tokens=1000,
            temperature=0,
            system=messages[0]['content'],
            messages=messages[1:],
            stream=False
        )
        return response.content[0].text
    else:
        if model['provider']=='together':
            client = OpenAI(api_key=together_api_key,base_url='https://api.together.xyz/v1')
        elif model['provider']=='deepseek':
            client = OpenAI(api_key=deepseek_api_key,base_url='https://api.deepseek.com')
        elif model['provider']=='openai':
            client = OpenAI(api_key=openai_api_key)
        elif model['provider']=='azure':
            client = AzureOpenAI(azure_endpoint=azure_endpoint,api_key=azure_api_key,api_version=azure_api_version)

        response = client.chat.completions.create(
            model=model['model'],
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content

def llm_call(messages, model, stream=True):
    if stream:
        return llm_call_stream(messages, model)
    return llm_call_no_stream(messages, model)
```

## ai_test.py

```
from dotenv import load_dotenv
import os
import sys

# Add parent directory to Python path to find core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ai_llm_helper import llm_call
from core.db_document import History, Prompt, File, Model, Example, User

messages = [
    {"role": "system", "content": "Du bist ein hilfreicher Assistent"},
    {"role": "user", "content": "Wann spielt der FC Bayern?"}
]

#model = {'provider':'azure','model':'gpt-4o-sweden-02','name':'gpt-4o-sweden-02'}
#model = {'provider':'openai','model':'gpt-4o-mini','name':'gpt-4o-mini'}
model = {'provider':'perplexity','model':'sonar-pro','name':'Perplexity - Sonar Reasoning Pro'}
#model = {'provider':'anthropic','model':'claude-3-5-sonnet-20240620','name':'claude-3.5-sonnet'}

#Stream response handling
response = llm_call(messages, model, stream=True)
for chunk in response:
    print(chunk)

# History.objects().delete()
# Prompt.objects().delete()
# File.objects().delete()

# user = User.objects(email='').first()
# user.role = 'admin'
# user.save()
```

## ai_perplexity.py

```
import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "llama-3.1-sonar-small-128k-online",
    "messages": [
        {
            "role": "system",
            "content": "Du bist ein hilfreicher Assistent"
        },
        {
            "role": "user",
            "content": "Wie hat der FC Bayern gestern gespielt?"
        }
    ],
    "top_k": 0,
    "stream": False
}
headers = {
    "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)
```

# config

```
{
  "filter": {
    "document_name": "filter",
    "collection_name": "filter",
    "page_name_document": "Filter",
    "page_name_collection": "Filter",
    "menu": {
      "settings": "open active",
      "filter": "open active"
    }
  },
  "user": {
    "document_name": "user",
    "collection_name": "users",
    "page_name_document": "User",
    "page_name_collection": "Users",
    "menu": {
      "users": "open active",
      "users": "open active"
    }
  },
  "file": {
    "document_name": "file",
    "collection_name": "files",
    "page_name_document": "File",
    "page_name_collection": "Files",
    "menu": {
      "files": "open active",
      "files": "open active"
    }
  },
  "example": {
    "document_name": "example",
    "collection_name": "examples",
    "page_name_document": "Example",
    "page_name_collection": "Example",
    "menu": {
      "examples": "open active",
      "examples": "open active"
    }
  }
}
```

## chat/chat_core.js

```
let isInCodeBlock = false;
let currentCodeElement = null;
let stop_stream = false;
let uploadedFilesCount = 0;
let currentMessageAttachments = [];
let displayedFileIds = new Set(); // Track which files we've already displayed

function appendCodeBlock(container, codeContent) {
  const codeElement = createCodeElement();
  const preElement = codeElement.querySelector("pre");
  const languageInfoElement = codeElement.querySelector(".language-info");

  const lines = codeContent.split("\n");
  const language = lines[0].trim();
  const code = lines.slice(1).join("\n").trim();

  if (language) {
    languageInfoElement.textContent = language;
  }
  preElement.textContent = code;

  container.appendChild(codeElement);
}

function createCodeElement() {
  const template = document.getElementById("code_template");
  if (!template) {
    console.error("Code template not found");
    return document.createElement("div");
  }
  const codeElement = template.content
    .cloneNode(true)
    .querySelector(".flex.flex-col.w-full");

  const copyButton = codeElement.querySelector(".copy-btn");
  const copiedInfo = codeElement.querySelector(".copied");
  const preElement = codeElement.querySelector("pre");

  copyButton.onclick = () => {
    copiedInfo.classList.remove("hidden");
    navigator.clipboard
      .writeText(preElement.textContent)
      .then(() => {
        console.log("Text copied to clipboard");
      })
      .catch((err) => {
        console.error("Failed to copy text:", err);
      });
    setTimeout(() => copiedInfo.classList.add("hidden"), 500);
  };

  return codeElement;
}

function initChatMessages() {
  // Clear displayed files when initializing
  displayedFileIds.clear();

  if (messages.length === 0) {
    messages.push({ role: "system", content: systemMessage });
  }

  // Display file banners first if they exist in the system message
  if (messages[0].attachments && messages[0].attachments.length > 0) {
    const chatMessages = document.getElementById("chat_messages");
    for (const attachment of messages[0].attachments) {
      if (attachment.type === "file") {
        displayFileBanner(attachment.name, attachment.id, chatMessages);
      }
    }
  }

  if (use_prompt_template === "True") {
    // Store prompt content
    const promptContent = messages.length > 1 ? messages[1].content : "";

    // Add welcome message
    const chatMessages = document.getElementById("chat_messages");
    if (chatMessages) {
      addBotMessage(welcomeMessage);
    }

    // Set chat input content
    const chat_input_ui = document.getElementById("chat_input");
    if (chat_input_ui) {
      chat_input_ui.value = promptContent;
      chat_input_ui.focus();
    }

    // Remove the prompt message from messages array
    if (messages.length > 1) {
      messages.splice(1, 1);
    }
  } else {
    if (messages.length === 1) {
      // Only system message present - show welcome message
      const chatMessages = document.getElementById("chat_messages");
      if (chatMessages) {
        const template = document
          .getElementById("bot-message-template")
          .content.cloneNode(true);
        const contentElement = template.querySelector(".content");
        contentElement.textContent = welcomeMessage;

        // Add margin-bottom to the chat messages container instead of removing it from the message
        chatMessages.classList.add("mb-6");

        chatMessages.appendChild(template);

        // Focus input
        const chatInput = document.getElementById("chat_input");
        if (chatInput) chatInput.focus();
      }
    } else {
      // Display existing messages and their attachments
      for (const message of messages) {
        // Skip system messages marked as file context
        if (message.isFileContext) continue;

        // Display attachments if they exist
        if (message.attachments && message.attachments.length > 0) {
          const chatMessages = document.getElementById("chat_messages");
          for (const attachment of message.attachments) {
            if (attachment.type === "file") {
              displayFileBanner(attachment.name, attachment.id, chatMessages);
            }
          }
        }

        // Display the message content
        if (message["role"] === "assistant") {
          const botMessageElement = addBotMessage("");
          appendData(message["content"], botMessageElement);
        } else if (message["role"] === "user") {
          addUserMessage(message["content"]);
        }
      }
      document.getElementById("chat_messages").focus();
    }
  }
}

// Initialize chat when DOM is ready
if (document.readyState === "complete") {
  initChatMessages();
} else {
  document.addEventListener("DOMContentLoaded", () => {
    initChatMessages();
  });
}

function appendImage(container, imageData) {
  const img = document.createElement("img");
  img.src = imageData.image_url.url;
  img.className = "w-16 h-auto rounded-lg";
  container.appendChild(img);
}

function appendData(text, botMessageElement) {
  // Clear any existing content
  botMessageElement.innerHTML = "";

  if (typeof text === "object" && Array.isArray(text)) {
    text.forEach((item) => {
      if (item.type === "text") {
        appendNormalText(botMessageElement, item.text);
      } else if (item.type === "image_url") {
        appendImage(botMessageElement, item);
      }
    });
    return;
  }

  // First handle code blocks
  const codeRegex = /```([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeRegex.exec(text)) !== null) {
    // Append text before code block
    if (match.index > lastIndex) {
      appendNormalText(botMessageElement, text.slice(lastIndex, match.index));
    }

    // Handle code block
    const codeContent = match[1];
    appendCodeBlock(botMessageElement, codeContent);

    lastIndex = match.index + match[0].length;
  }

  // Append any remaining text after the last code block
  if (lastIndex < text.length) {
    appendNormalText(botMessageElement, text.slice(lastIndex));
  }
}

function saveChatData(messages) {
  console.log("Saving chat data:");
  console.log("- chat_started:", chat_started);
  console.log("- messages:", JSON.stringify(messages, null, 2));

  if (!chat_started) {
    console.error("Missing required data for saving chat:");
    console.error("- chat_started:", chat_started);
    return Promise.reject(new Error("Missing required data for saving chat"));
  }

  // Get CSRF token from meta tag
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  // Create FormData
  const formData = new FormData();
  formData.append("chat_started", chat_started);
  formData.append("messages", JSON.stringify(messages));

  // Send POST request to save chat
  return fetch("/chat/save_chat", {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
    },
    body: formData,
    credentials: "same-origin",
  })
    .then((response) => {
      if (!response.ok) {
        console.error(
          "Save chat response not OK:",
          response.status,
          response.statusText,
        );
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then((data) => {
      console.log("Chat saved successfully. Server response:", data);
      return data;
    })
    .catch((error) => {
      console.error("Error saving chat:", error);
      throw error;
    });
}

async function stopStreaming() {
  // Set the flag to true to stop streaming
  stop_stream = true;
}

function appendNormalText(container, text) {
  // Split text into lines to process each line separately
  const lines = text.split("\n");
  let inList = false;
  let listElement = null;
  let inTable = false;
  let tableElement = null;
  let tableHeader = false;

  // New structure for managing lists
  const listContext = {
    lists: [], // Stack of list elements
    indentLevels: [], // Corresponding indent levels
  };

  lines.forEach((line, index) => {
    // Check for horizontal rule
    if (line.match(/^[\-*_]{3,}$/)) {
      // End any open lists
      if (inList) {
        inList = false;
      }
      if (inTable) {
        container.appendChild(tableElement);
        inTable = false;
      }
      const hr = document.createElement("hr");
      hr.className = "my-4 border-t-2 border-gray-300";
      container.appendChild(hr);
      return;
    }

    // Check for table
    const tableMatch = line.match(/^\|(.+)\|$/);
    if (tableMatch) {
      const cells = tableMatch[1].split("|").map((cell) => cell.trim());

      if (!inTable) {
        tableElement = document.createElement("table");
        tableElement.className =
          "min-w-full my-4 border-collapse border border-gray-300";
        inTable = true;
        tableHeader = true;
      }

      const row = document
        .createElement(tableHeader ? "thead" : "tbody")
        .appendChild(document.createElement("tr"));
      row.className = tableHeader ? "bg-gray-100" : "";

      cells.forEach((cell) => {
        const td = document.createElement(tableHeader ? "th" : "td");
        td.className = "border border-gray-300 px-4 py-2 text-left";
        td.innerHTML = processInlineMarkdown(cell);
        row.appendChild(td);
      });

      if (tableHeader) {
        tableElement.appendChild(row.parentElement);
        tableHeader = false;
      } else {
        tableElement.appendChild(row.parentElement);
      }
      return;
    } else if (inTable) {
      container.appendChild(tableElement);
      inTable = false;
    }

    // Check for heading patterns
    const h1Match = line.match(/^# (.*)/);
    const h2Match = line.match(/^## (.*)/);
    const h3Match = line.match(/^### (.*)/);

    // Check for list patterns
    const indentedListMatch = line.match(/^(\s+)([\*\-]|\d+\.)\s+(.*)/);
    const ulMatch = line.match(/^[\*\-] (.*)/);
    const olMatch = line.match(/^(\d+)\. (.*)/);
    const taskMatch = line.match(/^[\*\-] \[([ x])\] (.*)/);
    const nestedQuoteMatch = line.match(/^>+ (.*)/);

    if (nestedQuoteMatch) {
      // End any open lists
      if (listContext.lists.length > 0) {
        cleanupLists(container, listContext);
      }

      const quoteDepth = line.match(/^>+/)[0].length;
      const blockquote = document.createElement("blockquote");
      // Reduced spacing for blockquotes
      blockquote.className = `border-l-4 pl-4 py-2 my-2 ml-${(quoteDepth - 1) * 4}`;

      // Adjust styling based on nesting level
      switch (quoteDepth) {
        case 1:
          blockquote.classList.add(
            "border-blue-300",
            "text-gray-700",
            "bg-gray-50",
          );
          break;
        case 2:
          blockquote.classList.add(
            "border-purple-300",
            "text-gray-700",
            "bg-gray-100",
          );
          break;
        case 3:
          blockquote.classList.add(
            "border-indigo-300",
            "text-gray-700",
            "bg-gray-200",
          );
          break;
        default:
          blockquote.classList.add(
            "border-gray-400",
            "text-gray-700",
            "bg-gray-300",
          );
      }

      blockquote.innerHTML = processInlineMarkdown(nestedQuoteMatch[1]);
      container.appendChild(blockquote);
    } else if (h1Match || h2Match || h3Match) {
      // End any open lists
      if (listContext.lists.length > 0) {
        cleanupLists(container, listContext);
      }

      // Handle headings (existing code)
      if (h1Match) {
        const h1 = document.createElement("h1");
        h1.className = "text-2xl font-bold mt-1 mb-3 text-gray-700";
        h1.innerHTML = processInlineMarkdown(h1Match[1]);
        container.appendChild(h1);
      } else if (h2Match) {
        const h2 = document.createElement("h2");
        h2.className = "text-xl font-bold mt-1 mb-1 text-gray-700";
        h2.innerHTML = processInlineMarkdown(h2Match[1]);
        container.appendChild(h2);
      } else if (h3Match) {
        const h3 = document.createElement("h3");
        h3.className = "text-lg font-bold mt-1 mb-1 text-gray-800";
        h3.innerHTML = processInlineMarkdown(h3Match[1]);
        container.appendChild(h3);
      }
    } else if (indentedListMatch || ulMatch || olMatch) {
      // Process any type of list item (indented or not)
      let indentation = 0;
      let listMarker = "";
      let content = "";
      let isIndented = false;

      if (indentedListMatch) {
        indentation = indentedListMatch[1].length;
        listMarker = indentedListMatch[2];
        content = indentedListMatch[3];
        isIndented = true;
      } else if (ulMatch) {
        listMarker = "*";
        content = ulMatch[1];
      } else if (olMatch) {
        listMarker = olMatch[1] + ".";
        content = olMatch[2];
      }

      const isOrdered = listMarker.includes(".");
      const listType = isOrdered ? "ol" : "ul";

      // Handle list nesting
      processListItem(container, listContext, {
        indentation,
        listType,
        content,
        listMarker,
        isIndented,
      });

      inList = true;
    } else if (taskMatch) {
      // Clean up any lists with different indentation
      while (
        listContext.lists.length > 0 &&
        listContext.lists[listContext.lists.length - 1].tagName !== "UL"
      ) {
        listContext.lists.pop();
        listContext.indentLevels.pop();
      }

      // Create UL if needed
      if (listContext.lists.length === 0) {
        const ul = document.createElement("ul");
        ul.className = "mb-2";
        container.appendChild(ul);
        listContext.lists.push(ul);
        listContext.indentLevels.push(0);
      }

      // Create the task list item
      const li = document.createElement("li");
      li.className = "text-gray-700 mb-1 flex items-center";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = taskMatch[1] === "x";
      checkbox.disabled = true;
      checkbox.className = "mr-2";
      li.appendChild(checkbox);
      const textSpan = document.createElement("span");
      textSpan.innerHTML = processInlineMarkdown(taskMatch[2]);
      li.appendChild(textSpan);

      // Add to the current list
      listContext.lists[listContext.lists.length - 1].appendChild(li);

      inList = true;
    } else {
      // Handle non-list content - clean up any open lists
      if (listContext.lists.length > 0) {
        cleanupLists(container, listContext);
      }

      if (line === "") {
        const spacer = document.createElement("div");
        spacer.className = "h-1"; // Reduced empty line height
        container.appendChild(spacer);
      } else {
        const p = document.createElement("p");
        p.className = "mb-1 text-gray-700"; // Reduced margin
        p.innerHTML = processInlineMarkdown(line);
        container.appendChild(p);
      }

      inList = false;
    }
  });

  // Clean up any remaining lists
  if (listContext.lists.length > 0) {
    cleanupLists(container, listContext);
  }

  // Clean up any remaining table
  if (inTable) {
    container.appendChild(tableElement);
  }

  // Remove the last margin-bottom from the last element if it has one
  const lastElement = container.lastElementChild;
  if (lastElement) {
    lastElement.classList.remove("mb-0.5", "mb-1", "mb-2");
  }
}

// Helper function to clean up any open lists
function cleanupLists(container, listContext) {
  if (listContext.lists.length > 0) {
    container.appendChild(listContext.lists[0]);
    listContext.lists = [];
    listContext.indentLevels = [];
  }
}

// Helper function to process a list item and handle nesting properly
function processListItem(container, listContext, item) {
  const { indentation, listType, content, listMarker, isIndented } = item;

  // Adjust the list stack based on indentation
  if (isIndented) {
    // Remove lists at greater indentation levels
    while (
      listContext.lists.length > 0 &&
      listContext.indentLevels[listContext.indentLevels.length - 1] >=
        indentation
    ) {
      listContext.lists.pop();
      listContext.indentLevels.pop();
    }
  } else {
    // For non-indented items, clear lists and create a new top-level list
    listContext.lists = [];
    listContext.indentLevels = [];
  }

  // Create list item
  const li = document.createElement("li");
  li.className = "text-gray-700 mb-0.5";

  // Add bullet or number
  if (listType === "ul") {
    const bulletPoint = document.createElement("span");
    bulletPoint.className = "inline-block w-4";
    bulletPoint.textContent = "•";
    li.appendChild(bulletPoint);
  } else {
    const numberPoint = document.createElement("span");
    numberPoint.className = "inline-block w-4";
    const num = listMarker.replace(".", "");
    numberPoint.textContent = num + ".";
    if (parseInt(num)) {
      li.value = parseInt(num);
    }
    li.appendChild(numberPoint);
  }

  // Add content
  const textSpan = document.createElement("span");
  textSpan.innerHTML = processInlineMarkdown(content);
  li.appendChild(textSpan);

  // Find or create the appropriate list
  let parentList;

  if (listContext.lists.length === 0) {
    // Create a new top-level list
    parentList = document.createElement(listType);
    parentList.className = "mb-2";

    if (isIndented) {
      // This is an indented item without a parent - rare case
      container.appendChild(parentList);
    } else {
      // Normal top-level list
      container.appendChild(parentList);
    }

    listContext.lists.push(parentList);
    listContext.indentLevels.push(indentation);
  } else {
    // Get the current deepest list
    const currentList = listContext.lists[listContext.lists.length - 1];

    if (isIndented) {
      // This is a nested list item - create a new list inside the last list item
      const parentLi = currentList.lastElementChild;

      // Check if parent already has a list of this type
      let nestedList = null;
      if (parentLi) {
        for (let i = 0; i < parentLi.children.length; i++) {
          const child = parentLi.children[i];
          if (child.tagName && child.tagName.toLowerCase() === listType) {
            nestedList = child;
            break;
          }
        }
      }

      if (!nestedList && parentLi) {
        // Create a new nested list
        nestedList = document.createElement(listType);
        nestedList.className = "ml-6 mt-1 pl-2 border-l border-gray-200";
        parentLi.appendChild(nestedList);
      }

      parentList = nestedList || currentList;

      if (nestedList) {
        // Add the new list to our context
        listContext.lists.push(nestedList);
        listContext.indentLevels.push(indentation);
      }
    } else {
      // This is a new item at the same level as the current list
      parentList = currentList;
    }
  }

  // Add the list item to the appropriate list
  if (parentList) {
    parentList.appendChild(li);
  }
}

function processInlineMarkdown(text) {
  // Process blockquotes (now handled in appendNormalText for nesting support)
  if (text.startsWith("> ")) {
    return `<blockquote class="border-l-4 border-gray-300 pl-4 py-2 my-2 italic text-gray-600">${text.substring(2)}</blockquote>`;
  }

  // Process inline code first (to avoid conflicts with other syntax)
  text = text.replace(
    /`([^`]+)`/g,
    '<code class="bg-base-300 px-1 py-0.5 rounded text-sm font-mono">$1</code>',
  );

  // Process bold and italic
  text = text.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong class="font-bold">$1</strong>',
  );
  text = text.replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>');
  text = text.replace(/_([^_]+)_/g, '<em class="italic">$1</em>');

  // Process links
  text = text.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" class="text-primary hover:underline" target="_blank" rel="noopener noreferrer">$1</a>',
  );

  // Process strikethrough
  text = text.replace(/~~([^~]+)~~/, '<del class="line-through">$1</del>');

  return text;
}

function appendCodeText(container, text) {
  // Get the template and clone its content
  const template = document
    .getElementById("code_template")
    .content.cloneNode(true);

  const lines = text.split("\n");
  const language = lines[0].trim(); // Get the language info from the first line
  console.log(`Code block language: ${language}`); // Log the language info

  // Remove the first line (language info) and join the rest back into a single string
  const codeWithoutLanguageInfo = lines.slice(1).join("\n").trim();

  // Set the text content of the pre element
  const preElement = template.querySelector("pre");
  preElement.textContent = codeWithoutLanguageInfo;

  // Append the filled template to the specified container
  const importedNode = document.importNode(template, true);

  if (language) {
    // Check if the language string is not empty
    const languageInfoElement = importedNode.querySelector(".language-info");
    languageInfoElement.textContent = `${language}`; // Set the language info
  }

  // IMPORTANT: Add the event listener to the COPY button of this specific instance BEFORE appending to the container
  const copyButton = importedNode.querySelector(".copy-btn");
  const copiedInfo = importedNode.querySelector(".copied");
  copyButton.onclick = (event) => {
    // It's better to use onclick here to avoid multiple bindings
    copiedInfo.classList.remove("hidden");
    navigator.clipboard
      .writeText(preElement.textContent)
      .then(() => {
        console.log("Text copied to clipboard");
      })
      .catch((err) => {
        console.error("Failed to copy text:", err);
      });
    setTimeout(function () {
      copiedInfo.classList.add("hidden");
    }, 500);
  };

  container.appendChild(importedNode);
}

async function streamMessage() {
  const chatInput = document.getElementById("chat_input");
  const userMessage = chatInput.value.trim();
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  if (userMessage !== "") {
    // Remove prompts div if it exists
    const promptsDiv = document.getElementById("prompts");
    if (promptsDiv) promptsDiv.remove();

    // Create message object with attachments
    const messageObj = {
      role: "user",
      content: userMessage,
    };

    console.log("Current messages array before adding user message:", messages);

    messages.push(messageObj);
    addUserMessage(userMessage); // Display the user message in the chat
    chatInput.value = ""; // Clear the input field after sending the message

    // Save chat immediately after adding user message
    try {
      await saveChatData(messages);
      console.log("Chat saved after user message");
    } catch (error) {
      console.error("Failed to save chat after user message:", error);
    }

    toggleButtonVisibility();
    stop_stream = false;
    chatInput.readOnly = true;

    // Instantly add a bot message template to be filled with streamed content
    const botMessageElement = addBotMessage("..."); // Initially empty
    let accumulatedResponse = ""; // Variable to accumulate the streamed response

    try {
      let current_model = models[0];
      for (let i = 0; i < models.length; i++) {
        if (selected_model == models[i]["model"]) {
          current_model = models[i];
        }
      }
      const response = await fetch("/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ messages: messages, model: current_model }),
      });

      if (!response.body) {
        throw new Error("Failed to get a readable stream from the response");
      }

      const reader = response.body.getReader();

      while (true) {
        const { done, value } = await reader.read();
        if (done || stop_stream) {
          const stopIndexAccumulated =
            accumulatedResponse.indexOf("###STOP###");
          if (stopIndexAccumulated !== -1) {
            accumulatedResponse = accumulatedResponse.substring(
              0,
              stopIndexAccumulated,
            );
          }
          botMessageElement.innerHTML = "";
          appendData(accumulatedResponse, botMessageElement);
          messages.push({ role: "assistant", content: accumulatedResponse });

          console.log(
            "Current messages array before saving after AI response:",
            messages,
          );

          // Save chat after AI response
          try {
            await saveChatData(messages);
            console.log("Chat saved after AI response");
          } catch (error) {
            console.error("Failed to save chat after AI response:", error);
          }

          toggleButtonVisibility();
          chatInput.readOnly = false;
          break;
        }

        const text = new TextDecoder().decode(value);
        const stopIndex = text.indexOf("###STOP###");

        if (stopIndex !== -1) {
          accumulatedResponse += text.substring(0, stopIndex);
          botMessageElement.innerHTML = "";
          appendData(accumulatedResponse, botMessageElement);
          messages.push({ role: "assistant", content: accumulatedResponse });

          console.log(
            "Current messages array before saving after AI response:",
            messages,
          );

          // Save chat after AI response
          try {
            await saveChatData(messages);
            console.log("Chat saved after AI response");
          } catch (error) {
            console.error("Failed to save chat after AI response:", error);
          }

          toggleButtonVisibility();
          chatInput.readOnly = false;
          break;
        } else {
          accumulatedResponse += text;
          botMessageElement.innerHTML = "";
          appendData(accumulatedResponse, botMessageElement);
          scrollToBottom();
        }
      }
    } catch (error) {
      console.error("Streaming failed:", error);
      botMessageElement.textContent = `Error occurred: ${error.message}`;
      messages.push({
        role: "assistant",
        content: `Error occurred: ${error.message}`,
      });

      console.log(
        "Current messages array before saving after error:",
        messages,
      );

      // Save chat after error
      try {
        await saveChatData(messages);
        console.log("Chat saved after error");
      } catch (saveError) {
        console.error("Failed to save chat after error:", saveError);
      }

      toggleButtonVisibility();
      chatInput.readOnly = false;
    }
  }
}

function toggleButtonVisibility() {
  const chatButton = document.getElementById("chat_button");
  const stopButton = document.getElementById("stop_button");

  chatButton.classList.toggle("hidden");
  stopButton.classList.toggle("hidden");
}

function addBotMessage(text) {
  const template = document
    .getElementById("bot-message-template")
    .content.cloneNode(true);
  const contentElement = template.querySelector(".content");
  const copyButton = template.querySelector(".copy-btn");
  const copyIcon = copyButton.querySelector(".copy-icon");
  const checkIcon = copyButton.querySelector(".check-icon");
  const copyText = copyButton.querySelector(".copy-text");
  const checkText = copyButton.querySelector(".check-text");

  if (text == "...") {
    contentElement.innerHTML =
      '<span class="loading loading-dots loading-xs"></span>';
  } else if (typeof text === "object" && Array.isArray(text)) {
    text.forEach((item) => {
      if (item.type === "text") {
        appendNormalText(contentElement, item.text);
      } else if (item.type === "image_url") {
        appendImage(contentElement, item);
      }
    });
  } else {
    contentElement.textContent = text;
  }

  // Add copy functionality
  copyButton.addEventListener("click", async () => {
    // Create a temporary div to handle HTML content
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = contentElement.innerHTML;

    // Remove any loading indicators if present
    const loadingElements = tempDiv.getElementsByClassName("loading");
    while (loadingElements.length > 0) {
      loadingElements[0].remove();
    }

    // Function to inline Tailwind styles
    function inlineStyles(element) {
      const styles = window.getComputedStyle(element);
      const inlineStyle = {};
      for (let prop of styles) {
        inlineStyle[prop] = styles.getPropertyValue(prop);
      }
      element.style.cssText = Object.entries(inlineStyle)
        .map(([prop, value]) => `${prop}: ${value}`)
        .join("; ");

      // Process children
      Array.from(element.children).forEach((child) => inlineStyles(child));
    }

    // Clone the content and inline styles
    const clonedContent = contentElement.cloneNode(true);
    document.body.appendChild(clonedContent);
    inlineStyles(clonedContent);
    const styledHTML = clonedContent.outerHTML;
    document.body.removeChild(clonedContent);

    try {
      // Create a Blob with HTML content
      const blob = new Blob([styledHTML], { type: "text/html" });
      const plainText = contentElement.textContent;

      // Create clipboard data with both formats
      await navigator.clipboard.write([
        new ClipboardItem({
          "text/html": blob,
          "text/plain": new Blob([plainText], { type: "text/plain" }),
        }),
      ]);

      // Visual feedback
      copyIcon.classList.add("hidden");
      checkIcon.classList.remove("hidden");
      copyText.classList.add("hidden");
      checkText.classList.remove("hidden");
      copyButton.classList.add("text-green-600", "bg-green-50");

      // Reset after 2 seconds
      setTimeout(() => {
        copyIcon.classList.remove("hidden");
        checkIcon.classList.add("hidden");
        copyText.classList.remove("hidden");
        checkText.classList.add("hidden");
        copyButton.classList.remove("text-green-600", "bg-green-50");
      }, 2000);
    } catch (err) {
      console.error("Failed to copy formatted content:", err);
      // Fallback to plain text
      navigator.clipboard.writeText(contentElement.textContent);
    }
  });

  document.getElementById("chat_messages").appendChild(template);
  return contentElement;
}

function addUserMessage(text) {
  const template = document
    .getElementById("user-message-template")
    .content.cloneNode(true);
  const contentElement = template.querySelector(".content");

  if (typeof text === "object" && Array.isArray(text)) {
    text.forEach((item) => {
      if (item.type === "text") {
        appendNormalText(contentElement, item.text);
      } else if (item.type === "image_url") {
        appendImage(contentElement, item);
      }
    });
  } else {
    contentElement.textContent = text;
  }

  document.getElementById("chat_messages").appendChild(template);
  scrollToBottom();
}

function scrollToBottom() {
  setTimeout(() => {
    const chatMessages = document.getElementById("chat_messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }, 0); // Verzögerung von 0 ms, was den Effekt hat, die Ausführung bis nach dem Rendering zu verzögern
}

document.getElementById("chat_button").addEventListener("click", streamMessage);

document
  .getElementById("chat_input")
  .addEventListener("keydown", function (event) {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      streamMessage();
    }
  });

document.getElementById("reset_button").addEventListener("click", function () {
  displayedFileIds.clear();
  window.location.href = "/chat";
});

document.getElementById("stop_button").addEventListener("click", stopStreaming);

function createFileBanner(fileName, fileId) {
  // If we've already displayed this file, don't create another banner
  if (displayedFileIds.has(fileId)) {
    return null;
  }

  const template = document.getElementById("file-banner-template");
  if (!template) {
    console.error("File banner template not found");
    return document.createElement("div");
  }

  // Clone the template content
  const fragment = template.content.cloneNode(true);

  // Get the root element from the fragment
  const banner = fragment.querySelector(".mb-6");

  // Set the filename
  banner.querySelector(".filename").textContent = fileName;

  // Set the download link
  const downloadLink = banner.querySelector(".download-link");
  downloadLink.href = `/download_file/${fileId}`;

  // Mark this file as displayed
  displayedFileIds.add(fileId);

  return banner;
}

function displayFileBanner(fileName, fileId, chatMessages) {
  const banner = createFileBanner(fileName, fileId);
  if (banner) {
    chatMessages.appendChild(banner);
    return banner;
  }
  return null;
}

document
  .getElementById("file-upload")
  .addEventListener("change", async function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const fileName = file.name;
    document.getElementById("file-name-display").textContent = "Uploading...";

    // Get CSRF token
    const csrfToken = document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");

    // Create FormData and append file
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/chat/upload", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      });

      const result = await response.json();

      if (result.status === "ok") {
        console.log("File uploaded successfully:", result);

        // Initialize messages array if empty
        if (messages.length === 0) {
          messages.push({
            role: "system",
            content: systemMessage,
            attachments: [],
          });
        }

        // Add file to system message attachments
        if (!messages[0].attachments) {
          messages[0].attachments = [];
        }
        messages[0].attachments.push({
          type: "file",
          id: result.file_id,
          name: result.filename,
          file_type: result.file_type,
          timestamp: Math.floor(Date.now() / 1000),
        });

        // For non-image files, append the context to the existing system message
        if (!["jpg", "jpeg", "png"].includes(result.file_type.toLowerCase())) {
          messages[0].content += `\n\nUsing context from file: ${result.filename}\n\n${result.content}`;
        }

        // Save chat state immediately after adding file
        try {
          await saveChatData(messages);
          console.log("Chat state saved after file upload");
        } catch (error) {
          console.error("Failed to save chat state after file upload:", error);
        }

        // Display file banner
        const chatMessages = document.getElementById("chat_messages");
        const banner = displayFileBanner(
          fileName,
          result.file_id,
          chatMessages,
        );
        if (banner) {
          setTimeout(() => {
            banner.scrollIntoView({ behavior: "smooth", block: "center" });
          }, 100);
        }

        // Update display text
        document.getElementById("file-name-display").textContent = "Upload";
        console.log("Current messages array:", messages);
      } else {
        console.error("Upload failed:", result.message);
        document.getElementById("file-name-display").textContent =
          "Upload failed: " + result.message;
      }
    } catch (error) {
      console.error("Upload error:", error);
      document.getElementById("file-name-display").textContent =
        "Upload error: " + error.message;
    }
  });
```

