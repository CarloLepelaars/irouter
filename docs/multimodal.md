
# Multiple Modalities

Using multiple modalities in `irouter` is as simple as passing a list of strings.

The available input modalities are:
1. text
2. Image URL
3. Local image filepath
4. PDF URL
5. Local PDF filepath
6. Audio URL
7. Local Audio filepath


Simply pass a list of strings when calling the `Call` or `Chat` object. For basic instructions on using `Call` and `Chat` check [call.md](call.md) and [chat.md](chat.md).

```python
from irouter import Call

model_name = "google/gemini-2.5-flash"
audio_path = "../assets/bottles.mp3"
img_path = "../assets/puppy.jpg"

c = Call(model_name)
c([audio_path, img_path, "What do you hear and what do you see? Limit your response to 1 sentence."])
# 'I hear sounds of glass or ceramic and see a small, fluffy dog on a blue surface with a green background.'
```