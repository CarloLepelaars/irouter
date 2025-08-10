# Web Search

Web search integration for LLM calls using the `Call` and `Chat` objects. Web citations are automatically tracked in `Chat` objects.

## Method 1: Tag `:online` to Model Slug

The simplest way to enable web search is to add the `:online` tag to your model slug. Web search is powered by [Exa](https://exa.ai/).

```python
from irouter import Chat
c = Chat("openai/gpt-4o:online")
c("Please search on the web for the latest version of OpenAI's GPT. What is it?")
# "The latest version of OpenAI's GPT is GPT-5..."
print(c.web_citations)
```

This enables the model to search the web and provide up-to-date information that wasn't in its training data.

## Method 2: Configure the Web Plugin

For more control over web search behavior, use the `web` plugin in the `extra_body` parameter:

```python
from irouter import Chat
c = Chat("openai/gpt-4o")

extra_body = {
    "plugins": [
        {
            "id": "web",
            "max_results": 10,
            "search_prompt": "Give me only the most trustworthy results. No Reddit, Linkedin or shoddy news sites."
        }
    ]
}

c("Check the latest news sources I'm giving you. What is the most recent released version of OpenAI's GPT?", extra_body=extra_body)
# "Based on the most recent trusted sources provided, the latest released version of 
# OpenAI's GPT is GPT-5. (The information suggests it was either recently released or 
# planned for a launch in early August 2025.)"
print(c.web_citations)
```


For detailed plugin configuration options, see the [OpenRouter Web Search documentation](https://openrouter.ai/docs/features/web-search#customizing-the-web-plugin).