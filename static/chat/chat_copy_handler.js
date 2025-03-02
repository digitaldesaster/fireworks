// This file handles the copy functionality for bot messages and code blocks

/**
 * Initialize copy button functionality for all message content and code blocks
 * This will be called whenever new messages are added to the DOM
 */
function initializeCopyButtons() {
  // Initialize message copy buttons
  initializeMessageCopyButtons();

  // Initialize code block copy buttons
  initializeCodeBlockCopyButtons();
}

/**
 * Initialize copy buttons for bot messages
 */
function initializeMessageCopyButtons() {
  // Get all copy buttons with the data-action="copy-message" attribute
  document
    .querySelectorAll('button[data-action="copy-message"]')
    .forEach((button) => {
      // Skip buttons that already have listeners
      if (button.hasAttribute("data-listener-attached")) return;

      // Mark this button as having a listener attached
      button.setAttribute("data-listener-attached", "true");

      // Find related elements
      const copyIcon = button.querySelector(".copy-icon");
      const checkIcon = button.querySelector(".check-icon");
      const copyText = button.querySelector(".copy-text");
      const checkText = button.querySelector(".check-text");

      // Find the content element (the message content to be copied)
      const messageContainer = button.closest(".flex-1");
      const contentElement = messageContainer.querySelector(".content");

      button.addEventListener("click", async () => {
        try {
          // Create a clean representation of the message content for copying
          const textParts = [];

          // Traverse the DOM and extract content appropriately
          collectTextContent(contentElement, textParts);

          // Join all parts and clean up whitespace
          let textContent = textParts.join("");

          // Normalize spacing - only clean up excessive whitespace while preserving meaningful spaces
          textContent = textContent
            .replace(/\n{3,}/g, "\n\n") // Replace 3+ newlines with 2
            .replace(/[ \t]{2,}/g, " ") // Replace multiple spaces with a single space
            .replace(/[ \t]+\n/g, "\n") // Remove spaces before newlines
            .replace(/\n[ \t]+/g, "\n") // Remove spaces after newlines
            .trim();

          // Copy to clipboard
          await navigator.clipboard.writeText(textContent);

          // Visual feedback
          copyIcon.classList.add("hidden");
          checkIcon.classList.remove("hidden");
          copyText.classList.add("hidden");
          checkText.classList.remove("hidden");
          button.classList.add("text-success", "bg-success/10");

          // Reset after 2 seconds
          setTimeout(() => {
            copyIcon.classList.remove("hidden");
            checkIcon.classList.add("hidden");
            copyText.classList.remove("hidden");
            checkText.classList.add("hidden");
            button.classList.remove("text-success", "bg-success/10");
          }, 2000);
        } catch (err) {
          console.error("Failed to copy content:", err);
        }
      });
    });
}

/**
 * Recursively collect text content from DOM elements with special handling for code blocks
 */
