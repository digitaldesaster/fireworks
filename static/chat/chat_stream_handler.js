import {
  isInCodeBlock,
  currentCodeElement,
  codeLanguage,
  createCodeElement,
  resetCodeBlockState,
  setIsInCodeBlock,
  setCurrentCodeElement,
  setCodeLanguage,
} from "./chat_code_handler.js";

import { appendNormalText } from "./chat_markup.js";
import { saveChatData } from "./chat_save.js";
import { scrollToBottom } from "./chat_utils.js";
import { toggleButtonVisibility } from "./chat_event_handler.js";

function debug(message) {
  console.log(`[StreamHandler] ${message}`);
}

// Simplify the backtick detection approach
let backtickBuffer = "";
let waitingForLineBreak = false;
let languageBuffer = "";

// Function to clean up any stray backticks that might appear in the text
function cleanupBackticks(text) {
  if (!text) return "";

  // Only remove backticks that are likely part of incomplete code block markers
  let cleaned = text;

  // Check for trailing backticks that might be part of an incomplete code block marker
  if (cleaned.endsWith("```")) {
    cleaned = cleaned.slice(0, -3);
    debug("Removed trailing triple backticks");
  } else if (cleaned.endsWith("``")) {
    // Only remove double backticks, as they're likely part of an incomplete marker
    cleaned = cleaned.slice(0, -2);
    debug("Removed trailing double backticks");
  }

  // Check for leading backticks that might be part of an incomplete code block marker
  if (cleaned.startsWith("```")) {
    cleaned = cleaned.slice(3);
    debug("Removed leading triple backticks");
  } else if (cleaned.startsWith("``") && !cleaned.startsWith("```")) {
    // Only remove double backticks, as they're likely part of an incomplete marker
    cleaned = cleaned.slice(2);
    debug("Removed leading double backticks");
  }

  return cleaned;
}

// Simplified function to check for backticks
function checkForBackticks(text, startIndex) {
  for (let i = startIndex; i < text.length; i++) {
    const char = text[i];

    // If we're waiting for a line break to get the language
    if (waitingForLineBreak) {
      if (char === "\n") {
        // We found the line break, extract the language
        const language = languageBuffer.trim();
        waitingForLineBreak = false;
        languageBuffer = "";
        return {
          type: "language",
          index: i,
          language: language,
        };
      } else {
        // Accumulate characters for language detection
        languageBuffer += char;
      }
    }
    // Otherwise check for backticks
    else if (char === "`") {
      backtickBuffer += char;

      // If we have three backticks, we've found a marker
      if (backtickBuffer === "```") {
        backtickBuffer = ""; // Reset the buffer

        // If we're not in a code block, we need to wait for language
        if (!isInCodeBlock) {
          waitingForLineBreak = true;
          languageBuffer = "";
          return {
            type: "start",
            index: i - 2,
          };
        } else {
          // We're in a code block, so this is an end marker
          return {
            type: "end",
            index: i - 2,
          };
        }
      }
    }
    // If we find a non-backtick, reset the buffer
    // But only reset if the buffer has 1 or 2 backticks - incomplete code block markers
    // If we have a single backtick followed by text, it could be legitimate inline code
    else if (backtickBuffer.length > 0) {
      // Only reset if we have an incomplete code block marker (1-2 backticks)
      // Single backticks may be part of inline code and shouldn't trigger a reset
      if (backtickBuffer.length >= 2) {
        backtickBuffer = "";
      } else {
        // For single backticks, we need to check the next few characters
        // to determine if it's likely inline code or the start of a code block

        // Look ahead to see if this is followed by more backticks (potential code block)
        // or by text (likely inline code)
        let isLikelyInlineCode = true;

        // Check next character - if it's another backtick, keep the buffer
        if (i + 1 < text.length && text[i + 1] === "`") {
          isLikelyInlineCode = false;
        } else {
          // If it's not another backtick, it's likely inline code, so reset
          backtickBuffer = "";
        }
      }
    }
  }

  // If we reach the end with backticks in the buffer, log it
  if (backtickBuffer.length > 0) {
    debug(`End of text reached with backtick buffer: "${backtickBuffer}"`);
  }

  return { type: "none" };
}

