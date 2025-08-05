"""Tests for tool utilities."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from irouter.tool import (
    call_func,
    create_tool_results,
    function_to_schema,
    parse_doc_params,
    parse_func_params,
)


def sample_func(name: str, age: int = 25, active: bool = True) -> str:
    """A sample function for testing.

    :param name: The person's name.
    :param age: The person's age.
    :param active: Whether the person is active.
    :returns: A formatted string.
    """
    return f"{name} is {age} years old and {'active' if active else 'inactive'}"


def get_time(fmt: str = "%Y-%m-%d %H:%M:%S", utc: bool = False) -> str:
    """Returns the current time formatted as a string.

    :param fmt: Format string for strftime.
    :param utc: If True, returns UTC time.
    :returns: The formatted current time.
    """
    now = datetime.now(timezone.utc) if utc else datetime.now()
    return now.strftime(fmt)


def broken_func(x: int) -> int:
    """A function that raises an error.

    :param x: Input number.
    :returns: Never returns, always raises.
    """
    raise ValueError("This function always fails")


def test_parse_doc_params():
    """Test parsing parameter descriptions from docstrings."""
    docstring = """A sample function.
    
    :param name: The person's name.
    :param age: The person's age.
    :returns: A string.
    """
    result = parse_doc_params(docstring)
    assert result == {"name": "The person's name.", "age": "The person's age."}


def test_parse_doc_params_empty():
    """Test parsing empty docstring."""
    result = parse_doc_params("")
    assert result == {}


def test_parse_func_params():
    """Test parsing function parameters."""
    param_descs = {"name": "The person's name.", "age": "The person's age."}
    result = parse_func_params(sample_func, param_descs)

    expected = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The person's name."},
            "age": {"type": "integer", "description": "The person's age."},
            "active": {"type": "boolean", "description": ""},
        },
        "required": ["name"],
    }
    assert result == expected


def test_function_to_schema():
    """Test converting function to schema."""
    schema = function_to_schema(sample_func)

    assert schema["type"] == "function"
    assert schema["function"]["name"] == "sample_func"
    assert "A sample function for testing." in schema["function"]["description"]
    assert "name" in schema["function"]["parameters"]["properties"]
    assert "age" in schema["function"]["parameters"]["properties"]
    assert schema["function"]["parameters"]["required"] == ["name"]


def test_call_func_success():
    """Test successful function call."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(
            name="sample_func", arguments='{"name": "John", "age": 30}'
        )
    )

    result = call_func(tool_call, [sample_func])
    assert result == "John is 30 years old and active"


def test_call_func_with_defaults():
    """Test function call using default parameters."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(name="sample_func", arguments='{"name": "Jane"}')
    )

    result = call_func(tool_call, [sample_func])
    assert result == "Jane is 25 years old and active"


def test_call_func_empty_args():
    """Test function call with empty arguments."""
    tool_call = SimpleNamespace(function=SimpleNamespace(name="get_time", arguments=""))

    result = call_func(tool_call, [get_time])
    assert isinstance(result, str)
    assert len(result) > 0


def test_call_func_invalid_args():
    """Test function call with invalid arguments."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(name="sample_func", arguments="invalid json")
    )

    result = call_func(tool_call, [sample_func])
    assert isinstance(result, Exception)


def test_call_func_function_not_found():
    """Test function call when function doesn't exist."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(name="nonexistent_func", arguments="{}")
    )

    with pytest.raises(ValueError, match="Function nonexistent_func not found"):
        call_func(tool_call, [sample_func])


def test_call_func_function_error():
    """Test function call when function raises error."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(name="broken_func", arguments='{"x": 5}')
    )

    result = call_func(tool_call, [broken_func])
    assert isinstance(result, ValueError)
    assert str(result) == "This function always fails"


def test_create_tool_results():
    """Test creating tool results from tool calls."""
    tool_calls = [
        SimpleNamespace(
            id="call_123",
            function=SimpleNamespace(
                name="sample_func", arguments='{"name": "Alice", "age": 28}'
            ),
        ),
        SimpleNamespace(
            id="call_456",
            function=SimpleNamespace(name="get_time", arguments='{"fmt": "%Y-%m-%d"}'),
        ),
    ]

    results = create_tool_results(tool_calls, [sample_func, get_time])

    assert len(results) == 2
    assert results[0]["tool_call_id"] == "call_123"
    assert results[0]["role"] == "tool"
    assert results[0]["content"] == "Alice is 28 years old and active"

    assert results[1]["tool_call_id"] == "call_456"
    assert results[1]["role"] == "tool"
    assert isinstance(results[1]["content"], str)


def test_create_tool_results_with_error():
    """Test creating tool results when function fails."""
    tool_calls = [
        SimpleNamespace(
            id="call_error",
            function=SimpleNamespace(name="broken_func", arguments='{"x": 1}'),
        )
    ]

    results = create_tool_results(tool_calls, [broken_func])

    assert len(results) == 1
    assert results[0]["tool_call_id"] == "call_error"
    assert results[0]["role"] == "tool"
    assert "This function always fails" in results[0]["content"]
