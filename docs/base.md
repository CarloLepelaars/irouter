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

## detect_content_type

Detect if content is text, image URL, or local image:

```python
from irouter.base import detect_content_type

# Image URL detection
detect_content_type("https://example.com/image.jpg")  # "image_url"

# Local image detection  
detect_content_type("./photo.png")  # "local_image" (if file exists)

# Text detection
detect_content_type("Hello world")  # "text"
```

## encode_base64

Encode local images to base64 for API requests:

```python
from irouter.base import encode_base64

# Convert image to base64
base64_data = encode_base64("path/to/image.jpg")
print(base64_data[:50])  # First 50 characters of base64 string
```