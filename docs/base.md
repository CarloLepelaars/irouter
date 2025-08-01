# Base Module

Core utilities for the irouter package.

## get_all_models

Get all available models from the Openrouter API:

```python
from irouter.base import get_all_models

# Get model slugs for initializing LLMs
models = get_all_models()
print(models[:3])  # ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', ...]

# Get human-readable model names
names = get_all_models(slug=False)  
print(names[:3])  # ['GPT-4o', 'Claude 3.5 Sonnet', ...]
```

## nb_markdown

Display markdown in Jupyter notebooks:

```python
from irouter.base import nb_markdown

nb_markdown("**Hello** world!")
```

## history_to_markdown

Convert chat history to readable markdown:

```python
from irouter.base import history_to_markdown

# Get markdown string
markdown = history_to_markdown(chat.history)
print(markdown)

# Display directly in Jupyter
history_to_markdown(chat.history, ipython=True)
```