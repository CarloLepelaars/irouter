import os
from openai import OpenAI
from openai.types.chat import ChatCompletion
from fastcore.basics import listify

from .base import BASE_URL, BASE_HEADERS


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
    # TODO: Support list of messages input where some may be image URLs or image bytes input.
    def __call__(
        self, message: str | list[dict], extra_headers: dict = {}, raw: bool = False
    ) -> str | dict[str, str] | ChatCompletion | dict[str, ChatCompletion]:
        """Make API call.

        :param message: User message or list of message dicts.
        If user message is provided, a system prompt is added.
        If message dicts are provided, no additional system prompt is added.
        :param extra_headers: Additional headers for the Openrouter API
        :param raw: If True, returns the raw ChatCompletion object.
        :returns: Single response or list based on model count.
        """
        inp = (
            [
                {"role": "system", "content": self.system},
                {"role": "user", "content": message},
            ]
            if isinstance(message, str)
            else message
        )
        resps = {
            model: self._get_resp(model, inp, extra_headers, raw)
            for model in self.models
        }
        return resps[self.models[0]] if len(self.models) == 1 else resps

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
