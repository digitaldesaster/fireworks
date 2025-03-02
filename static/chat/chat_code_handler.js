let isInCodeBlock = false;
let currentCodeElement = null;
let codeLanguage = "";

function debug(message) {
  console.log(`[CodeHandler] ${message}`);
}

function resetCodeBlockState() {
  debug("Resetting code block state");
  isInCodeBlock = false;
  currentCodeElement = null;
  codeLanguage = "";
}

function setIsInCodeBlock(value) {
  debug(value ? "Code block started." : "Code block ended.");
  isInCodeBlock = value;
}

function setCurrentCodeElement(value) {
  currentCodeElement = value;
}

function setCodeLanguage(value) {
  codeLanguage = value;
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

  // Add the data attribute to identify this as a code block copy button
  const copyButton = importedNode.querySelector(".copy-btn");
  copyButton.setAttribute("data-action", "copy-code-block");

  // IMPORTANT: Add the event listener to the COPY button of this specific instance BEFORE appending to the container
  const copiedInfo = importedNode.querySelector(".copied");

  container.appendChild(importedNode);
}

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

function createCodeElement(language = "") {
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
  const languageInfoElement = codeElement.querySelector(".language-info");

  // Add a data attribute to identify this as a code block copy button
  copyButton.setAttribute("data-action", "copy-code-block");

  // Apply consistent styling to ensure the code block background works properly
  codeElement.classList.add("code-block-container", "overflow-hidden");

  // Set the language if provided
  if (language && languageInfoElement) {
    languageInfoElement.textContent = language;
    debug(`Setting code block language to: ${language}`);
  } else if (preElement) {
    // If no language provided, adjust the styling for the pre element
    preElement.classList.remove("rounded-b");
    preElement.classList.add("rounded");
  }

  return codeElement;
}

// Export the variables and functions
export {
  isInCodeBlock,
  currentCodeElement,
  codeLanguage,
  appendCodeBlock,
  appendCodeText,
  createCodeElement,
  resetCodeBlockState,
  setIsInCodeBlock,
  setCurrentCodeElement,
  setCodeLanguage,
};
