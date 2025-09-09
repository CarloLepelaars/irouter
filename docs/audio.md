# Audio Support

Here we show how `irouter` makes audio queries as simple as text, image and PDF queries.

There are a limited amount of models that support audio input. Make sure to use an LLM that supports audio input, like `google/gemini-2.5-flash`.

To check which LLMs support audio input, check out the [Model Overview](https://openrouter.ai/models?fmt=cards&input_modalities=audio).

## Audio URLs

The simplest way to work with audio files in `irouter` is to pass an audio URL containing an `.mp3` or `.wav` file:

```python
from irouter import Call

model_name = "google/gemini-2.5-flash"
audio_url = "https://www.bird-sounds.net/birdmedia/241/860.mp3"

c = Call(model_name)
c([audio_url, "What bird is this?"], temperature=0)
# 'Based on the distinct "caw, caw" calls, this is an **American Crow**.'
```

## Local Audio Files

You can also use local audio files by passing the filepath and an instruction as a list of strings:

```python
from irouter import Call

model_name = "google/gemini-2.5-flash"
audio_path = "../assets/bottles.mp3"

c = Call(model_name)
c([audio_path, "What do you hear?"], temperature=0)
# 'I hear the sound of a glass bottle being opened and closed, along with the distinct clinking of glass.'
```

## Chat with Audio

Use `Chat` for conversation tracking and token usage monitoring:

```python
from irouter import Chat

chat = Chat(model_name)
chat([audio_path, "What do you hear?"])
print(chat.history)
print(chat.usage)
```