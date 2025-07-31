# irouter
Access 100's of (free) LLMs with only a few lines of code

# Installation

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

## Credits

This project is built on top of [OpenRouter.ai's](https://openrouter.ai) API infrastructure, which provides access to LLMs through a unified interface.

This project is inspired by [Answer.AI's](https://www.answer.ai) projects:
- [cosette](https://github.com/AnswerDotAI/cosette) - Lightweight LLM wrapper for OpenAI's API
- [claudette](https://github.com/AnswerDotAI/claudette) - Lightweight LLM wrapper for Anthropic's API

`irouter` generalizes this idea to support 100s of LLMs, which includes OpenAI and Anthropic models, thanks to OpenRouter's infrastructure.
