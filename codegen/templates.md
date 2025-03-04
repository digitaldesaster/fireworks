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
    <!-- Early Theme Initialization -->
    <script>
      (function() {
        // Apply theme before page renders to avoid flash of wrong theme
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
          document.documentElement.dataset.theme = 'dark';
        } else {
          document.documentElement.dataset.theme = 'light';
        }
      })();
    </script>
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
    <!-- Early Theme Initialization -->
    <script>
      (function() {
        // Apply theme before page renders to avoid flash of wrong theme
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
          document.documentElement.dataset.theme = 'dark';
        } else {
          document.documentElement.dataset.theme = 'light';
        }
      })();
    </script>
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
  <body class="min-h-full flex flex-col bg-base-100">
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
  <body class="bg-base-100 min-h-screen">
    {% include('/main/nav.html') %}

    <section class="p-6 flex items-center lg:ml-64">
      <div class="max-w-screen-xl mx-auto px-4 lg:px-12 w-full">
        <!-- Start coding here -->
        <div class="relative bg-base-100 shadow-md sm:rounded-lg">
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
    <span class="mt-1 text-sm text-base-content/60">
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
    class="searchField bg-base-200 border border-base-content/10 text-base-content text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5"
  />

  <!-- Dropdown Menu -->
  <div
    id="dropdownMenu"
    class="z-10 hidden bg-base-100 rounded-lg shadow w-full mt-1 max-h-48 overflow-y-auto"
  >
    <ul id="userList" class="py-2 text-base-content"></ul>
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

    <div class="text-sm text-base-content/60">
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
  <body class="bg-base-100 min-h-screen">
    {% include('/main/nav.html') %}

    <section class="p-4 sm:p-6 flex items-center lg:ml-64">
      <div class="max-w-screen-xl mx-auto px-2 sm:px-4 lg:px-12 w-full">
        <div
          class="relative bg-base-100 shadow-md sm:rounded-lg p-3 sm:p-4 border border-base-content/10"
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
                        class="w-4 h-4 text-base-content/50"
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
                      class="w-full max-w-md pl-10 pr-4 py-2 border border-base-content/20 bg-base-100 text-base-content rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
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
    class="overflow-x-auto rounded-lg border border-base-content/10"
  >
    <table class="table border-collapse w-full">
      <thead>
        <tr>
          {% for header in table_header %}
          <th
            class="font-bold {{header.class}} px-4 py-3 border-b border-r border-base-content/10 last:border-r-0"
          >
            {{header.label}}
          </th>
          {% endfor %}
          <th
            class="w-16 px-4 py-3 text-right border-b border-r border-base-content/10 last:border-r-0 sticky right-0 bg-base-100 z-10"
          >
            Actions
          </th>
        </tr>
      </thead>
      <tbody>
        {% for document in table_content %}
        <tr
          id="tr-{{document[0].id}}"
          class="{% if not loop.last %}border-b border-base-content/10{% endif %}"
        >
          {% for field in document %}
          <td
            class="font-normal leading-normal px-4 py-2 border-r border-base-content/10 last:border-r-0 {% if field.name == 'first_message' %}max-w-md truncate line-clamp-2{% endif %}"
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
          <td class="w-16 px-4 py-2 text-right sticky right-0 bg-base-100">
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
  class="hidden overflow-y-auto overflow-x-hidden bg-base-300/65 backdrop-blur-sm fixed top-0 right-0 left-0 z-50 flex justify-center items-center w-full h-full"
>
  <div
    class="modal-content relative p-4 w-full max-w-md max-h-full"
  >
    <div class="relative bg-base-100 rounded-lg shadow">
      <button
        type="button"
        class="close-modal absolute top-3 right-2.5 text-base-content/60 bg-transparent hover:bg-base-200 hover:text-base-content rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center"
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
          class="mx-auto mb-4 text-base-content/60 w-12 h-12"
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
        <h3 class="mb-2 text-lg font-medium text-base-content">Confirm Action</h3>
        <p class="mb-5 text-base-content/60">Are you sure?</p>
        <button
          type="button"
          class="confirm-action text-primary-content bg-error hover:bg-error-focus focus:ring-4 focus:outline-none focus:ring-error/30 font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center"
        >
          Yes, I'm sure
        </button>
        <button
          type="button"
          class="cancel-action py-2.5 px-5 ms-3 text-sm font-medium text-base-content focus:outline-none bg-base-100 rounded-lg border border-base-300 hover:bg-base-200 focus:z-10 focus:ring-4 focus:ring-base-200"
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
      class="flex justify-center items-center w-10 h-10 bg-primary text-primary-content rounded-full"
    >
      {{ config.firstname[0] if config.firstname else '' }}{{ config.name[0] if
      config.name else '' }}
    </div>
    <div
      class="message content bg-base-200 rounded-lg p-4 flex-1 min-w-0 break-words"
      id="message-{{ loop.index }}"
    ></div>
  </div>
  {% endif %} {% if message.role =='assistant' %}
  <div class="flex space-x-4 mb-4">
    <div
      class="flex justify-center items-center w-10 h-10 bg-secondary text-secondary-content rounded-full"
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
      class="message content bg-base-200 text-base-content rounded-lg p-4 flex-1 min-w-0 break-words"
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
    class="flex justify-center items-center w-10 h-10 bg-primary text-primary-content rounded-full flex-shrink-0"
  >
    {{ config.firstname[0] if config.firstname else '' }}{{ config.name[0] if
    config.name else '' }}
  </div>
  <div
    class="message content bg-base-200 rounded-lg p-4 flex-1 min-w-0 break-words"
  ></div>
