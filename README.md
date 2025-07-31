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
