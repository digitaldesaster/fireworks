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

### Supported Models

The system supports multiple AI providers:

- **OpenAI**: GPT-3.5, GPT-4, and O1 models (o1-mini, o1-preview)
- **Anthropic**: Claude models
- **Together AI**: Various open-source models
- **DeepSeek**: DeepSeek language models
- **Perplexity**: Perplexity language models
- **Azure OpenAI**: Microsoft-hosted OpenAI models

#### O1 Model Support

OpenAI O1 models are supported with some limitations:
- **No system message support** - System messages are automatically converted to user messages
- **No streaming support** - Responses are always processed in non-streaming mode
- Content filtering results are captured
- Detailed token usage information is available

Important O1 model limitations:
1. System messages are converted by prepending them to the first user message
2. All requests use non-streaming mode regardless of the `stream` parameter

To use O1 models, configure in model settings:
```python
model = {
    "provider": "openai",
    "model": "o1-mini"  # or other O1 models
}
```

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
- Support for OpenAI's O1 models with detailed token analytics

## Testing

Use the testing scripts to validate model connectivity:
- `ai_test.py`: General API testing
- `test_o1_models.py`: Specific testing for O1 model compatibility
