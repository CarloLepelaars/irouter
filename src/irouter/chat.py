from fastcore.basics import listify
from .call import Call
from .base import BASE_URL


class Chat:
    """Chat with history and usage tracking."""

    def __init__(
        self,
        model: str | list[str],
        system: str = "You are a helpful assistant.",
        base_url: str = BASE_URL,
        api_key: str = None,
    ):
        """
        :param model: Model name(s) to use
        :param system: System prompt
        :param base_url: API base URL
        :param api_key: API key, defaults to OPENROUTER_API_KEY env var
        """
        self.models = listify(model)
        self.base_url = base_url
        self.system = system
        self.call = Call(
            model=self.models, base_url=base_url, api_key=api_key, system=system
        )
        self._history = {
            m: [{"role": "system", "content": system}] for m in self.models
        }
        self._usage = {
            m: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            for m in self.models
        }

    def __call__(
        self, message: str | list[str], extra_headers: dict = {}
    ) -> str | list[str]:
        """Send message and update history.

        :param message: User message or list of strings.
        For example, if an image URL or bytes and text are passed, the image will be handled in the LLM call.
        :param extra_headers: Additional headers
        :returns: Single response or list based on model count
        """
        for model in self.models:
            self._history[model].append({"role": "user", "content": message})
        resps = [
            self.call._get_resp(model, self._history[model], extra_headers, raw=True)
            for model in self.models
        ]

        for model, resp in zip(self.models, resps):
            msg = resp.choices[0].message
            self._history[model].append({"role": "assistant", "content": msg.content})
            if hasattr(resp, "usage") and resp.usage:
                usage = resp.usage
                self._usage[model]["prompt_tokens"] += usage.prompt_tokens
                self._usage[model]["completion_tokens"] += usage.completion_tokens
                self._usage[model]["total_tokens"] += usage.total_tokens

        outputs = {
            model: resp.choices[0].message.content
            for model, resp in zip(self.models, resps)
        }
        return outputs[self.models[0]] if len(self.models) == 1 else outputs

    @property
    def history(self) -> list[dict] | dict[str, list[dict]]:
        """Get history for a model.
        If single model is used, return the history for that model (list of dicts).
        If multiple models are used, return a dict mapping model to history.
        """
        return self._history if len(self.models) > 1 else self._history[self.models[0]]

    @property
    def usage(self) -> dict[str, dict[str, int]] | dict[str, int]:
        """Get usage for a model.
        If single model is used, return the usage for that model (dict).
        If multiple models are used, return a dict mapping model to usage.
        """
        return self._usage if len(self.models) > 1 else self._usage[self.models[0]]

    # TODO: Add streaming
    # TODO: Add tool usage support
    # TODO: Add list message input support (For example url and text)
    # TODO: Add image support (if input is bytes or url with img suffix)
