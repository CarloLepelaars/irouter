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


def test_construct_user_message():
    with patch("irouter.call.OpenAI"):
        call = Call("test-model")

    result = call.construct_user_message("Hello")
    assert result == {"role": "user", "content": "Hello"}

    # Mock image detection
    with patch("irouter.call.detect_content_type") as mock_detect:
        mock_detect.side_effect = ["text", "text"]  # Both items are text
        result = call.construct_user_message(["Hello", "world"])
        expected_content = [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "world"},
        ]
        assert result == {"role": "user", "content": expected_content}

    # Pre-built message dict
    message_dict = {"role": "user", "content": "Pre-built message"}
    result = call.construct_user_message(message_dict)
    assert result == message_dict


def test_construct_content():
    with patch("irouter.call.OpenAI"):
        call = Call("test-model")

    with (
        patch("irouter.call.detect_content_type") as mock_detect,
        patch("irouter.call.encode_base64", return_value="base64data"),
    ):
        mock_detect.side_effect = ["image_url", "text", "local_image"]

        result = call.construct_content(
            [
                "https://example.com/image.jpg",
                "What is in the image?",
                "local_image.png",
            ]
        )

        expected = [
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/image.jpg"},
            },
            {"type": "text", "text": "What is in the image?"},
            {
                "type": "image_url",
                "image_url": {"url": "data:image/jpeg;base64,base64data"},
            },
        ]
        assert result == expected


def test_call_with_images():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Image response"

    with (
        patch("irouter.call.OpenAI") as mock_openai,
        patch("irouter.call.detect_content_type") as mock_detect,
        patch("irouter.call.encode_base64", return_value="base64data"),
    ):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        mock_detect.side_effect = ["image_url", "text"]

        call = Call("gpt-4o-mini", system="You are helpful")
        result = call(["https://example.com/image.jpg", "What is in the image?"])

        assert result == "Image response"

        # Verify the message structure sent to API
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]

        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "You are helpful"}

        user_message = messages[1]
        assert user_message["role"] == "user"
        assert len(user_message["content"]) == 2
        assert user_message["content"][0]["type"] == "image_url"
        assert user_message["content"][1]["type"] == "text"
