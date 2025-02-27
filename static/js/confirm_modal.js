// Generic confirmation modal handler
class ConfirmModal {
  constructor(modalId) {
    this.modal = document.getElementById(modalId);
    if (!this.modal) {
      console.error(`Modal with ID ${modalId} not found in DOM`);
      return;
    }
    
    console.log(`Initializing modal: ${modalId}`, this.modal);
    
    // Find required elements with better error reporting
    this.modalContent = this.modal.querySelector('.modal-content');
    if (!this.modalContent) console.warn(`Modal content not found in ${modalId}`);
    
    this.confirmButton = this.modal.querySelector('button.confirm-action');
    if (!this.confirmButton) console.error(`Confirm button not found in ${modalId}`);
    
    this.cancelButton = this.modal.querySelector('button.cancel-action');
    if (!this.cancelButton) console.warn(`Cancel button not found in ${modalId}`);
    
    this.closeButton = this.modal.querySelector('button.close-modal');
    if (!this.closeButton) console.warn(`Close button not found in ${modalId}`);
    
    // Elements for dynamic content
    this.titleElement = this.modal.querySelector('h3');
    if (!this.titleElement) console.warn(`Title element (h3) not found in ${modalId}`);
    
    this.messageElement = this.modal.querySelector('p');
    if (!this.messageElement) console.warn(`Message element (p) not found in ${modalId}`);
    
    // Store modal ID for reference
    this.modalId = modalId;
    
    // Initialize with default data attributes
    this.actionUrl = '';
    this.redirectUrl = '';
    this.documentId = '';
    this.documentType = '';
    
    this.setupEventListeners();
  }

