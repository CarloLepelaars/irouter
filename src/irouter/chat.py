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
        self.history = {model_name: [{"role": "system", "content": system}] for model_name in self.model}

    def _get_resp(self, model: str, message: str, extra_headers: dict = {}):
        self.history[model].append({"role": "user", "content": message})
        return self.client.chat.completions.create(
            model=model,
            messages=self.history[model],
            extra_headers=extra_headers,
        )

    def __call__(self, message: str, extra_headers: dict = {}, text_output: bool = True):
        resps = [self._get_resp(model, message, extra_headers) for model in self.model]
        message_objs = [resp.choices[0].message for resp in resps]
        for model, message_obj in zip(self.model, message_objs):
            self.history[model].append({"role": "assistant", "content": message_obj.content})
        outputs = [message_obj.content for message_obj in message_objs] if text_output else message_objs
        return outputs[0] if len(self.model) == 1 else outputs
        
    # TODO: Track usage in use attr
    # TODO: Add streaming
    # TODO: Add tool usage support
    # TODO: Add list message input support (For example url and text)
    # TODO: Add image support (if input is bytes or url with img suffix)


