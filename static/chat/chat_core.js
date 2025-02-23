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
  console.log("- username:", username);
  console.log("- messages:", JSON.stringify(messages, null, 2));

  if (!chat_started || !username) {
    console.error("Missing required data for saving chat:");
    console.error("- chat_started:", chat_started);
    console.error("- username:", username);
    return Promise.reject(new Error("Missing required data for saving chat"));
  }

  // Get CSRF token from meta tag
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  // Create FormData
  const formData = new FormData();
  formData.append("username", username);
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
  const textNode = document.createTextNode(text);
  container.appendChild(textNode);
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
