import {
  isInCodeBlock,
  currentCodeElement,
  codeLanguage,
  appendCodeBlock,
  createCodeElement,
  resetCodeBlockState,
  setIsInCodeBlock,
  setCurrentCodeElement,
  setCodeLanguage,
  appendCodeText,
} from "./chat_code_handler.js";

import { initializeCopyButtons } from "./chat_copy_handler.js";

import {
  appendNormalText,
  processInlineMarkdown,
  appendImage,
} from "./chat_markup.js";

import {
  displayedFileIds,
  createFileBanner,
  displayFileBanner,
} from "./chat_file_upload.js";

import {
  initChatMessages,
  addBotMessage,
  addUserMessage,
} from "./chat_initialize.js";

import { scrollToBottom } from "./chat_utils.js";
import { saveChatData } from "./chat_save.js";
import { appendData } from "./chat_message_handler.js";
import { toggleButtonVisibility, stopStreaming } from "./chat_event_handler.js";
import { handleStream } from "./chat_stream_handler.js";

window.stop_stream = false;

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

    messages.push({ role: "user", content: userMessage });
    addUserMessage(userMessage);
    chatInput.value = "";

    toggleButtonVisibility();
    window.stop_stream = false;
    chatInput.readOnly = true;

    resetCodeBlockState();
    const botMessageElement = addBotMessage("");

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

      await handleStream(response, botMessageElement, messages);
      toggleButtonVisibility();
      chatInput.readOnly = false;
    } catch (error) {
      console.error("Streaming failed:", error);
      botMessageElement.textContent = `Error occurred: ${error.message}`;
      messages.push({
        role: "assistant",
        content: `Error occurred: ${error.message}`,
      });
      saveChatData(messages);
      toggleButtonVisibility();
      chatInput.readOnly = false;
    }
  }
}

export { streamMessage };
