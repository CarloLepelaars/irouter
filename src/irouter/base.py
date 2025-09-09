import base64
from typing import Any
from pathlib import Path
from fastcore.net import urljson, urlread
from urllib.parse import urlparse

BASE_URL = "https://openrouter.ai/api/v1"
# By default, irouter is used as Site URL and title for rankings on openrouter.ai.
# This can be overwritten by defining `extra_headers` in the `Call` or `Chat` object.
BASE_HEADERS = {
    "HTTP-Referer": "https://github.com/CarloLepelaars/irouter",  # Site URL for rankings on openrouter.ai.
    "X-Title": "irouter",  # Site title for rankings on openrouter.ai.
}

TOOL_LOOP_FINAL_PROMPT = "You have run out of tool uses. Please summarize what you did in the tool loop to the user. If the goal was not reached please inform the reader that you ran out of steps and what work still needs to be done. The user will decide how to proceed."


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


def download_and_encode_url(url: str) -> str:
    """Download URL content and encode to base64.

    :param url: URL to download.
    :returns: Base64 encoded content.
    """
    binary_data = urlread(url, decode=False)
    return base64.b64encode(binary_data).decode("utf-8")


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
    6. "audio_url" if item is a URL and ends with a supported audio extension.
    7. "local_audio" if item is a local file path and ends with a supported audio extension.

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
            elif suffix in SUPPORTED_AUDIO_EXTENSIONS:
                return "audio_url"
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
                    return "local_audio"
    return "text"


def history_to_markdown(history: dict) -> str:
    """Convert Chat history to markdown.

    :param history: History from Chat object
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
    return "\n\n".join(md)
