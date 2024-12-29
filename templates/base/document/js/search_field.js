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
        `{{ url_for("list", name="__MODULE__", mode="json") }}`.replace(
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
