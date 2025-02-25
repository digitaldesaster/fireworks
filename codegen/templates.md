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

        {% include 'base/document/js/delete_document.js' %}
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

    <!-- Delete Modal -->
    <div
      id="deleteModal"
      tabindex="-1"
      class="hidden overflow-y-auto overflow-x-hidden bg-gray-600 bg-opacity-65 backdrop-blur-sm fixed top-0 right-0 left-0 z-50 flex justify-center items-center w-full h-full"
    >
      <div id="modalContent" class="relative p-4 w-full max-w-md max-h-full">
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

    <script src="{{ url_for('static', filename='js/lib/flyonui.js') }}"></script>
    <script>
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", function () {
          const id = this.dataset.id;
          const type = this.dataset.type;
          const modal = document.getElementById("deleteModal");
          const modalContent = document.getElementById("modalContent");
          const confirmDelete = document.getElementById("confirmDelete");
          const cancelDelete = document.getElementById("cancelDelete");
          const closeButton = document.getElementById("closeModal");

          // Show modal
          modal.classList.remove("hidden");

          // Handle delete confirmation
          const handleDelete = () => {
            const url = "{{ url_for('delete_document') }}";

            fetch(url + "?id=" + id + "&type=" + type, {
              method: "GET",
              headers: {
                "X-CSRFToken": "{{ csrf_token() }}",
              },
            })
              .then((response) => response.json())
              .then((result) => {
                if (result.status === "ok") {
                  // Remove the row from the table
                  const row = button.closest("tr");
                  row.remove();

                  // Show success notification
                  const notification = document.createElement("div");
                  notification.className =
                    "fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg z-50";
                  notification.textContent = "Document deleted successfully";
                  document.body.appendChild(notification);
                  setTimeout(() => notification.remove(), 3000);
                } else {
                  // Show error notification
                  const notification = document.createElement("div");
                  notification.className =
                    "fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded shadow-lg z-50";
                  notification.textContent =
                    "Error deleting document: " + result.message;
                  document.body.appendChild(notification);
                  setTimeout(() => notification.remove(), 3000);
                }
              })
              .catch((error) => {
                console.error("Error:", error);
                // Show error notification
                const notification = document.createElement("div");
                notification.className =
                  "fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded shadow-lg z-50";
                notification.textContent = "Error deleting document";
                document.body.appendChild(notification);
                setTimeout(() => notification.remove(), 3000);
              })
              .finally(() => {
                modal.classList.add("hidden");
                cleanup();
              });
          };

          // Handle modal close
          const handleClose = () => {
            modal.classList.add("hidden");
            cleanup();
          };

          // Cleanup event listeners
          const cleanup = () => {
            confirmDelete.removeEventListener("click", handleDelete);
            cancelDelete.removeEventListener("click", handleClose);
            closeButton.removeEventListener("click", handleClose);
            modal.removeEventListener("click", handleOutsideClick);
          };

          // Handle click outside modal
          const handleOutsideClick = (event) => {
            if (!modalContent.contains(event.target)) {
              handleClose();
            }
          };

          // Add event listeners
          confirmDelete.addEventListener("click", handleDelete);
          cancelDelete.addEventListener("click", handleClose);
          closeButton.addEventListener("click", handleClose);
          modal.addEventListener("click", handleOutsideClick);
        });
      });
    </script>
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
          class="{% if not loop.last %}border-b border-slate-200 dark:border-slate-700{% endif %}"
        >
          {% for field in document %}
          <td
            class="font-normal leading-normal px-4 py-2 border-r border-slate-200 dark:border-slate-700 last:border-r-0"
          >
            {% if field.type == 'ButtonField' %}
            <div class="flex justify-start items-center">
              <a href="{{field.link}}/{{field.id}}" class="w-full">
                <button
                  type="button"
                  class="btn btn-primary btn-outline btn-sm {{field.class}} truncate"
                >
                  {{field.label}}
                </button>
              </a>
            </div>
            {% else %} {{field.value}} {% endif %}
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
                class="btn btn-error btn-sm btn-outline delete-btn"
                data-id="{{document[0].id}}"
                data-type="{{collection_name}}"
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
          class="badge badge-outline badge-primary dropdown-toggle"
          data-dropdown-toggle
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

      // Check localStorage for saved model
      if (localStorage.getItem('selected_model') !== null) {
        selected_model = localStorage.getItem('selected_model');
        const model = models.find(m => m.model === selected_model);
        if (model) {
          selected_model_name = model.name;
        }
      }

      selectedModelElement.innerText = selected_model_name;

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
  <title>Fireworks</title>
  <link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/output.css') }}"
  />
  <link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/flatpickr.min.css') }}"
  />
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
                    onclick="handleDeleteHistory()"
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
    if (
      !confirm(
        "Are you sure you want to delete all history documents? This action cannot be undone.",
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        "{{ url_for('dms_chat.delete_all_history') }}",
        {
          method: "POST",
          headers: {
            "X-CSRFToken": "{{ csrf_token() }}",
          },
        },
      );

      if (!response.ok) {
        throw new Error("Failed to delete history");
      }

      const result = await response.json();

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
    } catch (error) {
      console.error("Error deleting history:", error);
      showErrorNotification("Failed to delete history. Please try again.");
    }
  }

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
```

