import os
from openai import OpenAI
from openai.types.chat import ChatCompletion
from fastcore.basics import listify

from .base import BASE_URL, BASE_HEADERS, detect_content_type, encode_base64


class Call:
    """One-off API calls without history and usage tracking."""

    def __init__(
        self,
        model: str | list[str],
        base_url: str = BASE_URL,
        api_key: str = None,
        system: str = "",
    ):
        """
        :param model: Model(s) to use
        :param base_url: API base URL. Default to Openrouter.
        :param api_key: API key, defaults to `OPENROUTER_API_KEY`
        :param system: System prompt
        NOTE: If you get a bug where the model says image input is not supported, try passing a system prompt. This fixes the issue for some models.
        NOTE: Some models, like google/gemma-3n-e2b-it, do not support system messages. In that case leave the system prompt empty.
        """
        self.models = listify(model)
        self.base_url = base_url
        self.system = system
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"), base_url=base_url
        )

    # TODO: Add Streaming support.
    # TODO: Add support for tool usage.
    # TODO: Exception handling.
    def __call__(
        self,
        message: str | list[str] | list[dict],
        extra_headers: dict = {},
        raw: bool = False,
    ) -> str | dict[str, str] | ChatCompletion | dict[str, ChatCompletion]:
        """Make API call.

        :param message: Message string, list of strings or list of message dicts.
        If message string or list of strings is provided, a system prompt is added.
        If message dicts are provided, no additional system prompt is added.
        :param extra_headers: Additional headers for the Openrouter API.
        :param raw: If True, returns the raw ChatCompletion object.
        :returns: Single response or list based on model count.
        """
        inp = []
        if isinstance(message, (str, list)) and all(
            isinstance(m, str) for m in listify(message)
        ):
            if self.system:
                inp.append({"role": "system", "content": self.system})
            inp.append(self.construct_user_message(message))
        else:
            inp = message

        resps = {
            model: self._get_resp(
                model=model, messages=inp, extra_headers=extra_headers, raw=raw
            )
            for model in self.models
        }
        return resps[self.models[0]] if len(self.models) == 1 else resps

    def construct_user_message(self, message: str | list[str] | dict) -> dict:
        """Construct a user message dict from various input types.

        :param message: String, list of strings, or pre-built message dict
        :returns: User message dict with proper content structure
        """
        if isinstance(message, str):
            return {"role": "user", "content": message}
        elif isinstance(message, list) and all(isinstance(m, str) for m in message):
            return {"role": "user", "content": self.construct_content(message)}
        else:
            return message

    def construct_content(self, msg_list: list[str]) -> list:
        """Construct content for API call.

        :param msg_list: List of messages.
        :returns: Content list for API call.
        """
        content = []
        for m in msg_list:
            content_type = detect_content_type(m.strip())
            if content_type == "image_url":
                content.append({"type": "image_url", "image_url": {"url": m}})
            elif content_type == "local_image":
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_base64(m)}"
                        },
                    }
                )
            else:
                content.append({"type": "text", "text": m})
        return content

    def _get_resp(
        self,
        model: str,
        messages: list[dict],
        extra_headers: dict,
        raw: bool,
    ) -> str | ChatCompletion:
        """Get API response with merged headers.

        :param model: Model name to use
        :param messages: Message list for completion
        :param extra_headers: Additional headers, overrides BASE_HEADERS if same keys are given.
        Overriding HTTP-Referer and X-Title in extra_headers can be useful if you want to implement your own site tracking on openrouter.ai.
        :param raw: Return raw response if True, else content string
        :returns: Response content string or raw ChatCompletion object
        """
        # By default the base header is defined as irouter so tokens are counted for the openrouter.ai library.
        # Headers can be overwritten by defining extra_headers.
        # Check https://openrouter.ai/docs/quickstart for examples of extra headers that can be set.
        headers = {**BASE_HEADERS, **extra_headers}
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            extra_headers=headers,
        )
        return resp if raw else resp.choices[0].message.content
