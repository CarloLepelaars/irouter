import os
from openai import OpenAI


class Chat:
    def __init__(self, model: str, system: str = "You are a helpful assistant.", 
                 base_url: str = "https://openrouter.ai/api/v1", api_key: str = None):
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENROUTER_API_KEY"), base_url=base_url)
        self.system = system
        self.messages = []

    def __call__(self, message: str, extra_headers: dict = {}):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system}, {"role": "user", "content": message}],
            extra_headers=extra_headers,
        )
        return resp.choices[0].message.content