</div>
```

## chat/code_block_template.html

```
<div class="flex flex-col w-full">
    <div class="h-8 bg-neutral w-full flex rounded-t justify-between items-center px-4">
      <!-- Language Info Placeholder -->
      <span class="text-sm text-neutral-content language-info"></span>

      <div class="flex flex-row items-center gap-2">
        <span class="copied hidden text-sm font-extralight text-success">copied!</span>
        <!-- Copy Button -->
      <button class="h-4 w-4 copy-btn flex items-center justify-center text-neutral-content hover:text-success">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
        </svg>
      </button>
      </div>
      
    </div>
    <div class="w-full">
      <pre class="bg-neutral-focus text-sm text-neutral-content rounded-b p-2 overflow-x-auto whitespace-pre-wrap">
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
    class="text-center text-xl font-semibold text-base-content"
  >
    Last Chats
  </h3>
  <div class="flex flex-row flex-wrap justify-center gap-4">
    {% for item in config.history %}
    <a href="/chat/history/{{ item.id }}" class="no-underline">
      <div
        id="history_{{ loop.index }}"
        class="relative h-12 w-64 flex items-center justify-center bg-primary hover:bg-primary-focus text-primary-content rounded-xl cursor-pointer px-4"
      >
        <span class="truncate">{{ item.first_message }}</span>
      </div>
    </a>
    {% endfor %}
  </div>
  <hr class="h-px my-2 bg-base-content/10 border-0" />
  {% endif %} {% if config.latest_prompts %}
  <h3
    class="text-center text-xl font-semibold text-base-content"
  >
    Latest Prompts
  </h3>
  <div class="flex flex-row flex-wrap justify-center gap-4">
    {% for prompt in config.latest_prompts %}
    <a href="/chat/prompt/{{ prompt.id }}" class="no-underline">
      <div
        id="prompt_{{ loop.index }}"
        class="relative h-12 w-64 flex items-center justify-center bg-primary hover:bg-primary-focus text-primary-content rounded-xl cursor-pointer px-4"
      >
        <span class="truncate">{{ prompt.name }}</span>
      </div>
    </a>
    {% endfor %}
  </div>
  {% endif %} {% if not config.history and not config.latest_prompts %}
  <div class="flex flex-row flex-wrap justify-center gap-4">
    <div
      class="prompt relative h-12 w-64 flex items-center justify-center bg-primary hover:bg-primary-focus text-primary-content rounded-xl cursor-pointer px-4"
    >
      <span class="truncate">Wer war Ada Lovelace?</span>
    </div>
    <div
      class="group relative prompt h-12 w-64 flex items-center justify-center bg-primary hover:bg-primary-focus text-primary-content rounded-xl cursor-pointer px-4"
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
    class="flex justify-center items-center w-10 h-10 bg-secondary text-secondary-content rounded-full flex-shrink-0"
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
      class="message content bg-base-200 text-base-content rounded-lg p-4 break-words"
    ></div>
    <div class="flex justify-start mt-2">
      <button
        class="copy-btn flex items-center gap-1 text-sm text-base-content/60 hover:text-base-content active:scale-95 transition-all duration-100 rounded px-2 py-1 hover:bg-base-200"
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
  <div class="h-full w-full 2xl:max-w-7xl 2xl:mx-auto relative">
    <div
      class="flex flex-col absolute bottom-0 left-0 right-0 h-32 mx-2 mb-2 md:mx-10 md:mb-4 xl:mx-16 xl:mb-4 2xl:mx-20 2xl:mb-4 rounded-xl bg-base-100 shadow-[0_-2px_15px_-3px_rgba(0,0,0,0.1)] border border-base-content/10"
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
              class="model dropdown-item w-full text-left px-4 py-2 hover:bg-base-200"
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
      <div class="px-2 md:px-10 xl:px-16 2xl:px-20 w-full 2xl:max-w-7xl 2xl:mx-auto">
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
              <div class="bg-info/10 border-l-4 border-info p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg
                      class="h-5 w-5 text-info"
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
                    <p class="text-sm text-info-content">
                      Using context from file: <span class="filename"></span>
                    </p>
                    <a
                      href="#"
                      class="download-link text-info hover:text-info-focus"
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
  <!-- Early Theme Initialization -->
  <script>
    (function() {
      // Apply theme before page renders to avoid flash of wrong theme
      const savedTheme = localStorage.getItem('theme');
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      
      if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.dataset.theme = 'dark';
      } else {
        document.documentElement.dataset.theme = 'light';
      }
    })();
  </script>
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
  
  <!-- Screen Size Indicator (Temporary) -->
  <div id="screen-size-indicator" class="px-3 py-1 bg-slate-100 rounded-lg text-slate-600 text-xs font-mono hidden md:flex items-center gap-2">
    <span class="icon-[tabler--device-desktop-analytics] size-4"></span>
    <span class="screen-width">0</span> × <span class="screen-height">0</span>
    <span class="text-[10px] px-1.5 py-0.5 rounded breakpoint-tag" data-min-width="640" data-name="sm">sm</span>
    <span class="text-[10px] px-1.5 py-0.5 rounded breakpoint-tag" data-min-width="768" data-name="md">md</span>
    <span class="text-[10px] px-1.5 py-0.5 rounded breakpoint-tag" data-min-width="1024" data-name="lg">lg</span>
    <span class="text-[10px] px-1.5 py-0.5 rounded breakpoint-tag" data-min-width="1280" data-name="xl">xl</span>
    <span class="text-[10px] px-1.5 py-0.5 rounded breakpoint-tag" data-min-width="1536" data-name="2xl">2xl</span>
  </div>
  
  <div class="navbar-end flex items-center gap-2">
    <!-- Dark Mode Toggle -->
    <div class="flex items-center mr-2">
      <div class="flex items-center gap-1">
        <span class="icon-[tabler--sun] size-5 text-yellow-500"></span>
        <input type="checkbox" class="switch theme-controller switch-sm" id="darkModeToggle" value="dark" />
        <span class="icon-[tabler--moon] size-5 text-slate-700 dark:text-slate-300"></span>
      </div>
    </div>
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
  <div class="drawer-body w-64 bg-base-100 h-full flex flex-col overflow-hidden">
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
    const { modalId, result, documentType, action } = event.detail;
    
    // If this is from delete all history action
    if (result && (result.action === 'delete_all_history' || action === 'delete_all_history')) {
      console.log('History deletion was successful');
      
      // Check if we're on a history page or list history page
      const currentPath = window.location.pathname;
      if (
        currentPath.includes("/chat/history/") ||
        currentPath.includes("/list/history") ||
        currentPath.includes("/d/history")
      ) {
        console.log('On history page, redirecting to index');
        // Redirect to index page
        window.location.href = "/";
        return;
      }

      console.log('Not on history page, updating navigation items');
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
  
  // Special handler for the delete history button in the collapsed menu
  document.addEventListener('DOMContentLoaded', function() {
    const deleteHistoryBtn = document.querySelector('button[data-action*="delete_all_history"]');
    if (deleteHistoryBtn) {
      console.log('Found delete history button, adding special handler');
      deleteHistoryBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Delete history button clicked via special handler');
        
        const modalId = this.dataset.modalTarget;
        const modalInstance = window.modalInstances ? window.modalInstances[modalId] : null;
        
        if (modalInstance) {
          console.log('Using modal instance for delete history', this.dataset);
          // Make sure we correctly update the modal from this button's data attributes
          modalInstance.updateModalFromTrigger(this);
          modalInstance.showModal();
        } else {
          // Fallback: try to get modal directly
          console.log('No modal instance found, trying direct access');
          const modal = document.getElementById(modalId);
          if (modal) {
            // Update modal content directly
            const title = modal.querySelector('h3');
            const message = modal.querySelector('p');
            const confirmBtn = modal.querySelector('button.confirm-action');
            
            // Set data attributes on the modal itself for the confirm action
            modal.dataset.action = this.dataset.action;
            modal.dataset.method = 'post'; // Force POST method for delete_all_history
            
            if (title) title.textContent = this.dataset.title || 'Confirm Action';
            if (message) message.textContent = this.dataset.message || 'Are you sure?';
            
            // Attach direct click handler to confirm button as fallback
            if (confirmBtn) {
              confirmBtn.onclick = function() {
                const url = modal.dataset.action;
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
                
                fetch(url, {
                  method: 'POST',
                  headers: {
                    'X-CSRFToken': csrfToken
                  }
                })
                .then(response => response.json())
                .then(result => {
                  console.log('History deletion result:', result);
                  if (result.status === 'ok') {
                    // Show success notification
                    const notification = document.createElement('div');
                    notification.className = 'fixed bottom-4 right-4 px-6 py-3 rounded shadow-lg z-50 bg-green-500 text-white';
                    notification.textContent = 'History deleted successfully';
                    document.body.appendChild(notification);
                    setTimeout(() => notification.remove(), 3000);
                    
                    // Check if we're on a history-related page
                    const currentPath = window.location.pathname;
                    if (
                      currentPath.includes("/chat/history/") ||
                      currentPath.includes("/list/history") ||
                      currentPath.includes("/d/history")
                    ) {
                      console.log('On history page, redirecting to index');
                      window.location.href = "/";
                      return;
                    }
                    
                    // Update the navigation
                    console.log('Not on history page, updating navigation');
                    updateNavItems();
                  }
                  modal.classList.add('hidden');
                })
                .catch(error => {
                  console.error('Error deleting history:', error);
                  modal.classList.add('hidden');
                });
              };
            }
            
            // Show modal
            modal.classList.remove('hidden');
          }
        }
      });
    } else {
      console.warn('Delete history button not found on DOMContentLoaded');
      
      // Try again after a slight delay to account for dynamic content
      setTimeout(function() {
        const delayedButton = document.querySelector('button[data-action*="delete_all_history"]');
        if (delayedButton) {
          console.log('Found delete history button after delay');
          delayedButton.click(); // Trigger the click to ensure it works
        } else {
          console.error('Delete history button not found even after delay');
        }
      }, 500);
    }
  });
