
from fastcore.net import urljson

BASE_URL = "https://openrouter.ai/api/v1"

def get_all_models(slug=True):
    data = urljson(f"{BASE_URL}/models")['data']
    return [m['canonical_slug' if slug else 'name'] for m in data]
