import base64
from typing import Any
from pathlib import Path
from urllib.parse import urlparse
from IPython.display import Markdown, display
from fastcore.net import urljson

BASE_URL = "https://openrouter.ai/api/v1"
# By default, irouter is used as Site URL and title for rankings on openrouter.ai.
# This can be overwritten by defining `extra_headers` in the `Call` or `Chat` object.
BASE_HEADERS = {
    "HTTP-Referer": "https://github.com/CarloLepelaars/irouter",  # Site URL for rankings on openrouter.ai.
    "X-Title": "irouter",  # Site title for rankings on openrouter.ai.
}


def get_all_models(slug: bool = True) -> list[str]:
    """Get all models available in the Openrouter API.

    :param slug: If True get the slugs you need to initialize LLMs, else get the names of the LLMs.
    :returns: List of models.
    """
    data = urljson(f"{BASE_URL}/models")["data"]
    return [m["canonical_slug" if slug else "name"] for m in data]


def encode_base64(path: str) -> str:
    """Encode to base64.

    :param path: Path to file.
    :returns: Base64 encoded file.
    """
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def detect_content_type(item: Any) -> str:
    """Detect content type of item.
    Options are:
    1. "text" if the item is a non-string or doesn't belong to any of the other categories.
    Images:
    2. "image_url" if item is a URL and ends with a supported image extension.
    3. "local_image" if item is a local file path and ends with a supported image extension.
    PDFs:
    4. "pdf_url" if item is a URL and ends with a PDF extension.
    5. "local_pdf" if item is a local file path and ends with a PDF extension.
    Audio:
    6. "audio" if item is a local file path and ends with a supported audio extension.

    :param item: Item to detect content type of.
    :returns: Content type of item.
    """
    if isinstance(item, str):
        SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
        SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav"}
        parsed = urlparse(item)
        suffix = Path(parsed.path).suffix.lower()
        # URLs
        if parsed.scheme in ("http", "https"):
            if suffix in SUPPORTED_IMAGE_EXTENSIONS:
                return "image_url"
            elif suffix == ".pdf":
                return "pdf_url"
        # Local files
        else:
            if (
                suffix
                in {".pdf"} | SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_AUDIO_EXTENSIONS
            ):
                path = Path(item)
                if not path.exists():
                    raise FileNotFoundError(f"File not found: {item}")
                if suffix == ".pdf":
                    return "local_pdf"
                elif suffix in SUPPORTED_IMAGE_EXTENSIONS:
                    return "local_image"
                elif suffix in SUPPORTED_AUDIO_EXTENSIONS:
                    return "audio"
    return "text"


def nb_markdown(msg: str) -> str:
    """Display markdown in Jupyter notebooks.

    :param msg: Message to display.
    :returns: Displayed message.
    """
    return display(Markdown(msg))


def history_to_markdown(history: dict, ipython: bool = False) -> str:
    """Convert Chat history to markdown.

    :param history: History from Chat object
    :param ipython: If true display as markdown in Jupyter notebooks.
    :returns: String showing the conversation history.
    """
    md = []
    for msg in history[next(iter(history))]:
        role = msg["role"].capitalize()
        content = msg["content"]
        if role == "User":
            md.append(f"**User:** {content}")
        elif role == "Assistant":
            md.append(f"**Assistant:** {content}")
        elif role == "System":
            md.append(f"**System:** {content}")
        else:
            md.append(f"**{role}:** {content}")
    joined = "\n\n".join(md)
    return nb_markdown(joined) if ipython else joined
