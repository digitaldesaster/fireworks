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
    // Show the copied message
    copiedInfo.classList.remove("hidden");
    copyButton.classList.add("hidden");
    
    // Hide the copied message and show the button after 2 seconds
    setTimeout(() => {
      copiedInfo.classList.add("hidden");
      copyButton.classList.remove("hidden");
    }, 2000);
    navigator.clipboard
      .writeText(preElement.textContent)
      .then(() => {
        console.log("Text copied to clipboard");
      })
      .catch((err) => {
        console.error("Failed to copy text:", err);
      });
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
  // Clear any existing content
  botMessageElement.innerHTML = "";

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

  // First handle code blocks
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

async function stopStreaming() {
  // Set the flag to true to stop streaming
  stop_stream = true;
}

function appendNormalText(container, text) {
  // Split text into lines to process each line separately
  const lines = text.split("\n");
  let inList = false;
  let listElement = null;
  let inTable = false;
  let tableElement = null;
  let tableHeader = false;

  // New structure for managing lists
  const listContext = {
    lists: [], // Stack of list elements
    indentLevels: [], // Corresponding indent levels
  };

  lines.forEach((line, index) => {
    // Check for horizontal rule
    if (line.match(/^[\-*_]{3,}$/)) {
      // End any open lists
      if (inList) {
        inList = false;
      }
      if (inTable) {
        container.appendChild(tableElement);
        inTable = false;
      }
      const hr = document.createElement("hr");
      hr.className = "my-4 border-t-2 border-base-content/20";
      container.appendChild(hr);
      return;
    }

    // Check for table
    const tableMatch = line.match(/^\|(.+)\|$/);
    if (tableMatch) {
      const cells = tableMatch[1].split("|").map((cell) => cell.trim());

      if (!inTable) {
        tableElement = document.createElement("table");
        tableElement.className =
          "min-w-full my-4 border-collapse border border-base-content/20";
        inTable = true;
        tableHeader = true;
      }

      const row = document
        .createElement(tableHeader ? "thead" : "tbody")
        .appendChild(document.createElement("tr"));
      row.className = tableHeader ? "bg-base-200" : "";

      cells.forEach((cell) => {
        const td = document.createElement(tableHeader ? "th" : "td");
        td.className = "border border-base-content/20 px-4 py-2 text-left";
        td.innerHTML = processInlineMarkdown(cell);
        row.appendChild(td);
      });

      if (tableHeader) {
        tableElement.appendChild(row.parentElement);
        tableHeader = false;
      } else {
        tableElement.appendChild(row.parentElement);
      }
      return;
    } else if (inTable) {
      container.appendChild(tableElement);
      inTable = false;
    }

    // Check for heading patterns
    const h1Match = line.match(/^# (.*)/);
    const h2Match = line.match(/^## (.*)/);
    const h3Match = line.match(/^### (.*)/);

    // Check for list patterns
    const indentedListMatch = line.match(/^(\s+)([\*\-]|\d+\.)\s+(.*)/);
    const ulMatch = line.match(/^[\*\-] (.*)/);
    const olMatch = line.match(/^(\d+)\. (.*)/);
    const taskMatch = line.match(/^[\*\-] \[([ x])\] (.*)/);
    const nestedQuoteMatch = line.match(/^>+ (.*)/);

    if (nestedQuoteMatch) {
      // End any open lists
      if (listContext.lists.length > 0) {
        cleanupLists(container, listContext);
      }

      const quoteDepth = line.match(/^>+/)[0].length;
      const blockquote = document.createElement("blockquote");
      // Reduced spacing for blockquotes
      blockquote.className = `border-l-4 pl-4 py-2 my-2 ml-${(quoteDepth - 1) * 4}`;

      // Adjust styling based on nesting level
      switch (quoteDepth) {
        case 1:
          blockquote.classList.add(
            "border-primary/50",
            "text-base-content",
            "bg-base-200",
          );
          break;
        case 2:
          blockquote.classList.add(
            "border-secondary/50",
            "text-base-content",
            "bg-base-200/70",
          );
          break;
        case 3:
          blockquote.classList.add(
            "border-accent/50",
            "text-base-content",
            "bg-base-300",
          );
          break;
        default:
          blockquote.classList.add(
            "border-base-content/30",
            "text-base-content",
            "bg-base-300",
          );
      }

      blockquote.innerHTML = processInlineMarkdown(nestedQuoteMatch[1]);
      container.appendChild(blockquote);
    } else if (h1Match || h2Match || h3Match) {
      // End any open lists
      if (listContext.lists.length > 0) {
        cleanupLists(container, listContext);
      }

      // Handle headings (existing code)
      if (h1Match) {
        const h1 = document.createElement("h1");
        h1.className = "text-2xl font-bold mt-1 mb-3 text-base-content";
        h1.innerHTML = processInlineMarkdown(h1Match[1]);
        container.appendChild(h1);
      } else if (h2Match) {
        const h2 = document.createElement("h2");
        h2.className = "text-xl font-bold mt-1 mb-1 text-base-content";
        h2.innerHTML = processInlineMarkdown(h2Match[1]);
        container.appendChild(h2);
      } else if (h3Match) {
        const h3 = document.createElement("h3");
        h3.className = "text-lg font-bold mt-1 mb-1 text-base-content";
        h3.innerHTML = processInlineMarkdown(h3Match[1]);
        container.appendChild(h3);
      }
    } else if (indentedListMatch || ulMatch || olMatch) {
      // Process any type of list item (indented or not)
      let indentation = 0;
      let listMarker = "";
      let content = "";
      let isIndented = false;

      if (indentedListMatch) {
        indentation = indentedListMatch[1].length;
        listMarker = indentedListMatch[2];
        content = indentedListMatch[3];
        isIndented = true;
      } else if (ulMatch) {
        listMarker = "*";
        content = ulMatch[1];
      } else if (olMatch) {
        listMarker = olMatch[1] + ".";
        content = olMatch[2];
      }

      const isOrdered = listMarker.includes(".");
      const listType = isOrdered ? "ol" : "ul";

      // Handle list nesting
      processListItem(container, listContext, {
        indentation,
        listType,
        content,
        listMarker,
        isIndented,
      });

      inList = true;
    } else if (taskMatch) {
      // Clean up any lists with different indentation
      while (
        listContext.lists.length > 0 &&
        listContext.lists[listContext.lists.length - 1].tagName !== "UL"
      ) {
        listContext.lists.pop();
        listContext.indentLevels.pop();
      }

      // Create UL if needed
      if (listContext.lists.length === 0) {
        const ul = document.createElement("ul");
        ul.className = "mb-2";
        container.appendChild(ul);
        listContext.lists.push(ul);
        listContext.indentLevels.push(0);
      }

      // Create the task list item
      const li = document.createElement("li");
      li.className = "text-base-content mb-1 flex items-center";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = taskMatch[1] === "x";
      checkbox.disabled = true;
      checkbox.className = "mr-2";
      li.appendChild(checkbox);
      const textSpan = document.createElement("span");
      textSpan.innerHTML = processInlineMarkdown(taskMatch[2]);
      li.appendChild(textSpan);

      // Add to the current list
      listContext.lists[listContext.lists.length - 1].appendChild(li);

      inList = true;
    } else {
      // Handle non-list content - clean up any open lists
      if (listContext.lists.length > 0) {
        cleanupLists(container, listContext);
      }

      if (line === "") {
        const spacer = document.createElement("div");
        spacer.className = "h-1"; // Reduced empty line height
        container.appendChild(spacer);
      } else {
        const p = document.createElement("p");
        p.className = "mb-1 text-base-content"; // Reduced margin
        p.innerHTML = processInlineMarkdown(line);
        container.appendChild(p);
      }

      inList = false;
    }
  });

  // Clean up any remaining lists
  if (listContext.lists.length > 0) {
    cleanupLists(container, listContext);
  }

  // Clean up any remaining table
  if (inTable) {
    container.appendChild(tableElement);
  }

  // Remove the last margin-bottom from the last element if it has one
  const lastElement = container.lastElementChild;
  if (lastElement) {
    lastElement.classList.remove("mb-0.5", "mb-1", "mb-2");
  }
}

// Helper function to clean up any open lists
function cleanupLists(container, listContext) {
  if (listContext.lists.length > 0) {
    container.appendChild(listContext.lists[0]);
    listContext.lists = [];
    listContext.indentLevels = [];
  }
}

// Helper function to process a list item and handle nesting properly
function processListItem(container, listContext, item) {
  const { indentation, listType, content, listMarker, isIndented } = item;

  // Adjust the list stack based on indentation
  if (isIndented) {
    // Remove lists at greater indentation levels
    while (
      listContext.lists.length > 0 &&
      listContext.indentLevels[listContext.indentLevels.length - 1] >=
        indentation
    ) {
      listContext.lists.pop();
      listContext.indentLevels.pop();
    }
  } else {
    // For non-indented items, clear lists and create a new top-level list
    listContext.lists = [];
    listContext.indentLevels = [];
  }

  // Create list item
  const li = document.createElement("li");
  li.className = "text-base-content mb-0.5";

  // Add bullet or number
  if (listType === "ul") {
    const bulletPoint = document.createElement("span");
    bulletPoint.className = "inline-block w-4";
    bulletPoint.textContent = "•";
    li.appendChild(bulletPoint);
  } else {
    const numberPoint = document.createElement("span");
    numberPoint.className = "inline-block w-4";
    const num = listMarker.replace(".", "");
    numberPoint.textContent = num + ".";
    if (parseInt(num)) {
      li.value = parseInt(num);
    }
    li.appendChild(numberPoint);
  }

  // Add content
  const textSpan = document.createElement("span");
  textSpan.innerHTML = processInlineMarkdown(content);
  li.appendChild(textSpan);

  // Find or create the appropriate list
  let parentList;

  if (listContext.lists.length === 0) {
    // Create a new top-level list
    parentList = document.createElement(listType);
    parentList.className = "mb-2";

    if (isIndented) {
      // This is an indented item without a parent - rare case
      container.appendChild(parentList);
    } else {
      // Normal top-level list
      container.appendChild(parentList);
    }

    listContext.lists.push(parentList);
    listContext.indentLevels.push(indentation);
  } else {
    // Get the current deepest list
    const currentList = listContext.lists[listContext.lists.length - 1];

    if (isIndented) {
      // This is a nested list item - create a new list inside the last list item
      const parentLi = currentList.lastElementChild;

      // Check if parent already has a list of this type
      let nestedList = null;
      if (parentLi) {
        for (let i = 0; i < parentLi.children.length; i++) {
          const child = parentLi.children[i];
          if (child.tagName && child.tagName.toLowerCase() === listType) {
            nestedList = child;
            break;
          }
        }
      }

      if (!nestedList && parentLi) {
        // Create a new nested list
        nestedList = document.createElement(listType);
        nestedList.className = "ml-6 mt-1 pl-2 border-l border-base-content/20";
        parentLi.appendChild(nestedList);
      }

      parentList = nestedList || currentList;

      if (nestedList) {
        // Add the new list to our context
        listContext.lists.push(nestedList);
        listContext.indentLevels.push(indentation);
      }
    } else {
      // This is a new item at the same level as the current list
      parentList = currentList;
    }
  }

  // Add the list item to the appropriate list
  if (parentList) {
    parentList.appendChild(li);
  }
}

function processInlineMarkdown(text) {
  // Process blockquotes (now handled in appendNormalText for nesting support)
  if (text.startsWith("> ")) {
    return `<blockquote class="border-l-4 border-base-content/20 pl-4 py-2 my-2 italic text-base-content/70">${text.substring(2)}</blockquote>`;
  }

  // Process inline code first (to avoid conflicts with other syntax)
  text = text.replace(
    /`([^`]+)`/g,
    '<code class="bg-base-300 px-1 py-0.5 rounded text-sm font-mono">$1</code>',
  );

  // Process bold and italic
  text = text.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong class="font-bold">$1</strong>',
  );
  text = text.replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>');
  text = text.replace(/_([^_]+)_/g, '<em class="italic">$1</em>');

  // Process links
  text = text.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" class="text-primary hover:underline" target="_blank" rel="noopener noreferrer">$1</a>',
  );

  // Process strikethrough
  text = text.replace(/~~([^~]+)~~/, '<del class="line-through">$1</del>');

  return text;
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
  const copyButton = template.querySelector(".copy-btn");
  const copyIcon = copyButton.querySelector(".copy-icon");
  const checkIcon = copyButton.querySelector(".check-icon");
  const copyText = copyButton.querySelector(".copy-text");
  const checkText = copyButton.querySelector(".check-text");

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

  // Add copy functionality
  copyButton.addEventListener("click", async () => {
    // Create a temporary div to handle HTML content
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = contentElement.innerHTML;

    // Remove any loading indicators if present
    const loadingElements = tempDiv.getElementsByClassName("loading");
    while (loadingElements.length > 0) {
      loadingElements[0].remove();
    }

    // Function to inline Tailwind styles
    function inlineStyles(element) {
      const styles = window.getComputedStyle(element);
      const inlineStyle = {};
      for (let prop of styles) {
        inlineStyle[prop] = styles.getPropertyValue(prop);
      }
      element.style.cssText = Object.entries(inlineStyle)
        .map(([prop, value]) => `${prop}: ${value}`)
        .join("; ");

      // Process children
      Array.from(element.children).forEach((child) => inlineStyles(child));
    }

    // Clone the content and inline styles
    const clonedContent = contentElement.cloneNode(true);
    document.body.appendChild(clonedContent);
    inlineStyles(clonedContent);
    const styledHTML = clonedContent.outerHTML;
    document.body.removeChild(clonedContent);

    try {
      // Create a Blob with HTML content
      const blob = new Blob([styledHTML], { type: "text/html" });
      const plainText = contentElement.textContent;

      // Create clipboard data with both formats
      await navigator.clipboard.write([
        new ClipboardItem({
          "text/html": blob,
          "text/plain": new Blob([plainText], { type: "text/plain" }),
        }),
      ]);

      // Visual feedback
      copyIcon.classList.add("hidden");
      checkIcon.classList.remove("hidden");
      copyText.classList.add("hidden");
      checkText.classList.remove("hidden");
      copyButton.classList.add("text-success", "bg-success/10");

      // Reset after 2 seconds
      setTimeout(() => {
        copyIcon.classList.remove("hidden");
        checkIcon.classList.add("hidden");
        copyText.classList.remove("hidden");
        checkText.classList.add("hidden");
        copyButton.classList.remove("text-success", "bg-success/10");
      }, 2000);
    } catch (err) {
      console.error("Failed to copy formatted content:", err);
      // Fallback to plain text
      navigator.clipboard.writeText(contentElement.textContent);
    }
  });

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