</script>

<!-- Screen Size Indicator Script -->
<script>
  // Function to update screen size information
  function updateScreenSizeIndicator() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // Update the displayed dimensions
    document.querySelectorAll('.screen-width').forEach(el => {
      el.textContent = width;
    });
    
    document.querySelectorAll('.screen-height').forEach(el => {
      el.textContent = height;
    });
    
    // Show the indicator on all screens 
    const indicator = document.getElementById('screen-size-indicator');
    if (indicator) {
      indicator.classList.remove('hidden', 'md:flex');
      indicator.classList.add('flex');
    }

    // Define breakpoints in order from smallest to largest
    const breakpoints = [
      { name: 'sm', minWidth: 640 },
      { name: 'md', minWidth: 768 },
      { name: 'lg', minWidth: 1024 },
      { name: 'xl', minWidth: 1280 },
      { name: '2xl', minWidth: 1536 }
    ];
    
    // Find the highest active breakpoint
    let activeBreakpoint = null;
    for (let i = breakpoints.length - 1; i >= 0; i--) {
      if (width >= breakpoints[i].minWidth) {
        activeBreakpoint = breakpoints[i].name;
        break;
      }
    }
    
    // Update all breakpoint tags
    document.querySelectorAll('.breakpoint-tag').forEach(tag => {
      const name = tag.dataset.name;
      
      // Reset all styles
      tag.classList.remove('bg-green-500', 'text-white', 'font-bold', 'bg-gray-100', 'opacity-50');
      
      if (name === activeBreakpoint) {
        // Highlight the active breakpoint
        tag.classList.add('bg-green-500', 'text-white', 'font-bold');
      } else {
        // Make other breakpoints subtle
        tag.classList.add('bg-gray-100', 'opacity-50');
      }
    });
  }
  
  // Run on page load
  document.addEventListener('DOMContentLoaded', updateScreenSizeIndicator);
  
  // Run whenever the window is resized
  window.addEventListener('resize', updateScreenSizeIndicator);
</script>

<!-- Theme Persistence Script -->
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    // Check saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial state
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
      document.documentElement.dataset.theme = 'dark';
      if (darkModeToggle) darkModeToggle.checked = true;
    }
    
    // Add change event listener to toggle
    if (darkModeToggle) {
      darkModeToggle.addEventListener('change', function() {
        const newTheme = this.checked ? 'dark' : 'light';
        document.documentElement.dataset.theme = newTheme;
        localStorage.setItem('theme', newTheme);
      });
    }
  });
</script>

{% include 'components/confirm_modal.html' %}
```

