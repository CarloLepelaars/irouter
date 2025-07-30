import os
from openai import OpenAI
from fastcore.basics import listify

from .base import BASE_URL

class Chat:
    def __init__(self, model: str | list[str], system: str = "You are a helpful assistant.", 
                 base_url: str = BASE_URL, api_key: str = None):
        self.model = listify(model)
        self.client = OpenAI(api_key=api_key or os.getenv("OPENROUTER_API_KEY"), base_url=base_url)
        self.system = system
        self.messages = []

    def _get_resp(self, model: str, message: str, extra_headers: dict = {}):
        return self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": self.system}, {"role": "user", "content": message}],
            extra_headers=extra_headers,
        )

    def __call__(self, message: str, extra_headers: dict = {}, text_output: bool = True):
        resps = [self._get_resp(model, message, extra_headers) for model in self.model]
        outputs = [resp.choices[0].message.content for resp in resps] if text_output else resps
        if len(outputs) == 1:
            return outputs[0]
        else:
            return {model: output for model, output in zip(self.model, outputs)}

