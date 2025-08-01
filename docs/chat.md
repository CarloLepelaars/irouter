# Chat

Conversational LLM interactions with history and token usage tracking.

## Quick Start

```python
from irouter import Chat
from dotenv import load_dotenv

load_dotenv()  # Load OPENROUTER_API_KEY from .env

# Single model with system prompt
c = Chat("moonshotai/kimi-k2:free", system="You are the best assistant.")
response = c("Who created you?")
print(c.history)  # View conversation history
print(c.usage)    # View token usage
```

## Single Model Usage

```python
c = Chat("moonshotai/kimi-k2:free", system="You are the best assistant in the world.")
# or with explicit API key
# c = Chat("moonshotai/kimi-k2:free", api_key="your_api_key")

# Initial state
print(c.history)  # [{'role': 'system', 'content': 'You are helpful.'}]
print(c.usage)    # {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

# Make a call
response = c("Who created you?")

# Updated state
print(c.history)  # Full conversation history
print(c.usage)    # Updated token counts
```

## Multiple Models

Track separate conversations with multiple models:

```python
models = ["moonshotai/kimi-k2:free", "z-ai/glm-4.5-air:free"]
c = Chat(models, system="You are the best assistant.")

# Each model has separate history and usage
print(c.history)  # Dict mapping model -> history
print(c.usage)    # Dict mapping model -> usage

responses = c("Who created you?")
# Returns: {"moonshotai/kimi-k2:free": "...", "z-ai/glm-4.5-air:free": "..."}

# Access specific model data
print(c.history["moonshotai/kimi-k2:free"])
print(c.usage["moonshotai/kimi-k2:free"])
```

## Managing State

Reset conversation history:

```python
c.reset_history()  # Revert to system prompt
```

Reset token usage:

```python
c.reset_usage()    # Reset counters to zero
print(c.usage)     # {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
```

## Comparison with Call

- **Call**: One-off requests, no state tracking
- **Chat**: Multi-turn conversations, maintains history and usage statistics

Use `Chat` when you need persistent conversations or want to track token consumption across multiple interactions.