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
    console.log('Modal content:', this.modalContent);
    
    // Use more specific selectors to find the buttons
    this.confirmButton = this.modal.querySelector('button.confirm-action');
    console.log('Confirm button:', this.confirmButton);
    
    this.cancelButton = this.modal.querySelector('button.cancel-action');
    console.log('Cancel button:', this.cancelButton);
    
    this.closeButton = this.modal.querySelector('button.close-modal');
    console.log('Close button:', this.closeButton);
    
    this.actionUrl = this.modal.dataset.action || '';
    this.redirectUrl = this.modal.dataset.redirect || '';
    
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

  showModal() {
    console.log('Showing modal');
    this.modal.classList.remove('hidden');
  }

  hideModal() {
    console.log('Hiding modal');
    this.modal.classList.add('hidden');
  }

  handleConfirmAction() {
    // Default implementation for API calls
    if (this.actionUrl) {
      console.log(`Making request to: ${this.actionUrl}`);
      fetch(this.actionUrl)
        .then(response => response.json())
        .then(result => {
          console.log('Response:', result);
          if (result.status === 'ok') {
            if (this.redirectUrl) {
              console.log(`Redirecting to: ${this.redirectUrl}`);
              window.location.href = this.redirectUrl;
            }
            // Trigger a custom event that specific implementations can listen for
            const event = new CustomEvent('confirmAction:success', { 
              detail: { modalId: this.modal.id, result } 
            });
            document.dispatchEvent(event);
          } else {
            console.error('Action failed:', result);
            // Trigger error event
            const event = new CustomEvent('confirmAction:error', { 
              detail: { modalId: this.modal.id, result } 
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
}

// Initialize all confirm modals on the page
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing modals');
  
  // Find all confirm modals
  const modals = document.querySelectorAll('[id$="_modal"]');
  console.log(`Found ${modals.length} modals`);
  
  // Initialize each modal
  modals.forEach(modal => {
    console.log(`Creating ConfirmModal for ${modal.id}`);
    new ConfirmModal(modal.id);
  });
  
  // Add trigger handlers for buttons that should open modals
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  console.log(`Found ${modalTriggers.length} modal triggers`);
  
  modalTriggers.forEach(button => {
    button.addEventListener('click', function(event) {
      event.preventDefault();
      const modalId = this.dataset.modalTarget;
      console.log(`Trigger clicked for modal: ${modalId}`);
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.remove('hidden');
      } else {
        console.error(`Modal with ID ${modalId} not found`);
      }
    });
  });
  
  // Add file deletion functionality (migrated from delete_document.js)
  document.querySelectorAll('.delete_file').forEach(button => {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      const documentId = this.getAttribute('document_id');
      const fileId = this.id;
      const url = `/delete_document?id=${fileId}&type=files`;
      
      fetch(url)
      .then(response => response.json())
      .then(data => {
          if (data.status=='ok') {
              const fileElement = document.getElementById(documentId);
              if (fileElement) {
                  fileElement.remove();
                  console.log("File removed!")
              }
          } else {
              console.error('Failed to delete document:', data);
          }
      })
      .catch(error => console.error('Error:', error));
    });
  });
}); 