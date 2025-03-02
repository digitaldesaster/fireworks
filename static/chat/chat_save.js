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

export { saveChatData };
