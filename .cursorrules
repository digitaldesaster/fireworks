# Cursorrules for Our Python Flask + Tailwind + FlyonUI Project

This document provides clear guidelines and best practices to ensure that any new code is robust, secure, and consistent with our existing codebase. Always refer to this file (and the examples in our repository) when developing or modifying functionality.

---

## 1. Tech Stack Overview

### Backend
- **Python 3.x** with Flask for building RESTful routes and modular Blueprints.
- **MongoDB** using MongoEngine for data modeling and persistence.
- **Security:**  
  - Use Flask-Login for authentication.
  - Enforce CSRF protection on all forms and API endpoints.

### Frontend
- **Tailwind CSS** for styling using a utility-first approach.
- **FlyonUI** as our component library for UI elements.
  - **Note:** All examples and usage patterns for FlyonUI components are located in the `flyonui-docs` folder.
  - When developing UI elements, always review these examples before building or modifying components.

---

## 2. Core Development Principles

1. **Code Quality & Maintainability**
   - Follow Python best practices and PEP 8 guidelines.
   - Write modular, well-documented code with clear naming conventions.
   - Include type hints where beneficial.
   - Implement unit and integration tests for all new functionality.

2. **Security First**
   - Store all sensitive data (e.g., API keys, secret keys) in environment variables.
   - Enforce CSRF protection on all forms and API endpoints.
   - Sanitize and validate all user inputs.
   - Manage sessions securely using Flask-Login.

3. **User Experience**
   - Create responsive, accessible UI designs.
   - For UI elements, always refer to the examples in the `flyonui-docs` folder to ensure consistency.
   - Provide clear, meaningful error messages for both users and in logs.

4. **Documentation & Comments**
   - Document complex code logic and update documentation files (e.g., Readme.md, ToDo.md) as changes are made.
   - Use inline comments to explain non-obvious code sections.

---

## 3. Coding Guidelines

### Project Structure & Organization
- **Modularity:**  
  Organize your code into clearly defined modules (e.g., separate folders for core functionality, UI templates, utilities, and blueprints).
- **Database Models:**  
  Follow established patterns in files such as `core/db_document.py` and `core/db_connect.py`.
- **API Routes:**  
  Use Flask Blueprints (e.g., in `ai_chat.py`) for route organization. Render templates for UI pages and return JSON for API endpoints.

### Error Handling
- Use `try/except` blocks to catch and log exceptions.
- Provide fallback behaviors and user notifications on errors.

### Commit Practices
- Write clear and concise commit messages.
- Make small, incremental commits that explain the purpose of the change.

---

## 4. UI Component Guidelines

- **Styling:**  
  Use Tailwind CSS classes consistently for styling.
- **FlyonUI Components:**  
  - Always refer to the examples in the `flyonui-docs` folder when building or modifying UI components.
  - New UI elements should follow the design and behavior patterns found in the folder.
- **Non-UI Elements:**  
  When building or modifying backend or non-UI functionality, always review the existing examples in the repository to maintain consistency.

---

## 5. Testing & Deployment

- **Testing**
  - Write and run tests regularly (both unit and integration) to ensure code stability.
- **Deployment**
  - Use environment-specific configurations.
  - Disable debugging and enable all security features in production.

---

## 6. Best Practices Summary

- **Review:**  
  Always review the entire codebase and existing examples before adding new functionality.
- **Consistency:**  
  New code must integrate seamlessly with existing modules.
- **Reference Materials:**  
  When in doubt, refer to the examples in the repository—especially the `flyonui-docs` folder for UI elements.
- **Security:**  
  Never compromise on security or data validation.
- **Documentation:**  
  Keep documentation and inline comments up to date.

---

By adhering to these guidelines, any AI-generated code or modifications will be secure, maintainable, and aligned with our project’s standards.
