// Generic confirmation modal handler
class ConfirmModal {
  constructor(modalId) {
    this.modal = document.getElementById(modalId);
    if (!this.modal) {
      console.error(`Modal with ID ${modalId} not found`);
      return;
    }
    
    console.log(`Initializing modal: ${modalId}`);
    
    this.modalContent = this.modal.querySelector('.modal-content');
    this.confirmButton = this.modal.querySelector('button.confirm-action');
    this.cancelButton = this.modal.querySelector('button.cancel-action');
    this.closeButton = this.modal.querySelector('button.close-modal');
    
    // Elements for dynamic content
    this.titleElement = this.modal.querySelector('h3');
    this.messageElement = this.modal.querySelector('p');
    
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
    // Close modal when clicking cancel or close buttons
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
  }

  showModal(triggerElement) {
    console.log('Showing modal');
    
    // Update modal content based on trigger element's data attributes
    if (triggerElement) {
      this.updateModalFromTrigger(triggerElement);
    }
    
    this.modal.classList.remove('hidden');
  }

  hideModal() {
    console.log('Hiding modal');
    this.modal.classList.add('hidden');
  }
  
  updateModalFromTrigger(triggerElement) {
    // Get data attributes from trigger element
    this.actionUrl = triggerElement.dataset.action || '';
    this.redirectUrl = triggerElement.dataset.redirect || '';
    this.documentId = triggerElement.dataset.documentId || '';
    this.documentType = triggerElement.dataset.documentType || '';
    
    // Update modal content
    if (this.titleElement && triggerElement.dataset.title) {
      this.titleElement.textContent = triggerElement.dataset.title;
    }
    
    if (this.messageElement && triggerElement.dataset.message) {
      this.messageElement.textContent = triggerElement.dataset.message;
    }
    
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
    
    console.log(`Making request to: ${url}`);
    
    // Determine if we should use POST method
    const usePost = this.modal.dataset.method === 'post' || url.includes('delete_all_history');
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    
    // Prepare fetch options
    const fetchOptions = {
      method: usePost ? 'POST' : 'GET',
      headers: {}
    };
    
    // Add CSRF token for POST requests
    if (usePost && csrfToken) {
      fetchOptions.headers['X-CSRFToken'] = csrfToken;
    }
    
    fetch(url, fetchOptions)
      .then(response => response.json())
      .then(result => {
        console.log('Response:', result);
        if (result.status === 'ok') {
          // Handle document/element removal if document ID is provided
          if (this.documentId) {
            const element = document.getElementById(this.documentId);
            if (element) {
              console.log(`Removing element with ID: ${this.documentId}`);
              element.remove();
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
              action: url.split('?')[0].split('/').pop() // Extract action name from URL
            } 
          });
          document.dispatchEvent(event);
        } else {
          console.error('Action failed:', result);
          // Trigger error event
          const event = new CustomEvent('confirmAction:error', { 
            detail: { modalId: this.modalId, result } 
          });
          document.dispatchEvent(event);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      })
      .finally(() => {
        this.hideModal();
      });
  }
}

// Initialize the global confirm modal when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing modals');
  
  // Find all confirm modals
  const modals = document.querySelectorAll('[id$="_modal"]');
  console.log(`Found ${modals.length} modals`);
  
  // Store modal instances in a global object for reference
  window.modalInstances = {};
  
  // Initialize each modal
  modals.forEach(modal => {
    console.log(`Creating ConfirmModal for ${modal.id}`);
    window.modalInstances[modal.id] = new ConfirmModal(modal.id);
  });
  
  // Add trigger handlers for buttons that should open modals
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  console.log(`Found ${modalTriggers.length} modal triggers`);
  
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', function(event) {
      event.preventDefault();
      const modalId = this.dataset.modalTarget;
      console.log(`Trigger clicked for modal: ${modalId}`);
      
      const modalInstance = window.modalInstances[modalId];
      if (modalInstance) {
        modalInstance.showModal(this);
      } else {
        console.error(`Modal instance for ID ${modalId} not found`);
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.classList.remove('hidden');
        } else {
          console.error(`Modal with ID ${modalId} not found`);
        }
      }
    });
  });
}); 