import { streamMessage } from "./chat_core.js";
import { displayedFileIds } from "./chat_file_upload.js";

function initializeEventHandlers() {
  // Chat button click handler
  document
    .getElementById("chat_button")
    .addEventListener("click", streamMessage);

  // Chat input keydown handler for Cmd/Ctrl + Enter
  document
    .getElementById("chat_input")
    .addEventListener("keydown", function (event) {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        streamMessage();
      }
    });

  // Reset button click handler
  document
    .getElementById("reset_button")
    .addEventListener("click", function () {
      displayedFileIds.clear();
      window.location.href = "/chat";
    });

  // Stop button click handler
  document
    .getElementById("stop_button")
    .addEventListener("click", stopStreaming);
}

function toggleButtonVisibility() {
  const chatButton = document.getElementById("chat_button");
  const stopButton = document.getElementById("stop_button");

  chatButton.classList.toggle("hidden");
  stopButton.classList.toggle("hidden");
}

async function stopStreaming() {
  window.stop_stream = true;
}

export { initializeEventHandlers, toggleButtonVisibility, stopStreaming };