function collectTextContent(element, parts) {
  // Skip hidden elements
  if (
    element.classList &&
    (element.classList.contains("hidden") ||
      element.classList.contains("loading"))
  ) {
    return;
  }

  // Special handling for code blocks
  if (
    element.classList &&
    element.classList.contains("flex") &&
    element.classList.contains("flex-col") &&
    element.classList.contains("w-full")
  ) {
    const pre = element.querySelector("pre");
    const languageInfo = element.querySelector(".language-info");

    if (pre) {
      // Get language if available
      let language = "";
      if (languageInfo && languageInfo.textContent.trim()) {
        language = languageInfo.textContent.trim();
      }

      // Get code content and ensure it doesn't already have backticks at the end
      let codeContent = pre.textContent.trim();

      // Remove any trailing backticks that might have been accidentally included
      // But preserve single backticks as they might be legitimate inline code
      if (codeContent.endsWith("```")) {
        codeContent = codeContent.slice(0, -3);
      } else if (codeContent.endsWith("``")) {
        codeContent = codeContent.slice(0, -2);
      }

      // Format as a code block with triple backticks
      parts.push(`\n\n\`\`\`${language}\n${codeContent}\n\`\`\`\n\n`);
    }
    return;
  }

  // Handle text nodes directly
  if (element.nodeType === Node.TEXT_NODE) {
    // Add the raw text without trimming or adding spaces
    const text = element.textContent;
    if (text) {
      parts.push(text);
    }
    return;
  }

  // For block-level elements, ensure we have appropriate spacing
  const isBlockElement =
    element.tagName &&
    [
      "DIV",
      "P",
      "H1",
      "H2",
      "H3",
      "H4",
      "H5",
      "H6",
      "LI",
      "BLOCKQUOTE",
      "UL",
      "OL",
    ].includes(element.tagName);

  // If this is a block element, add newline before if needed
  if (isBlockElement) {
    const lastPart = parts.length > 0 ? parts[parts.length - 1] : "";
    if (lastPart && !lastPart.endsWith("\n")) {
      parts.push("\n");
    }
  }

  // Recursively process child nodes
  if (element.childNodes && element.childNodes.length > 0) {
    Array.from(element.childNodes).forEach((child) => {
      collectTextContent(child, parts);
    });
  } else if (element.nodeType === Node.ELEMENT_NODE) {
    // For elements without children, add their text content
    const text = element.textContent;
    if (text) {
      parts.push(text);
    }
  }

  // If this is a block element, add newline after if needed
  if (isBlockElement) {
    const lastPart = parts.length > 0 ? parts[parts.length - 1] : "";
    if (lastPart && !lastPart.endsWith("\n")) {
      parts.push("\n");
    }
  }
}

/**
 * Initialize copy buttons for code blocks
 */
function initializeCodeBlockCopyButtons() {
  // Get all copy buttons with the data-action="copy-code-block" attribute
  document
    .querySelectorAll('button[data-action="copy-code-block"]')
    .forEach((button) => {
      // Skip buttons that already have listeners
      if (button.hasAttribute("data-listener-attached")) return;

      // Mark this button as having a listener attached
      button.setAttribute("data-listener-attached", "true");

      // Find related elements
      const copyIcon = button.querySelector(".copy-icon");
      const checkIcon = button.querySelector(".check-icon");
      const copyText = button.querySelector(".copy-text");
      const checkText = button.querySelector(".check-text");

      // Find the code element (the code block to be copied)
      const codeBlock = button.closest(".flex.flex-col.w-full");
      const preElement = codeBlock.querySelector("pre");

      button.addEventListener("click", async () => {
        try {
          // Get code content
          const codeContent = preElement.textContent;

          // Copy to clipboard
          await navigator.clipboard.writeText(codeContent);

          // Visual feedback
          copyIcon.classList.add("hidden");
          checkIcon.classList.remove("hidden");
          copyText.classList.add("hidden");
          checkText.classList.remove("hidden");
          button.classList.add(
            "text-green-500",
            "dark:text-green-400",
            "bg-green-500/10",
          );

          // Reset after 2 seconds
          setTimeout(() => {
            copyIcon.classList.remove("hidden");
            checkIcon.classList.add("hidden");
            copyText.classList.remove("hidden");
            checkText.classList.add("hidden");
            button.classList.remove(
              "text-green-500",
              "dark:text-green-400",
              "bg-green-500/10",
            );
          }, 2000);
        } catch (err) {
          console.error("Failed to copy code block:", err);
        }
      });
    });
}

// Initialize copy buttons when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", initializeCopyButtons);

// Also initialize after any dynamic content is added
const chatMessagesObserver = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.addedNodes.length) {
      initializeCopyButtons();
    }
  });
});

// Start observing the chat messages container
document.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chat_messages");
  if (chatMessages) {
    chatMessagesObserver.observe(chatMessages, {
      childList: true,
      subtree: true,
    });
  }
});

export { initializeCopyButtons };
