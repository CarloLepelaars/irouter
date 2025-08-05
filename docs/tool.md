# Tool Usage

`Chat` supports tool calling, allowing LLMs to execute functions you provide. Simply pass a list of functions as the `tools` parameter. 

To ensure the best tool usage experience, use the reStructuredText convention for function docstrings with `:param` tags, like the function below.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

def get_time(fmt="%Y-%m-%d %H:%M:%S", tz=None):
    """Returns the current time formatted as a string.

    :param fmt: Format string for strftime.
    :param tz: Optional timezone name (e.g., "UTC"). If given, uses that timezone.
    :returns: The formatted current time.
    """
    dt = datetime.now(ZoneInfo(tz)) if tz else datetime.now()
    return dt.strftime(fmt)

chat = Chat("gpt-4o-mini")
result = chat("What is the current time in New York City?", tools=[get_time])
# "'The current time in New York City is 7:45 AM on August 5, 2025.\n'"
```

NOTE: `Call` does not support tool calling as it does not track message history. Use `Chat` if you need tool calling.