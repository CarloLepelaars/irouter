from fastcore.basics import listify
from .call import Call
from .base import BASE_URL
from .tool import function_to_schema, create_tool_results


class Chat:
    """Chat with history tracking, usage tracking, and tool support."""

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
        self,
        message: str | list[str],
        tools: list = None,
        max_steps: int = 10,
        extra_headers: dict = {},
        extra_body: dict = {},
        **kwargs,
    ) -> str | list[str]:
        """Send message and update history with optional tool calling.

        :param message: User message or list of strings.
        For example, if an image URL or bytes and text are passed, the image will be handled in the LLM call.
        :param tools: List of functions available for tool calling.
        :param max_steps: Maximum number of tool call iterations.
        :param extra_headers: Additional headers
        :param extra_body: Openrouter-only API body parameters.
        For example, to set the free PDF parser plugin: {"plugins": [{"id": "file-parser", "pdf": {"engine": "pdf-text"}}]}.
        **kwargs are passed to the API chat completion call. Common parameters include `temperature` and `max_tokens`.
        :returns: Single response or list based on model count
        """
        if tools:
            # Multi-round tool calling
            list(
                self.toolloop(
                    message=message,
                    tools=tools,
                    max_steps=max_steps,
                    extra_headers=extra_headers,
                    extra_body=extra_body,
                    **kwargs,
                )
            )
        else:
            # Simple single API call (no tools)
            self._simple_call(
                message=message,
                extra_headers=extra_headers,
                extra_body=extra_body,
                **kwargs,
            )

        return self._get_final_outputs()

    def update_token_usage(self, resp, model: str):
        """Update token usage for a model.

        :param resp: ChatCompletion object
        """
        if hasattr(resp, "usage") and resp.usage:
            usage = resp.usage
            self._usage[model]["prompt_tokens"] += usage.prompt_tokens
            self._usage[model]["completion_tokens"] += usage.completion_tokens
            self._usage[model]["total_tokens"] += usage.total_tokens

    @property
    def history(self) -> list[dict] | dict[str, list[dict]]:
        """Get history for a model.
        If single model is used, return the history for that model (list of dicts).
        If multiple models are used, return a dict mapping model to history.

        :returns: History for a model or dict mapping model to history.
        """
        return self._history if len(self.models) > 1 else self._history[self.models[0]]

    @property
    def usage(self) -> dict[str, dict[str, int]] | dict[str, int]:
        """Get usage for a model.
        If single model is used, return the usage for that model (dict).
        If multiple models are used, return a dict mapping model to usage.

        :returns: Usage for a model or dict mapping model to usage.
        """
        return self._usage if len(self.models) > 1 else self._usage[self.models[0]]

    def set_history(self, history: list[dict]):
        """Set custom history for a model.

        :param history: List of dicts (messages) which define history for a model
        :returns: None
        """
        assert isinstance(history, list), (
            f"History must be a list of dicts. Got {type(history)}"
        )
        for h in history:
            assert isinstance(h, dict), (
                f"History must be a list of dicts. Got {type(h)}"
            )
            assert "role" in h, f"History must contain a role. Got {h}"
            assert "content" in h, f"History must contain a content. Got {h}"
            assert h["role"] in ["system", "user", "assistant"], (
                f"Role must be one of system, user, or assistant. Got {h['role']}"
            )
        self._history = history

    def reset_history(self):
        """Reset history for all models."""
        self._history = {
            m: [{"role": "system", "content": self.system}] for m in self.models
        }

    def reset_usage(self):
        """Reset usage for all models."""
        self._usage = {
            m: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            for m in self.models
        }

    def reset(self):
        """Reset history and usage for all models."""
        self.reset_history()
        self.reset_usage()

    def _execute_tool_calls(self, tool_calls, tools: list, model: str):
        """Execute tool calls and add results to history.

        :param tool_calls: Tool calls from assistant message
        :param tools: List of available tool functions
        :param model: Model name
        """
        tool_results = create_tool_results(tool_calls=tool_calls, funcs=tools)
        self._history[model].extend(tool_results)

    def toolloop(
        self,
        message: str | list[str],
        tools: list = None,
        max_steps: int = 10,
        extra_headers: dict = {},
        extra_body: dict = {},
        **kwargs,
    ):
        """Send message and handle multiple rounds of tool calls.

        :param message: User message or list of strings
        :param tools: List of functions available for tool calling
        :param max_steps: Maximum number of tool call iterations
        :param extra_headers: Additional headers
        :param extra_body: Additional body parameters
        :yields: Response at each step of the tool loop
        """
        user_message = self.call.construct_user_message(message=message)
        for model in self.models:
            self._history[model].append(user_message)

        tool_schemas = (
            [function_to_schema(func=func) for func in tools] if tools else None
        )

        for model in self.models:
            step = 0
            while step < max_steps:
                resp = self.call._get_resp(
                    model=model,
                    messages=self._history[model],
                    extra_headers=extra_headers,
                    extra_body=extra_body,
                    raw=True,
                    tools=tool_schemas,
                    **kwargs,
                )

                msg = resp.choices[0].message
                assistant_msg = {"role": "assistant", "content": msg.content or ""}
                if msg.tool_calls:
                    assistant_msg["tool_calls"] = msg.tool_calls
                self._history[model].append(assistant_msg)
                self.update_token_usage(resp=resp, model=model)

                yield resp

                if msg.tool_calls and tools:
                    self._execute_tool_calls(
                        tool_calls=msg.tool_calls,
                        tools=tools,
                        model=model,
                    )
                    step += 1
                else:
                    break

    def _simple_call(
        self,
        message: str | list[str],
        extra_headers: dict = {},
        extra_body: dict = {},
        **kwargs,
    ):
        """Handle simple chat without tools (single API call).

        :param message: User message or list of strings
        :param extra_headers: Additional headers
        :param extra_body: Additional body parameters
        """
        user_message = self.call.construct_user_message(message=message)
        for model in self.models:
            self._history[model].append(user_message)

        for model in self.models:
            resp = self.call._get_resp(
                model=model,
                messages=self._history[model],
                extra_headers=extra_headers,
                extra_body=extra_body,
                raw=True,
                **kwargs,
            )

            msg = resp.choices[0].message
            assistant_msg = {"role": "assistant", "content": msg.content or ""}
            self._history[model].append(assistant_msg)
            self.update_token_usage(resp=resp, model=model)

    def _get_final_outputs(self) -> str | dict[str, str]:
        """Extract final assistant responses from history.

        :returns: Single response or dict mapping model to response
        """
        outputs = {}
        for model in self.models:
            for msg in reversed(self._history[model]):
                if msg["role"] == "assistant" and msg.get("content"):
                    outputs[model] = msg["content"]
                    break

        return outputs[self.models[0]] if len(self.models) == 1 else outputs

    # TODO: Add streaming
