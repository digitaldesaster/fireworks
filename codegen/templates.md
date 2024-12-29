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

