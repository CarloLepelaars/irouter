from fastcore.basics import listify
from .call import Call

# TODO: Clean up and test usage.
class Chat:
    """Chat with history and usage tracking."""

    def __init__(
        self,
        model: str | list[str],
        system: str = "You are a helpful assistant.",
        base_url: str = None,
        api_key: str = None,
    ):
        """
        :param model: Model name(s) to use
        :param system: System prompt
        :param base_url: API base URL
        :param api_key: API key, defaults to OPENROUTER_API_KEY env var
        """
        self.model = listify(model)
        self.call = Call(model, base_url, api_key)
        self.system = system
        self.history = {m: [{"role": "system", "content": system}] for m in self.model}
        self.usage = {
            m: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            for m in self.model
        }

    def __call__(
        self, message: str, extra_headers: dict = {}
    ) -> str | list[str]:
        """Send message and update history.

        :param message: User message
        :param extra_headers: Additional headers
        :param text_output: Return text content if True, else message objects
        :returns: Single response or list based on model count
        """
        for model in self.model:
            self.history[model].append({"role": "user", "content": message})
        resps = [
            self.call._get_resp(model, self.history[model], extra_headers)
            for model in self.model
        ]

        for model, resp in zip(self.model, resps):
            msg = resp.choices[0].message
            self.history[model].append({"role": "assistant", "content": msg.content})
            if hasattr(resp, "usage") and resp.usage:
                usage = resp.usage
                self.usage[model]["prompt_tokens"] += usage.prompt_tokens
                self.usage[model]["completion_tokens"] += usage.completion_tokens
                self.usage[model]["total_tokens"] += usage.total_tokens

        outputs = [resp.choices[0].message.content for resp in resps]

        return outputs[0] if len(self.model) == 1 else outputs

    # TODO: Add streaming
    # TODO: Add tool usage support
    # TODO: Add list message input support (For example url and text)
    # TODO: Add image support (if input is bytes or url with img suffix)
