# irouter

![PyPI version](https://img.shields.io/pypi/v/irouter)
![PyPI downloads](https://img.shields.io/pypi/dm/irouter)
![Python Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/carlolepelaars/irouter/master/pyproject.toml&query=%24.project%5B%22requires-python%22%5D&label=python&color=blue) 
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


Access 100s of LLMs with 2 lines of code.

## Installation

1. Install `irouter` from PyPI:

```bash
pip install irouter
```

2. Create an account on [OpenRouter](https://openrouter.ai) and generate an API key.

3a. (recommended!) Set the OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY=your_api_key
```

In this way you can use `irouter` objects like `Call` and `Chat` without have to pass an API key.

```python
from irouter import Call
c = Call(model="moonshotai/kimi-k2:free")
```

3b. Alternatively, pass `api_key` to `irouter` objects like `Call` and `Chat`.

```python
from irouter import Call
c = Call(model="moonshotai/kimi-k2:free", api_key="your_api_key")
```

## Usage

### Call

`Call` is the simplest interface to call one or more LLMs.

#### Single LLM
```python
from irouter import Call
c = Call(model="moonshotai/kimi-k2:free")
c("Who are you?")
# "I'm Kimi, your AI friend from Moonshot AI. I'm here to chat, answer your questions, and help you out whenever you need it."
```

#### Multiple LLMs
```python
from irouter import Call
c = Call(model=["moonshotai/kimi-k2:free", "google/gemini-2.0-flash-exp:free"])
c("Who are you?")
# {'moonshotai/kimi-k2:free': "I'm Kimi, your AI friend from Moonshot AI. I'm here to chat, answer your questions, and help you out whenever you need it.",
#  'google/gemini-2.0-flash-exp:free': 'I am a large language model, trained by Google.\n'}
```

### Chat

`Chat` is an easy way to interface with one or more LLMs, while tracking message history and token usage.

#### Single LLM

```python
from irouter import Chat
c = Chat(model="moonshotai/kimi-k2:free")
c("Who are you?")
print(c.history) # {'moonshotai/kimi-k2:free': [...]}
print(c.usage) # {'moonshotai/kimi-k2:free': {'prompt_tokens': 8, 'completion_tokens': 8, 'total_tokens': 16}}
```

#### Multiple LLMs

```python
from irouter import Chat
c = Chat(model=["moonshotai/kimi-k2:free", "google/gemini-2.0-flash-exp:free"])
c("Who are you?")
print(c.history) 
# {'moonshotai/kimi-k2:free': [...], 
# 'google/gemini-2.0-flash-exp:free': [...]}
print(c.usage) 
# {'moonshotai/kimi-k2:free': {'prompt_tokens': 8, 'completion_tokens': 8, 'total_tokens': 16}, 
# 'google/gemini-2.0-flash-exp:free': {'prompt_tokens': 8, 'completion_tokens': 10, 'total_tokens': 18}}
```

### Image Support

Both `Call` and `Chat` support images from image URLs or local images.

Adding images is as simple as providing a list of strings with:
- text and/or
- image URL(s) and/or
- image path(s)

Make sure to select an LLM that supports image input, like `gpt-4o-mini`.

<img src="https://www.petlandflorida.com/wp-content/uploads/2022/04/shutterstock_1290320698-1-scaled.jpg" alt="Example image" width="300">

```python
from irouter import Chat
ic = Chat("gpt-4o-mini")
# Image URL
ic(["https://www.petlandflorida.com/wp-content/uploads/2022/04/shutterstock_1290320698-1-scaled.jpg", 
    "What is in the image?"])
# or local image
# ic(["../assets/puppy.jpg", "What is in the image?"])
# Example output:
# The image shows a cute puppy, ..., The background is blurred, 
# with green hues suggesting an outdoors setting.

# Images are tracked in history
print(ic.history)
# [{'role': 'system', 'content': 'You are a helpful assistant.'}, 
#  {'role': 'user', 'content': [{'type': 'image_url', 'image_url':
#  {'url': '...'}}, {'type': 'text', 'text': 'What is in the image?'}]}, 
#  {'role': 'assistant', 'content': 'The image shows a cute puppy...'}]
```

For more information on `Chat`, check out the `chat.ipynb` notebook in the `nbs` folder.

### Misc

#### `get_all_models`

You can easily get all 300+ models available with `irouter` using `get_all_models`.

```python
from irouter.base import get_all_models
get_all_models()
# ['llm_provider1/model1', ... 'llm_providerx/modelx']
```

#### `history_to_markdown`

Convert chat history to markdown for easy display in Jupyter notebooks.

```python
from irouter.base import history_to_markdown
history_to_markdown(c.history, ipython=True)
```

## Credits

This project is built on top of the [OpenRouter](https://openrouter.ai) API infrastructure, which provides access to LLMs through a unified interface.

This project is inspired by [Answer.AI's](https://www.answer.ai) projects like [cosette](https://github.com/AnswerDotAI/cosette) and [claudette](https://github.com/AnswerDotAI/claudette).

`irouter` generalizes this idea to support 100s of LLMs, which includes OpenAI and Anthropic models and more, thanks to [OpenRouter's](https://openrouter.ai) infrastructure.
