from unittest.mock import patch, MagicMock, Mock
from irouter.chat import Chat
from irouter.base import BASE_URL


def test_single_model_response():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Chat response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Hello"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model", system="Test system")
        assert chat.base_url == BASE_URL

        assert chat.system == "Test system"
        assert chat.history == [{"role": "system", "content": "Test system"}]
        assert chat.history[0]["role"] == "system"
        assert chat.history[0]["content"] == "Test system"

        result = chat("Hello")
        assert result == "Chat response"

        # Test history tracking
        assert len(chat.history) == 3
        assert chat.history[1]["role"] == "user"
        assert chat.history[1]["content"] == "Hello"
        assert chat.history[2]["role"] == "assistant"
        assert chat.history[2]["content"] == "Chat response"

        # Test usage tracking
        assert chat.usage["prompt_tokens"] == 10
        assert chat.usage["completion_tokens"] == 5
        assert chat.usage["total_tokens"] == 15


def test_multiple_model_response():
    # Create separate mock responses for each model
    mock_response1 = MagicMock()
    mock_response1.choices = [MagicMock()]
    mock_response1.choices[0].message.content = "Model1 response"
    mock_response1.choices[0].message.tool_calls = None
    mock_response1.usage = MagicMock()
    mock_response1.usage.prompt_tokens = 10
    mock_response1.usage.completion_tokens = 5
    mock_response1.usage.total_tokens = 15

    mock_response2 = MagicMock()
    mock_response2.choices = [MagicMock()]
    mock_response2.choices[0].message.content = "Model2 response"
    mock_response2.choices[0].message.tool_calls = None
    mock_response2.usage = MagicMock()
    mock_response2.usage.prompt_tokens = 8
    mock_response2.usage.completion_tokens = 12
    mock_response2.usage.total_tokens = 20

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()

        # Mock _get_resp to return different responses based on model
        def mock_get_resp(model, *args, **kwargs):
            return mock_response1 if model == "model1" else mock_response2

        mock_call._get_resp = Mock(side_effect=mock_get_resp)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Hello"}
        )
        mock_call_class.return_value = mock_call

        multi_chat = Chat(["model1", "model2"])
        multi_result = multi_chat("Hello")
        assert isinstance(multi_result, dict)
        assert len(multi_result) == 2
        assert multi_result == {
            "model1": "Model1 response",
            "model2": "Model2 response",
        }

        assert multi_chat.history == {
            "model1": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Model1 response"},
            ],
            "model2": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Model2 response"},
            ],
        }
        assert multi_chat.usage == {
            "model1": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model2": {"prompt_tokens": 8, "completion_tokens": 12, "total_tokens": 20},
        }

        assert multi_chat.history["model1"][2]["content"] == "Model1 response"
        assert multi_chat.history["model2"][2]["content"] == "Model2 response"


def test_chat_with_images():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Image chat response"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 15
    mock_response.usage.completion_tokens = 10
    mock_response.usage.total_tokens = 25

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)

        # Mock the construct_user_message method
        def mock_construct_user_message(message):
            if isinstance(message, list):
                return {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": "https://example.com/image.jpg"},
                        },
                        {"type": "text", "text": "What is in the image?"},
                    ],
                }
            return {"role": "user", "content": message}

        mock_call.construct_user_message = Mock(side_effect=mock_construct_user_message)
        mock_call_class.return_value = mock_call

        chat = Chat("gpt-4o-mini")
        result = chat(["https://example.com/image.jpg", "What is in the image?"])

        assert result == "Image chat response"

        # Test that image content is properly tracked in history
        assert len(chat.history) == 3  # system + user + assistant

        user_message = chat.history[1]
        assert user_message["role"] == "user"
        assert isinstance(user_message["content"], list)
        assert user_message["content"][0]["type"] == "image_url"
        assert user_message["content"][1]["type"] == "text"

        # Test usage tracking still works with images
        assert chat.usage["prompt_tokens"] == 15
        assert chat.usage["completion_tokens"] == 10
        assert chat.usage["total_tokens"] == 25


def test_chat_construct_user_message_integration():
    """Test that Chat properly delegates to Call's construct_user_message"""
    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "mocked"}
        )
        mock_call._get_resp = Mock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="test"))]
            )
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        chat("test message")

        # Verify construct_user_message was called with the input
        mock_call.construct_user_message.assert_called_once_with("test message")


