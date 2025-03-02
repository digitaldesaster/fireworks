import { displayedFileIds, displayFileBanner } from "./chat_file_upload.js";
import { appendNormalText, appendImage } from "./chat_markup.js";
import { appendData } from "./chat_message_handler.js";
import { scrollToBottom } from "./chat_utils.js";
import { initializeCopyButtons } from "./chat_copy_handler.js";

function addBotMessage(text) {
  const template = document
    .getElementById("bot-message-template")
    .content.cloneNode(true);
  const contentElement = template.querySelector(".content");

  // Hide the copy button initially - it will be shown after streaming completes
  const copyButtonContainer = template.querySelector(".flex.justify-start");
  if (copyButtonContainer) {
    copyButtonContainer.classList.add("hidden");
    copyButtonContainer.style.display = "none";
  }

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

  // Initialize copy buttons for the newly added bot message
  requestAnimationFrame(() => {
    initializeCopyButtons();
  });

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
  initializeCopyButtons();
} else {
  document.addEventListener("DOMContentLoaded", () => {
    initChatMessages();
    initializeCopyButtons();
  });
}

export { initChatMessages, addBotMessage, addUserMessage };
