# Changelog

## [2023-12-24] Security and Session Management Improvements

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