def test_chat_with_extra_body():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Chat response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Hello"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        extra_body = {
            "provider": {"require_parameters": True},
            "transforms": ["middle-out"],
        }
        result = chat("Hello", extra_body=extra_body)

        assert result == "Chat response"
        # Verify _get_resp was called with extra_body
        mock_call._get_resp.assert_called_once_with(
            "test-model",
            chat._history["test-model"],
            {},
            extra_body,
            raw=True,
            tools=None,
        )


def test_chat_with_kwargs():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Chat response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Hello"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        result = chat("Hello", temperature=0.8, max_tokens=150, top_p=0.9)

        assert result == "Chat response"
        # Verify _get_resp was called with kwargs
        mock_call._get_resp.assert_called_once_with(
            "test-model",
            chat._history["test-model"],
            {},
            {},
            raw=True,
            tools=None,
            temperature=0.8,
            max_tokens=150,
            top_p=0.9,
        )


def test_chat_with_extra_headers():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Chat response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Hello"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        extra_headers = {"HTTP-Referer": "https://mysite.com", "X-Title": "My App"}
        result = chat("Hello", extra_headers=extra_headers)

        assert result == "Chat response"
        # Verify _get_resp was called with extra_headers
        mock_call._get_resp.assert_called_once_with(
            "test-model",
            chat._history["test-model"],
            extra_headers,
            {},
            raw=True,
            tools=None,
        )


def test_chat_with_plugins():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Chat response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Hello"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        plugins = [{"id": "file-parser", "pdf": {"engine": "pdf-text"}}]
        result = chat("Hello", extra_body={"plugins": plugins})

        assert result == "Chat response"
        # Verify _get_resp was called with plugins in extra_body
        mock_call._get_resp.assert_called_once_with(
            "test-model",
            chat._history["test-model"],
            {},
            {"plugins": plugins},
            raw=True,
            tools=None,
        )


def test_chat_with_audio():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Audio transcription response"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 15
    mock_response.usage.completion_tokens = 10
    mock_response.usage.total_tokens = 25

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)

        # Mock the construct_user_message method for audio content
        def mock_construct_user_message(message):
            if isinstance(message, list):
                return {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": "base64audio",
                                "format": "mp3",
                            },
                        },
                        {"type": "text", "text": "Transcribe this"},
                    ],
                }
            return {"role": "user", "content": message}

        mock_call.construct_user_message = Mock(side_effect=mock_construct_user_message)
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        result = chat(["audio.mp3", "Transcribe this"])

        assert result == "Audio transcription response"

        # Test that audio content is properly tracked in history
        assert len(chat.history) == 3  # system + user + assistant

        user_message = chat.history[1]
        assert user_message["role"] == "user"
        assert isinstance(user_message["content"], list)
        assert user_message["content"][0]["type"] == "input_audio"
        assert user_message["content"][1]["type"] == "text"


def test_chat_with_pdf():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "PDF analysis response"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 20
    mock_response.usage.completion_tokens = 15
    mock_response.usage.total_tokens = 35

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)

        # Mock the construct_user_message method for PDF content
        def mock_construct_user_message(message):
            if isinstance(message, list):
                return {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file": {
                                "filename": "document.pdf",
                                "file_data": "data:application/pdf;base64,base64pdf",
                            },
                        },
                        {"type": "text", "text": "Analyze this document"},
                    ],
                }
            return {"role": "user", "content": message}

        mock_call.construct_user_message = Mock(side_effect=mock_construct_user_message)
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        result = chat(["document.pdf", "Analyze this document"])

        assert result == "PDF analysis response"

        # Test that PDF content is properly tracked in history
        assert len(chat.history) == 3  # system + user + assistant

        user_message = chat.history[1]
        assert user_message["role"] == "user"
        assert isinstance(user_message["content"], list)
        assert user_message["content"][0]["type"] == "file"
        assert user_message["content"][1]["type"] == "text"

        # Test usage tracking still works with PDFs
        assert chat.usage["prompt_tokens"] == 20
        assert chat.usage["completion_tokens"] == 15
        assert chat.usage["total_tokens"] == 35
