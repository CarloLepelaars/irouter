# Image Support

`irouter` supports image input for both `Call` and `Chat` objects. Images can be provided as URLs or local file paths.

Make sure to use an LLM that supports image processing, like `gpt-4o-mini`.

For a full overview of which LLMs support image input, check the [OpenRouter Model Overview](https://openrouter.ai/models?fmt=cards&input_modalities=image).

<img src="https://www.petlandflorida.com/wp-content/uploads/2022/04/shutterstock_1290320698-1-scaled.jpg" width="300">

## Image URL

`irouter` can work directly with image URLs. Just pass the URL and instruction as a list of strings.

```python
from irouter import Call

c = Call("gpt-4o-mini", system="You analyze images.")
image_url = "https://www.petlandflorida.com/wp-content/uploads/2022/04/shutterstock_1290320698-1-scaled.jpg"
c([image_url, "What is in the image?"])
# 'The image features a cute corgi puppy sitting down. The puppy has a fluffy coat with a mix of orange and white colors...'
```

## Local Image

Local images can be passed as a path to the `Call` or `Chat` object.

```python
c(["../assets/puppy.jpg", "What is in the image?"])
# 'The image shows a cute puppy, specifically a Corgi. The puppy has a light brown and white coat...'
```

## Chat with Images

The only difference of `Chat` and `Call` is that `Chat` also tracks conversation history and token usage.

```python
from irouter import Chat

chat = Chat("gpt-4o-mini", system="You analyze images.")
chat([image_url, "What is in the image?"])
print(chat.history)
print(chat.usage)
```