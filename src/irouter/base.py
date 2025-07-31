from IPython.display import Markdown, display
from fastcore.net import urljson

BASE_URL = "https://openrouter.ai/api/v1"
BASE_HEADERS = {
    "HTTP-Referer": "https://github.com/CarloLepelaars/irouter",  # Site URL for rankings on openrouter.ai.
    "X-Title": "irouter",  # Site title for rankings on openrouter.ai.
}


def get_all_models(slug: bool = True) -> list[str]:
    """Get all models available in the Openrouter API.

    :param slug: If True get the slugs you need to initialize LLMs, else get the names of the LLMs.
    """
    data = urljson(f"{BASE_URL}/models")["data"]
    return [m["canonical_slug" if slug else "name"] for m in data]


def nb_markdown(msg: str) -> str:
    return display(Markdown(msg))


def history_to_markdown(history: dict, ipython: bool = False) -> str:
    """Convert Chat history to markdown.

    :param history: History from Chat object
    :param ipython: If true display as markdown in Jupyter notebooks.
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
