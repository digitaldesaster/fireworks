# Changelog

## [2024-01-25] UI Overhaul and Package Management Updates

### UI Improvements

- Implemented new sidebar navigation layout for better organization
- Enhanced responsive design with proper lg: breakpoints
- Added sticky columns to tables for better usability
- Improved chat UI positioning and layout
- Updated dropdown menus and button styles
- Added new icon system using Tabler icons
- Enhanced navigation structure with better hierarchy

### Template Updates

- Modified collection templates for better layout consistency
- Updated document form templates with improved spacing
- Enhanced chat interface with better positioning
- Improved index page layout with centered content
- Completely redesigned navigation template with sidebar

### Package Management

- Replaced `requirement.txt` with standardized `requirements.txt`
- Removed deprecated `install.py`
- Updated package.json dependencies

### CSS Updates

- Updated output.css with new utility classes
- Enhanced responsive design utilities
- Added new component styles for sidebar
- Improved table styling with sticky columns

### Database

- Modified db_document.py with schema improvements

## [2024-12-28] Security and Session Management Improvements

### Security Enhancements

- Moved secret key to environment variables
- Added CSRF protection to all forms (login, register, logout)
- Enabled strong session protection in Flask-Login
- Configured secure cookie settings (HTTPOnly, duration)

### Session Management

- Removed conflicting session management in `before_request`
- Implemented proper "Remember me" functionality
  - Without checkbox: Session ends on browser close
  - With checkbox: Session persists for 30 days
- Added proper session cleanup on logout

### Authentication Flow

- Enhanced login form with proper autocomplete attributes
- Improved error messages in registration form
- Added specific error messages for registration failures:
  - Email already exists
  - Password too short
  - Missing required fields

### Error Handling Improvements

- Added comprehensive logging system with proper levels
- Implemented specific error types and handling:
  - ValidationError for invalid data validation
  - NotUniqueError for duplicate email handling
  - OperationError for database issues
  - Generic Exception as fallback with logging
- Enhanced User model with required fields and constraints:
  - Made email field unique
  - Added required=True to essential fields
  - Set default role for new users
- Improved error messages for better debugging:
  - Added detailed logging with user context
  - More descriptive user-facing messages
  - Consistent error response format

### Configuration Changes

#### In `app.py`

- Added Flask-Login initialization with secure settings
- Configured session lifetimes and cookie security
- Removed permanent session forcing
- Added CSRF protection initialization

#### In `auth.py`

- Updated login handler to support remember me functionality
- Enhanced logout to properly clear sessions
- Improved error message handling in registration

#### In Templates

- Added CSRF tokens to all forms
- Enhanced form validation and error displays
- Added proper autocomplete attributes for better UX

### Security Notes

- `REMEMBER_COOKIE_SECURE` is set to False for local development
- Should be set to True in production with HTTPS
- Session duration set to 30 days for remembered sessions
