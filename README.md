# irouter

![PyPI version](https://img.shields.io/pypi/v/irouter)
![PyPI Downloads](https://static.pepy.tech/badge/irouter)
![Python Version](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/carlolepelaars/irouter/master/pyproject.toml&query=%24.project%5B%22requires-python%22%5D&label=python&color=blue) 
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

`irouter` provides a simple interface to access 100s of LLMs with minimal lines of code.

## Installation

1. Install `irouter` from PyPI:

```bash
pip install irouter
```

2. Create an account on [OpenRouter](https://openrouter.ai) and generate an API key.

3a. (recommended!) Set the OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY=your_openrouter_api_key
```

In this way you can use `irouter` objects like `Call` and `Chat` without having to pass an API key.

```python
from irouter import Call
c = Call("moonshotai/kimi-k2:free")
c("How are you?")
```

3b. Alternatively, pass `api_key` to `irouter` objects like `Call` and `Chat`.

```python
from irouter import Call
c = Call("moonshotai/kimi-k2:free", api_key="your_openrouter_api_key")
c("How are you?")
```

## Usage

Below are basic usage examples of functionality in `irouter`. For more detailed examples, check out the `nbs` folder.

### Call

`Call` is the simplest interface to have one-off interactions with one or more LLMs (without tool support).

For conversational interactions use `Chat`, which tracks message history, token usage, and supports tool calling.

#### Single LLM
```python
from irouter import Call
c = Call("moonshotai/kimi-k2:free")
c("Who are you?")
# "I'm Kimi, your AI friend from Moonshot AI. I'm here to chat, answer your questions, and help you out whenever you need it."
```

#### Multiple LLMs
```python
from irouter import Call
c = Call(["moonshotai/kimi-k2:free", "google/gemini-2.0-flash-exp:free"])
c("Who are you?")
# {'moonshotai/kimi-k2:free': "I'm Kimi, your AI friend from Moonshot AI. I'm here to chat, answer your questions, and help you out whenever you need it.",
#  'google/gemini-2.0-flash-exp:free': 'I am a large language model, trained by Google.\n'}
```

### Chat

`Chat` is an easy way to interface with one or more LLMs, while tracking message history, token usage, and supporting tool calling.

#### Single LLM

```python
from irouter import Chat
c = Chat("moonshotai/kimi-k2:free")
c("Who are you?")
print(c.history) # {'moonshotai/kimi-k2:free': [...]}
print(c.usage) # {'moonshotai/kimi-k2:free': {'prompt_tokens': 8, 'completion_tokens': 8, 'total_tokens': 16}}
```

#### Multiple LLMs

```python
from irouter import Chat
c = Chat(["moonshotai/kimi-k2:free", "google/gemini-2.0-flash-exp:free"])
c("Who are you?")
print(c.history) 
# {'moonshotai/kimi-k2:free': [...], 
# 'google/gemini-2.0-flash-exp:free': [...]}
print(c.usage) 
# {'moonshotai/kimi-k2:free': {'prompt_tokens': 8, 'completion_tokens': 8, 'total_tokens': 16}, 
# 'google/gemini-2.0-flash-exp:free': {'prompt_tokens': 8, 'completion_tokens': 10, 'total_tokens': 18}}
```

### Image

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

### PDF

Both `Call` and `Chat` support PDF processing from URLs or local files.

```python
from irouter import Call
c = Call("moonshotai/kimi-k2:free")
c(["https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf", 
   "What is the main contribution of this paper?"])
# 'The main contribution of this paper is the introduction of the Transformer architecture...'
```

### Audio

Some LLMs have native audio support. Simply pass a local filepath that points to a `.mp3` or `.wav` file with an instruction as a list of strings.

```python
from irouter import Call
c = Call("google/gemini-2.5-flash")
c(["../assets/bottles.mp3", "What do you hear?"])
# 'I hear the sound of a glass bottle being opened and closed...'
```

### Multiple Modalities

Combine text, images, PDFs, and audio in a single request. Simply pass a list of strings containing URLs, filepaths and/or text.

```python
from irouter import Call
c = Call("google/gemini-2.5-flash")
c(["../assets/bottles.mp3", "../assets/puppy.jpg", "What do you hear and see?"])
# 'I hear sounds of glass and see a small, fluffy dog...'
```

### Tool Usage

`Chat` supports (multi-turn) tool calling, allowing LLMs to execute functions you provide. Simply pass a list of functions as the `tools` parameter. `irouter` will take care of the rest.

To ensure the best tool usage experience:

- Use the [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) convention for function docstrings with `:param` tags, like the function below. In that case the tool schema will specifically include descriptions for each parameter.

- Consider using type hints so the LLM knows what types to provide.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

def get_time(fmt: str="%Y-%m-%d %H:%M:%S", tz: str=None) -> str:
    """Returns the current time formatted as a string.

    :param fmt: Format string for strftime.
    :param tz: Optional timezone name (e.g., "UTC"). If given, uses that timezone.
    :returns: The formatted current time.
    """
    return datetime.now(ZoneInfo(tz)) if tz else datetime.now().strftime(fmt)

chat = Chat("gpt-4o-mini")
result = chat("What is the current time in New York City?", tools=[get_time])
# "'The current time in New York City is 7:45 AM on August 5, 2025.\n'"
```

### Misc

#### `get_all_models`

You can easily get an overview of all 300+ models available using `get_all_models`.

Alternatively, browse [OpenRouter's models page](https://openrouter.ai/models) to view supported models on `irouter`.

```python
from irouter.base import get_all_models
get_all_models()
# ['llm_provider1/model1', ... 'llm_providerx/modelx']
```

## Credits

This project is built on top of the [OpenRouter](https://openrouter.ai) API infrastructure, which provides access to LLMs through a unified interface.

This project is inspired by [Answer.AI's](https://www.answer.ai) projects like [cosette](https://github.com/AnswerDotAI/cosette) and [claudette](https://github.com/AnswerDotAI/claudette).

`irouter` generalizes this idea to support 100s of LLMs, which includes OpenAI, Anthropic and more. `irouter` also provides additional modalities and functionality to work with. This is possible thanks to [OpenRouter's](https://openrouter.ai) infrastructure.
