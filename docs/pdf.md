# PDF Support

`irouter` supports PDF processing for both `Call` and `Chat` objects. PDFs can be provided as URLs or local file paths with various parsing engines.

If the selected LLM has native file processing capabilities, that parser will be used. Otherwise the `mistral-ocr` parser is used, which has some small costs associated with it.

For more details on PDF support in OpenRouter and pricing, check [this docs page](https://openrouter.ai/docs/features/images-and-pdfs#pdf-support).

To see an overview of which LLMs support file input, check the [OpenRouter Model Overview](https://openrouter.ai/models?fmt=cards&input_modalities=audio%2Cfile).

<img src="https://nlp.seas.harvard.edu/images/the-annotated-transformer_0_0.png" width="300"/>

## PDF URL

The simplest way to work with PDF files in `irouter` is to pass the URL of the PDF file and instruction as a list of strings.

```python
from irouter import Call

model = "moonshotai/kimi-k2:free"
# The "Attention Is All You Need" paper
pdf_url = "https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"

c = Call(model)
c([pdf_url, "What is the main contribution of this paper?"])
```

## PDF Parsing Configuration

You can specify different PDF parsing engines using the `extra_body` parameter. For example, use the `pdf-text` engine for free parsing.

```python
extra_body = {"plugins": [{"id": "file-parser", "pdf": {"engine": "pdf-text"}}]}
c([pdf_url, "Summarize the key innovations in this paper."], extra_body=extra_body)
```

Check [this docs page](https://openrouter.ai/docs/features/multimodal/pdfs#plugin-configuration) for OpenRouter's details on plugin configuration.

## Chat with PDF

In contrast to the `Call` class, `Chat` tracks history and token usage.

```python
from irouter import Chat

chat = Chat(model)
chat([pdf_url, "What is this paper about?"])
# Follow up questions.
chat("What are the key advantages of this approach over RNNs?")
# History and usage is tracked.
print(chat.history)
print(chat.usage)
```