async function handleStream(response, botMessageElement, messages) {
  if (!response.body) {
    throw new Error("Failed to get a readable stream from the response");
  }

  const reader = response.body.getReader();
  let accumulatedResponse = "";
  let lastProcessedIndex = 0;
  let textContainer = document.createElement("div");
  textContainer.className = "w-full";
  botMessageElement.appendChild(textContainer);

  // Reset state variables
  backtickBuffer = "";
  waitingForLineBreak = false;
  languageBuffer = "";
  debug("Reset all state variables");

  while (true) {
    const { done, value } = await reader.read();
    if (done || window.stop_stream) {
      debug("Stream ended or stopped");

      // Handle any remaining text
      if (lastProcessedIndex < accumulatedResponse.length) {
        const remainingText = cleanupBackticks(
          accumulatedResponse.substring(lastProcessedIndex),
        );

        if (isInCodeBlock) {
          if (currentCodeElement && currentCodeElement.querySelector("pre")) {
            currentCodeElement.querySelector("pre").textContent +=
              remainingText;
          }
          // Ensure we close any open code blocks at the end of the stream
          resetCodeBlockState();
        } else if (remainingText.trim()) {
          appendNormalText(textContainer, remainingText);
        }
      }

      // Reset any lingering state
      backtickBuffer = "";
      waitingForLineBreak = false;
      languageBuffer = "";

      messages.push({ role: "assistant", content: accumulatedResponse });
      await saveChatData(messages);
      return accumulatedResponse;
    }

    const text = new TextDecoder().decode(value);
    debug(`Received chunk of ${text.length} characters`);

    accumulatedResponse += text;

    // Process the accumulated response
    while (lastProcessedIndex < accumulatedResponse.length) {
      const result = checkForBackticks(accumulatedResponse, lastProcessedIndex);

      if (result.type === "start") {
        // We found the start of a code block
        debug("Found start of code block");

        // Handle text before the code block
        const textBefore = cleanupBackticks(
          accumulatedResponse.substring(lastProcessedIndex, result.index),
        );
        if (textBefore.trim()) {
          appendNormalText(textContainer, textBefore);
        }

        // Skip the backticks
        lastProcessedIndex = result.index + 3;

        // We'll wait for the language in the next iteration
      } else if (result.type === "language") {
        // We found the language line
        debug(`Setting up code block with language: "${result.language}"`);

        // Skip the language line
        lastProcessedIndex = result.index + 1;

        // Start a new code block
        setIsInCodeBlock(true);
        setCodeLanguage(result.language);

        // Create code element with the detected language
        const codeEl = createCodeElement(result.language);

        // No need for additional styling adjustments as the template already includes the proper classes
        // and createCodeElement handles the language-specific styling

        setCurrentCodeElement(codeEl);
        botMessageElement.appendChild(codeEl);
      } else if (result.type === "end") {
        // We found the end of a code block
        debug("Found end of code block");

        // Handle the code content up to the backticks
        const codeContent = accumulatedResponse.substring(
          lastProcessedIndex,
          result.index,
        );

        if (
          codeContent &&
          currentCodeElement &&
          currentCodeElement.querySelector("pre")
        ) {
          // Ensure we don't have any stray backticks at the end of the code content
          let cleanContent = codeContent;

          // Remove any trailing triple or double backticks that might have been accidentally included
          // But preserve single backticks which might be legitimate inline code
          if (cleanContent.endsWith("```")) {
            cleanContent = cleanContent.slice(0, -3);
            debug("Removed trailing triple backticks from code content");
          } else if (cleanContent.endsWith("``")) {
            cleanContent = cleanContent.slice(0, -2);
            debug("Removed trailing double backticks from code content");
          }

          currentCodeElement.querySelector("pre").textContent += cleanContent;
        }

        // End the code block
        resetCodeBlockState();
        // Skip past the closing backticks (```)
        lastProcessedIndex = result.index + 3;

        // Create new text container for content after code block
        textContainer = document.createElement("div");
        textContainer.className = "w-full";
        botMessageElement.appendChild(textContainer);
      } else {
        // No special markers, just append text
        if (isInCodeBlock) {
          // We're in a code block, append to the code element
          const pendingCode = accumulatedResponse.substring(lastProcessedIndex);

          if (
            pendingCode &&
            currentCodeElement &&
            currentCodeElement.querySelector("pre")
          ) {
            // Ensure we don't have stray backticks in the pending code
            let cleanPendingCode = pendingCode;

            // Check for incomplete backtick sequences that might be part of closing markers
            if (cleanPendingCode.includes("```")) {
              // If we find triple backticks, only include text up to that point
              // as it's likely a closing marker in the next chunk
              const tripleBacktickIndex = cleanPendingCode.indexOf("```");
              if (tripleBacktickIndex >= 0) {
                cleanPendingCode = cleanPendingCode.substring(
                  0,
                  tripleBacktickIndex,
                );
              }
            } else if (cleanPendingCode.includes("``")) {
              // If we find double backticks, only include text up to that point
              // as it might be part of a closing marker in the next chunk
              const doubleBacktickIndex = cleanPendingCode.indexOf("``");
              if (doubleBacktickIndex >= 0) {
                cleanPendingCode = cleanPendingCode.substring(
                  0,
                  doubleBacktickIndex,
                );
              }
            }
            // Note: We deliberately don't check for single backticks here
            // as they might be legitimate inline code

            currentCodeElement.querySelector("pre").textContent +=
              cleanPendingCode;
          }
        } else {
          // We're not in a code block, append as normal text
          const textToAppend = cleanupBackticks(
            accumulatedResponse.substring(lastProcessedIndex),
          );

          if (textToAppend.trim()) {
            debug("Appending normal text");
            appendNormalText(textContainer, textToAppend);
          }
        }
        lastProcessedIndex = accumulatedResponse.length;
        break;
      }
    }

    scrollToBottom();

    // Check for stream end marker
    const stopIndex = accumulatedResponse.indexOf("###STOP###");
    if (stopIndex !== -1) {
      accumulatedResponse = accumulatedResponse.substring(0, stopIndex);
      messages.push({ role: "assistant", content: accumulatedResponse });
      await saveChatData(messages);
      return accumulatedResponse;
    }
  }
}

export { handleStream };
