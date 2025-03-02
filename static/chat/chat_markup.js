function appendNormalText(container, text) {
  const textNode = document.createTextNode(text);
  container.appendChild(textNode);
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

function appendImage(container, imageData) {
  const img = document.createElement("img");
  img.src = imageData.image_url.url;
  img.className = "w-16 h-auto rounded-lg";
  container.appendChild(img);
}

// Export the functions
export { appendNormalText, processInlineMarkdown, appendImage };
