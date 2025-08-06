# Tool Usage

`Chat` supports (multi-turn) tool calling, allowing LLMs to execute functions you provide. Simply pass a list of functions as the `tools` parameter. 

To ensure the best tool usage experience:

- Use the [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) convention for function docstrings with `:param` tags, like the function below. In that case the tool schema will specifically include descriptions for each parameter.

- Consider using type hints so the LLM knows what types to provide.

## Basic Tool Usage

This example shows how to use a tool to get the current time.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

def get_time(fmt: str="%Y-%m-%d %H:%M:%S", tz: str=None) -> str:
    """Returns the current time formatted as a string.

    :param fmt: Format string for strftime.
    :param tz: Optional timezone name (e.g., "UTC"). If given, uses that timezone.
    :returns: The formatted current time.
    """
    dt = datetime.now(ZoneInfo(tz)) if tz else datetime.now()
    return dt.strftime(fmt)

c = Chat("gpt-4o-mini")
result = c("What is the current time in New York City?", tools=[get_time])
# "The current time in New York City is 7:45 AM on August 5, 2025."
```

## Multi-Step Tool Usage

The LLM can call multiple tools in sequence without any additional code adjustments. Just pass a list of functions as the `tools` parameter.

The example below will run multiple tool calls because it needs to get weather and distance information for each city. Since each tool can have multiple tool calls, the expectation is the LLM will run 3 tool loops:

1. Get weather for Paris and distance from Paris to London.

2. Get weather for London and distance from London to Tokyo.

3. Get weather for Tokyo.

Use `max_steps` to control the maximum number of tool iterations (default: 100).

```python
def get_weather(city: str) -> str:
    """Get weather for a city (simulated).

    :param city: City name
    :returns: Weather description
    """
    weather_db = {
        "paris": "Sunny, 22°C",
        "london": "Cloudy, 15°C",
        "tokyo": "Rainy, 18°C",
    }
    return weather_db.get(city.lower(), "Weather data not available")


def calculate_distance(city1: str, city2: str) -> str:
    """Calculate distance between cities (simulated).

    :param city1: First city
    :param city2: Second city
    :returns: Distance in km
    """
    distances = {
        ("paris", "london"): 344,
        ("london", "paris"): 344,
        ("paris", "tokyo"): 9715,
        ("tokyo", "paris"): 9715,
    }
    key = (city1.lower(), city2.lower())
    return distances.get(key, "Distance not available")

c = Chat("gpt-4o-mini")
c(
    "I'm planning a trip from Paris to London, then to Tokyo. What's the weather like in each city and what are the distances?",
    tools=[get_weather, calculate_distance],
    max_steps=10,
)
# "Here's the information for your trip:\n\n**Weather:**\n- 
# **Paris:** Sunny, 22°C\n- **London:** Cloudy, 15°C\n- 
# **Tokyo:** Rainy, 18°C\n\n**Distances:**\n- 
# **Distance from Paris to London:** 344 km\n- 
# **Distance from London to Tokyo:** Distance not available\n\n
# If you need further information or assistance, feel free to ask!"
```

NOTE: `Call` does not support tool calling as it does not track message history. Use `Chat` if you need tool calling.