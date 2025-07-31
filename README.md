# irouter
Access 100's of (free) LLMs with only a few lines of code

## Installation

1.Install `irouter` from PyPI:

```bash
pip install irouter
```

2. Create an account and generate an API key on [OpenRouter](https://openrouter.ai/settings/keys).

3a. Set the API key as an environment variable (recommended):

```bash
export OPENROUTER_API_KEY=your_api_key
```

3b. Pass `api_key` to `irouter` objects like `Call` and `Chat`.

```python
from irouter import Call
call = Call(model="moonshotai/kimi-k2:free", api_key="your_api_key")
```

## Usage

### Call

`Call` is the simplest interface to call one or more LLMs. To track message history and token usage, use `Chat`. 

#### Single LLM
```python
from irouter import Call
c = Call(model="moonshotai/kimi-k2:free")
c ("Who are you?")
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

For more information on `Call`, check out the `call.ipynb` notebook in the `nbs` folder.

### Chat

`Chat` is an easy way to interface with one or more LLMs, while tracking message history and token usage.

### Single LLM

```python
from irouter import Chat
c = Chat(model="moonshotai/kimi-k2:free")
c("Who are you?")
print(c.history)
print(c.usage)
```

### Multiple LLMs

```python
from irouter import Chat
c = Chat(model=["moonshotai/kimi-k2:free", "google/gemini-2.0-flash-exp:free"])
c("Who are you?")
print(c.history)
print(c.usage)
```

For more information on `Chat`, check out the `chat.ipynb` notebook in the `nbs` folder.

### Misc

#### `get_all_models`

You can easily see all 300+ models available with `irouter` through OpenRouter.ai using `get_all_models`.

```python
from irouter.base import get_all_models
get_all_models()
```

## Credits

This project is built on top of [OpenRouter.ai's](https://openrouter.ai) API infrastructure, which provides access to LLMs through a unified interface.

This project is inspired by [Answer.AI's](https://www.answer.ai) projects:
- [cosette](https://github.com/AnswerDotAI/cosette) - Lightweight LLM wrapper for OpenAI's API
- [claudette](https://github.com/AnswerDotAI/claudette) - Lightweight LLM wrapper for Anthropic's API

`irouter` generalizes this idea to support 100s of LLMs, which includes OpenAI and Anthropic models, thanks to OpenRouter's infrastructure.
