let uploadedFilesCount = 0;
let displayedFileIds = new Set();

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

// Export the functions and Set
export { displayedFileIds, createFileBanner, displayFileBanner };

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
