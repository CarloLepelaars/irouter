# Call

Simple one-off LLM calls without history or token tracking.

## Quick Start

```python
from irouter import Call
from dotenv import load_dotenv

load_dotenv()  # Load OPENROUTER_API_KEY from .env

# Single model
c = Call("moonshotai/kimi-k2:free")
response = c("Who played guitar on Steely Dan's Kid Charlemagne?")
print(response)
```

## Single Model Usage

Initialize with a model slug:

```python
c = Call("moonshotai/kimi-k2:free")
# or with explicit API key
c = Call("moonshotai/kimi-k2:free", api_key="your_api_key")

response = c("Your question here")
```

Get raw ChatCompletion object:

```python
raw_response = c("Your question", raw=True)
print(raw_response.usage)  # Token usage info
```

## Multiple Models

Call multiple models simultaneously:

```python
models = ["moonshotai/kimi-k2:free", "google/gemma-3n-e2b-it:free"]
mc = Call(models)

responses = mc("Who played guitar on Kid Charlemagne?")
# Returns: {"moonshotai/kimi-k2:free": "Larry Carlton", "google/gemma-3n-e2b-it:free": "David Spengler"}

# Access specific model response
print(responses["moonshotai/kimi-k2:free"])
```

## Message Format

Pass conversation history as list of messages:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Amsterdam."},
    {"role": "user", "content": "No, why would you say Amsterdam?"}
]

c = Call("moonshotai/kimi-k2:free")
response = c(messages)
```

**Note:** When using message format, the `system` parameter is ignored. Include system messages in your message list.

## Image Support

Image URLs and local images are supported. Supports `.jpg`, `.jpeg`, `.png` and `.webp` formats.

Pass images with text for vision-capable models:

```python
c = Call("gpt-4o-mini")

# Image URL + text
response = c(["https://example.com/image.jpg", "What's in this image?"])

# Local image + text  
response = c(["./photo.png", "Describe this photo"])
```