from unittest.mock import patch, MagicMock

from irouter.base import BASE_URL
from irouter.call import Call


def test_call():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("test-model", system="Test system")
        assert call.base_url == BASE_URL

        result = call("Hello world")
        assert result == "Test response"

        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "test-model"
        assert call_args[1]["messages"] == [
            {"role": "system", "content": "Test system"},
            {"role": "user", "content": "Hello world"},
        ]

        raw_result = call("Hello", raw=True)
        assert raw_result == mock_response

        multi_call = Call(["model1", "model2"])
        multi_result = multi_call("Hello")
        assert isinstance(multi_result, dict)
        assert len(multi_result) == 2

        messages = [
            {"role": "system", "content": "Test system"},
            {"role": "user", "content": "Direct messages"},
            {"role": "assistant", "content": "Test response"},
            {"role": "user", "content": "Hello world"},
        ]
        call(messages)
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["messages"] == messages
