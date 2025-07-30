from IPython.display import Markdown, display
from fastcore.net import urljson

BASE_URL = "https://openrouter.ai/api/v1"

def get_all_models(slug=True):
    data = urljson(f"{BASE_URL}/models")['data']
    return [m['canonical_slug' if slug else 'name'] for m in data]

def history_to_markdown(history: dict, ipython: bool = False):
    md = []
    for msg in history[next(iter(history))]:
        role = msg['role'].capitalize()
        content = msg['content']
        if role == "User":
            md.append(f"**User:** {content}")
        elif role == "Assistant":
            md.append(f"**Assistant:** {content}")
        elif role == "System":
            md.append(f"**System:** {content}")
        else:
            md.append(f"**{role}:** {content}")
    joined = "\n\n".join(md)
    return display(Markdown(joined)) if ipython else joined
