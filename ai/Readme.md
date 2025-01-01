# AI Chat System Documentation

## Prerequisites

- OpenAI API key or Anthropic API key required for operation
- Set your API keys in the `.env` file

## System Architecture

### Backend Components (`/ai`)

- `ai_chat.py`: Main chat blueprint and route handlers
- `ai_llm_helper.py`: LLM integration and response processing
- `ai_insert_models.py`: Database models initialization
- `__init__.py`: Package initialization

### Frontend Components

#### Templates (`/templates/chat/`)

- `chat.html`: Main chat interface layout
- `chat_ui.html`: Chat UI components and structure
- `chat_messages.html`: Message container template
- `chat_messages_rendered.html`: Rendered messages view
- `bot_message_template.html`: AI response formatting
- `user_message_template.html`: User message formatting
- `code_block_template.html`: Code snippet display
- `chat_prompts.html`: System prompts management

#### JavaScript (`/static/chat/`)

- `chat_core.js`: Core chat functionality, HTMX interactions, and UI handlers

## Database Integration

- Chat models and schemas defined in `core/db_document.py`
- Stores message history, prompts, and system configurations

## Setup Instructions

1. Configure your environment variables in `.env`
2. Import the chat blueprint in `app.py`:
   ```python
   from ai.ai_chat import dms_chat
   app.register_blueprint(dms_chat, url_prefix='/chat')
   ```

## Features

- Real-time chat interface with AI models
- Code snippet highlighting and formatting
- Message history persistence
- Custom prompt management
- HTMX-powered dynamic updates