  setupEventListeners() {
    if (!this.modal) return;
    
    // Event listeners for closing the modal
    if (this.cancelButton) {
      this.cancelButton.addEventListener('click', (e) => {
        console.log('Cancel button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.hideModal();
      });
    }
    
    if (this.closeButton) {
      this.closeButton.addEventListener('click', (e) => {
        console.log('Close button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.hideModal();
      });
    }
    
    // Close modal when clicking outside
    this.modal.addEventListener('click', (event) => {
      if (this.modalContent && !this.modalContent.contains(event.target)) {
        console.log('Clicked outside modal');
        this.hideModal();
      }
    });
    
    // Handle confirm action
    if (this.confirmButton) {
      this.confirmButton.addEventListener('click', (e) => {
        console.log('Confirm button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.handleConfirmAction();
      });
    } else {
      console.error('Confirm button not found in modal');
    }
    
    // Set up event listeners for all trigger elements
    const modalTriggers = document.querySelectorAll(`[data-modal-target="${this.modalId}"]`);
    console.log(`Found ${modalTriggers.length} triggers for modal ${this.modalId}`);
    
    // Log each trigger for debugging
    modalTriggers.forEach((trigger, index) => {
      console.log(`Trigger ${index + 1}:`, {
        element: trigger.tagName,
        class: trigger.className,
        modalTarget: trigger.dataset.modalTarget,
        action: trigger.dataset.action,
        text: trigger.innerText.trim().substring(0, 20) + (trigger.innerText.length > 20 ? '...' : '')
      });
    });
    
    modalTriggers.forEach(trigger => {
      trigger.addEventListener('click', (event) => {
        console.log(`Modal trigger clicked for ${this.modalId}`, {
          trigger: event.currentTarget,
          action: event.currentTarget.dataset.action,
          message: event.currentTarget.dataset.message
        });
        
        this.updateModalFromTrigger(event.currentTarget);
        this.showModal();
      });
    });
  }

  showModal() {
    console.log(`Attempting to open modal ${this.modalId}`);
    
    if (!this.modal) {
      console.error(`Cannot open modal: Modal with ID ${this.modalId} not found`);
      
      // Fallback attempt to get the modal directly
      const directModal = document.getElementById(this.modalId);
      if (directModal) {
        console.log('Found modal through direct DOM access', directModal);
        this.modal = directModal;
      } else {
        console.error('Modal not found even with direct access');
        return;
      }
    }
    
    // Remove the 'hidden' class to show the modal
    this.modal.classList.remove('hidden');
    console.log(`Modal ${this.modalId} opened`);
  }
  
  hideModal() {
    console.log(`Hiding modal ${this.modalId}`);
    if (this.modal) {
      this.modal.classList.add('hidden');
    }
  }
  
  updateModalFromTrigger(triggerElement) {
    console.log('Updating modal content from trigger:', triggerElement);
    
    if (!triggerElement) {
      console.error('No trigger element provided to updateModalFromTrigger');
      return;
    }
    
    // Get data attributes from the trigger
    this.actionUrl = triggerElement.dataset.action || '';
    this.redirectUrl = triggerElement.dataset.redirect || '';
    this.documentId = triggerElement.dataset.documentId || '';
    this.documentType = triggerElement.dataset.documentType || '';
    
    // Update modal content
    const title = triggerElement.dataset.title || 'Confirm Action';
    const message = triggerElement.dataset.message || 'Are you sure you want to proceed?';
    
    console.log('Setting modal content:', { 
      title, 
      message, 
      actionUrl: this.actionUrl,
      documentId: this.documentId
    });
    
    if (this.titleElement) this.titleElement.textContent = title;
    if (this.messageElement) this.messageElement.textContent = message;
    
    // Update modal data attributes (for backward compatibility)
    this.modal.dataset.action = this.actionUrl;
    this.modal.dataset.redirect = this.redirectUrl;
  }
  
  handleConfirmAction() {
    // Use the action URL from object property
    const url = this.actionUrl;
    
    if (!url) {
      console.error('No action URL specified for modal');
      this.hideModal();
      return;
    }
    
    console.log(`Making request to: ${url} with documentId: ${this.documentId || 'none'}`);
    
    // Detect special endpoints
    const isHistoryDeletion = url.includes('delete_all_history');
    const isDocumentDeletion = url.includes('delete_document');
    
    // Determine if we should use POST method - more specific checks for special endpoints
    const usePost = this.modal.dataset.method === 'post' || 
                   isHistoryDeletion || 
                   isDocumentDeletion;
                   
    console.log(`Request will use ${usePost ? 'POST' : 'GET'} method`);
    
    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    if (usePost && !csrfToken) {
      console.warn('CSRF token not found, but attempting POST request anyway');
    }
    
    // Prepare fetch options
    const fetchOptions = {
      method: usePost ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    // Add CSRF token for POST requests
    if (usePost && csrfToken) {
      fetchOptions.headers['X-CSRFToken'] = csrfToken;
    }
    
    console.log('Fetch options:', fetchOptions);
    
    fetch(url, fetchOptions)
      .then(response => {
        if (!response.ok) {
          console.error(`Server returned status: ${response.status}`);
          return response.text().then(text => {
            try {
              // Try to parse as JSON first
              return JSON.parse(text);
            } catch (e) {
              // If not JSON, return as text in result object
              return { status: 'error', message: text };
            }
          });
        }
        
        // Try to parse as JSON
        return response.text().then(text => {
          try {
            const data = JSON.parse(text);
            
            // Normalize the status field for consistency - if it has a status field of 'success', convert to 'ok' for compatibility
            if (data.status === 'success') {
              console.log('Normalizing response status from "success" to "ok" for compatibility');
              data.originalStatus = data.status; // Save original status
              data.status = 'ok';
            }
            
            return data;
          } catch (e) {
            // If response is not JSON, create a success object
            return { status: 'ok', message: text };
          }
        });
      })
      .then(result => {
        console.log('Response:', result);
        
        if (result.status === 'ok' || result.status === 'success') {
          // Handle document/element removal if document ID is provided
          if (this.documentId) {
            const element = document.getElementById(this.documentId);
            if (element) {
              console.log(`Removing element with ID: ${this.documentId}`);
              element.remove();
              
              // Show success notification
              this.showNotification('Document deleted successfully', 'success');
            }
          } else if (isHistoryDeletion) {
            // Special handling for history deletion
            this.showNotification('History deleted successfully', 'success');
            
            // Check if we're on a history page
            const currentPath = window.location.pathname;
            const isHistoryPage = currentPath.includes('/d/history') || 
                                 currentPath.includes('/list/history') ||
                                 currentPath.includes('/chat/history');
                                 
            if (isHistoryPage) {
              console.log('On history page, redirecting to index');
              window.location.href = '/';
              return; // Stop further processing
            } else {
              // Just update the navigation items
              console.log('Not on history page, updating navigation items');
              if (typeof updateNavItems === 'function') {
                setTimeout(updateNavItems, 500);
              }
            }
          }
          
          // Handle redirect if URL provided
          if (this.redirectUrl) {
            console.log(`Redirecting to: ${this.redirectUrl}`);
            window.location.href = this.redirectUrl;
          }
          
          // Trigger success event
          const event = new CustomEvent('confirmAction:success', { 
            detail: { 
              modalId: this.modalId, 
              result, 
              documentType: this.documentType,
              action: isHistoryDeletion ? 'delete_all_history' : url.split('?')[0].split('/').pop() // Extract action name from URL
            } 
          });
          document.dispatchEvent(event);
        } else {
          // Check if this might actually be a success response with a different status key
          if (result.status && (result.status.toLowerCase().includes('success') || result.status.toLowerCase() === 'ok')) {
            console.log('Response has a success-like status but not matching our expected format. Treating as success:', result);
            
            // Show success notification with the message from the response
            this.showNotification(result.message || 'Action completed successfully', 'success');
            
            // Trigger success event for compatibility
            const event = new CustomEvent('confirmAction:success', { 
              detail: { 
                modalId: this.modalId, 
                result, 
                documentType: this.documentType,
                action: isHistoryDeletion ? 'delete_all_history' : url.split('?')[0].split('/').pop()
              } 
            });
            document.dispatchEvent(event);
          } else {
            console.error('Action failed:', result);
            
            // Show error notification
            this.showNotification('Error: ' + (result.message || 'Action failed'), 'error');
            
            // Trigger error event
            const event = new CustomEvent('confirmAction:error', { 
              detail: { modalId: this.modalId, result } 
            });
            document.dispatchEvent(event);
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        this.showNotification('Error processing request: ' + error.message, 'error');
      })
      .finally(() => {
        this.hideModal();
      });
  }
  
  showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 px-6 py-3 rounded shadow-lg z-50 ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    
    // Add to body and remove after delay
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
  }
}

// Initialize the global confirm modal when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing modals');
  
  // Function to initialize modal triggers
  function initializeModalSystem() {
    // Find all confirm modals
    const modals = document.querySelectorAll('[id$="_modal"]');
    console.log(`Found ${modals.length} modals`);
    
    // Store modal instances in a global object for reference
    window.modalInstances = window.modalInstances || {};
    
    // Initialize each modal
    modals.forEach(modal => {
      if (!window.modalInstances[modal.id]) {
        console.log(`Creating ConfirmModal for ${modal.id}`);
        window.modalInstances[modal.id] = new ConfirmModal(modal.id);
      }
    });
    
    // Log all modal triggers for debugging
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    console.log(`Found ${modalTriggers.length} modal triggers at initialization time`);
    
    // Log all modal triggers and their attributes for debugging
    modalTriggers.forEach((trigger, index) => {
      console.log(`Trigger #${index}:`, {
        element: trigger.tagName,
        class: trigger.className,
        modalTarget: trigger.dataset.modalTarget,
        action: trigger.dataset.action || 'no action',
        parentClass: trigger.parentElement ? trigger.parentElement.className : 'no parent',
        isVisible: trigger.offsetParent !== null, // Will be null if element is hidden
        text: trigger.innerText.trim().substring(0, 20) + (trigger.innerText.length > 20 ? '...' : '')
      });
    });
  }
  
  // Initial initialization
  initializeModalSystem();
  
  // Re-check after a short delay to catch any dynamically added elements
  setTimeout(initializeModalSystem, 500);
  
  // Use event delegation instead of directly attaching to each button
  // This will catch clicks on buttons even if they're dynamically added or in collapsed sections
  document.addEventListener('click', function(event) {
    // Check if the clicked element or any of its parents has the data-modal-target attribute
    let targetElement = event.target;
    
    // Navigate up to 5 levels up to find a button or link with data-modal-target
    for (let i = 0; i < 5; i++) {
      if (!targetElement) break;
      
      if (targetElement.hasAttribute && targetElement.hasAttribute('data-modal-target')) {
        // We found a modal trigger
        event.preventDefault();
        event.stopPropagation(); // Stop event bubbling to parent elements
        
        const modalId = targetElement.dataset.modalTarget;
        console.log(`Modal trigger clicked (via delegation) for: ${modalId}`, {
          element: targetElement.tagName,
          class: targetElement.className,
          action: targetElement.dataset.action || 'no action',
          text: (targetElement.innerText || '').trim().substring(0, 20) + 
                ((targetElement.innerText || '').length > 20 ? '...' : '')
        });
        
        // Special handling for delete_all_history
        const isHistoryDelete = targetElement.dataset.action && 
                               targetElement.dataset.action.includes('delete_all_history');
        
        if (isHistoryDelete) {
          console.log('Special handling for delete all history button');
        }
        
        // Check if the modal instance exists, if not try to create it
        if (!window.modalInstances || !window.modalInstances[modalId]) {
          console.log(`Modal instance for ${modalId} not found, trying to create it now`);
          const modal = document.getElementById(modalId);
          if (modal) {
            window.modalInstances = window.modalInstances || {};
            window.modalInstances[modalId] = new ConfirmModal(modalId);
          }
        }
        
        const modalInstance = window.modalInstances && window.modalInstances[modalId];
        if (modalInstance) {
          console.log(`Modal instance found for ${modalId}, showing modal`);
          
          // Make sure we update the modal from the button's data attributes
          modalInstance.updateModalFromTrigger(targetElement);
          modalInstance.showModal();
        } else {
          console.error(`Modal instance for ID ${modalId} not found`);
          // Try direct DOM access as fallback
          const modal = document.getElementById(modalId);
          if (modal) {
            console.log(`Modal element found by ID, showing directly`);
            
            // Get attributes from the clicked element
            const title = targetElement.dataset.title || 'Confirm Action';
            const message = targetElement.dataset.message || 'Are you sure?';
            const actionUrl = targetElement.dataset.action || '';
            
            // Apply them directly to the modal
            const titleEl = modal.querySelector('h3');
            const messageEl = modal.querySelector('p');
            
            if (titleEl) titleEl.textContent = title;
            if (messageEl) messageEl.textContent = message;
            
            // Set the action URL on the modal for the confirm button
            modal.dataset.action = actionUrl;
            
            // Make delete operations use POST method
            if (actionUrl && (actionUrl.includes('delete') || actionUrl.includes('remove'))) {
              modal.dataset.method = 'post';
            }
            
            modal.classList.remove('hidden');
          } else {
            console.error(`Modal with ID ${modalId} not found in DOM`);
          }
        }
        
        break; // Found and handled the modal trigger, stop looking
      }
      
      // Move up the DOM tree
      targetElement = targetElement.parentElement;
    }
  });
}); 