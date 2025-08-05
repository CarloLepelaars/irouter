import re
import inspect
from ast import literal_eval
from typing import Any, Callable


def parse_doc_params(docstring: str) -> dict:
    """Parse function parameter descriptions from a docstring.

    :param docstring: The docstring to parse.
    :returns: Dictionary mapping parameter names to descriptions.
    """
    doc_lines = [line.strip() for line in docstring.strip().splitlines()]
    param_descs = {}
    param_re = re.compile(r":param\s+(\w+):\s*(.*)")
    for line in doc_lines:
        match = param_re.match(line)
        if match:
            param_name, param_desc = match.groups()
            param_descs[param_name] = param_desc
    return param_descs


def parse_func_params(func: Callable, param_descs: dict) -> dict:
    """Parse function signature and parameter descriptions to build properties and required lists.

    :param func: Function to parse.
    :param param_descs: Parameter descriptions to use.
    :returns: Dictionary with function parameters and their descriptions.
    """
    type_map = {
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }
    param_dict = {"type": "object", "properties": {}, "required": []}
    for name, param in inspect.signature(func).parameters.items():
        param_type = type_map.get(param.annotation, "string")
        desc = param_descs.get(name, "")
        param_dict["properties"][name] = {"type": param_type, "description": desc}
        if param.default is inspect.Parameter.empty:
            param_dict["required"].append(name)
    return param_dict


def function_to_schema(func: Callable) -> dict:
    """Convert function into schema dictionary describing its signature in the required format.

    :param func: Function to convert.
    :returns: Dictionary with the function schema.
    """
    doc_string = func.__doc__ or ""
    param_descs = parse_doc_params(doc_string)
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc_string,
            "parameters": parse_func_params(func, param_descs),
        },
    }
    return schema


def call_func(tool_call, funcs: list[Callable]) -> Any | Exception:
    """Call a function from a ChatCompletionMessageToolCall.

    :param tool_call: The tool call returned by the API.
    :param funcs: List of functions that can be called.
    :returns: The result of the function call or Exception if error.
    """
    ns = {f.__name__: f for f in funcs}
    f = ns.get(tool_call.function.name)
    if f is None:
        raise ValueError(f"Function {tool_call.function.name} not found")
    try:
        args = literal_eval(tool_call.function.arguments or "{}")
        return f(**(args if isinstance(args, dict) else {}))
    except Exception as e:
        return e


def create_tool_results(tool_calls, funcs: list[Callable]) -> list[dict]:
    """Create tool result messages from tool calls.

    :param tool_calls: List of tool calls from the API response.
    :param funcs: List of functions that can be called.
    :returns: List of tool result message dictionaries.
    """
    results = []
    for tc in tool_calls:
        output = call_func(tc, funcs)
        results.append({"tool_call_id": tc.id, "role": "tool", "content": str(output)})
    return results
