from unittest.mock import patch, MagicMock, Mock
from irouter.chat import Chat
from irouter.base import BASE_URL, TOOL_LOOP_FINAL_PROMPT


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
        mock_call.construct_user_message.assert_called_once_with(message="test message")


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


def test_call_with_tools_single_step():
    """Test __call__ with tools that complete in one step"""

    def dummy_tool(x: int) -> int:
        """Add 1 to x"""
        return x + 1

    # Mock responses - first with tool call, second without
    mock_response1 = MagicMock()
    mock_response1.choices = [MagicMock()]
    mock_response1.choices[0].message.content = ""
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_1"
    mock_tool_call.type = "function"
    mock_tool_call.function.name = "dummy_tool"
    mock_tool_call.function.arguments = '{"x": 5}'
    mock_response1.choices[0].message.tool_calls = [mock_tool_call]
    mock_response1.usage = MagicMock()
    mock_response1.usage.prompt_tokens = 10
    mock_response1.usage.completion_tokens = 5
    mock_response1.usage.total_tokens = 15

    mock_response2 = MagicMock()
    mock_response2.choices = [MagicMock()]
    mock_response2.choices[0].message.content = "The result is 6"
    mock_response2.choices[0].message.tool_calls = None
    mock_response2.usage = MagicMock()
    mock_response2.usage.prompt_tokens = 15
    mock_response2.usage.completion_tokens = 8
    mock_response2.usage.total_tokens = 23

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        # Need 2 responses: first call with tool_calls, final call without tool_calls
        mock_call._get_resp = Mock(side_effect=[mock_response1, mock_response2])
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Add 1 to 5"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        response = chat("Add 1 to 5", tools=[dummy_tool])

        # Should get the final response content
        assert response == "The result is 6"
        assert chat.usage["total_tokens"] == 38  # 15 + 23

        # Check history includes tool results
        history = chat.history
        assert len(history) >= 5  # system, user, assistant, tool_result, assistant
        assert history[-1]["content"] == "The result is 6"


def test_call_with_tools_multiple_steps():
    """Test __call__ with multiple rounds of tool calls"""

    def dummy_tool(x: int) -> int:
        """Add 1 to x"""
        return x + 1

    # Mock responses - multiple tool calls
    mock_response1 = MagicMock()
    mock_response1.choices = [MagicMock()]
    mock_response1.choices[0].message.content = ""
    mock_tool_call1 = MagicMock()
    mock_tool_call1.id = "call_1"
    mock_tool_call1.type = "function"
    mock_tool_call1.function.name = "dummy_tool"
    mock_tool_call1.function.arguments = '{"x": 5}'
    mock_response1.choices[0].message.tool_calls = [mock_tool_call1]
    mock_response1.usage = MagicMock()
    mock_response1.usage.prompt_tokens = 10
    mock_response1.usage.completion_tokens = 5
    mock_response1.usage.total_tokens = 15

    mock_response2 = MagicMock()
    mock_response2.choices = [MagicMock()]
    mock_response2.choices[0].message.content = ""
    mock_tool_call2 = MagicMock()
    mock_tool_call2.id = "call_2"
    mock_tool_call2.type = "function"
    mock_tool_call2.function.name = "dummy_tool"
    mock_tool_call2.function.arguments = '{"x": 6}'
    mock_response2.choices[0].message.tool_calls = [mock_tool_call2]
    mock_response2.usage = MagicMock()
    mock_response2.usage.prompt_tokens = 15
    mock_response2.usage.completion_tokens = 8
    mock_response2.usage.total_tokens = 23

    mock_response3 = MagicMock()
    mock_response3.choices = [MagicMock()]
    mock_response3.choices[0].message.content = "Final result is 7"
    mock_response3.choices[0].message.tool_calls = None
    mock_response3.usage = MagicMock()
    mock_response3.usage.prompt_tokens = 20
    mock_response3.usage.completion_tokens = 10
    mock_response3.usage.total_tokens = 30

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        # Need 3 responses: first call with tool_calls, second call with tool_calls, final call without tool_calls
        mock_call._get_resp = Mock(
            side_effect=[mock_response1, mock_response2, mock_response3]
        )
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Add 1 twice to 5"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        response = chat("Add 1 twice to 5", tools=[dummy_tool])

        # Should get the final response content
        assert response == "Final result is 7"
        assert chat.usage["total_tokens"] == 68  # 15 + 23 + 30

        # Verify final message
        history = chat.history
        assert history[-1]["content"] == "Final result is 7"


def test_call_with_tools_max_steps():
    """Test __call__ respects max_steps limit"""

    def dummy_tool(x: int) -> int:
        """Add 1 to x"""
        return x + 1

    def create_mock_response():
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_1"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "dummy_tool"
        mock_tool_call.function.arguments = '{"x": 5}'
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        return mock_response

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(
            side_effect=[create_mock_response() for _ in range(10)]
        )
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Keep adding"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        response = chat("Keep adding", tools=[dummy_tool], max_steps=3)

        assert response == TOOL_LOOP_FINAL_PROMPT
        assert chat.usage["total_tokens"] == 45  # 3 * 15


def test_call_without_tools():
    """Test __call__ without tools behaves like regular chat"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Simple response"
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
        response = chat("Hello")

        assert response == "Simple response"
        assert chat.usage["total_tokens"] == 15

        # Should have normal chat history
        history = chat.history
        assert len(history) == 3  # system, user, assistant
        assert history[-1]["content"] == "Simple response"


def test_call_with_multiround_tools():
    """Test that __call__ now handles multi-round tool calls automatically"""

    def dummy_tool(x: int) -> int:
        """Add 1 to x"""
        return x + 1

    # Mock responses - multiple tool calls that should be handled by __call__
    mock_response1 = MagicMock()
    mock_response1.choices = [MagicMock()]
    mock_response1.choices[0].message.content = ""
    mock_tool_call1 = MagicMock()
    mock_tool_call1.id = "call_1"
    mock_tool_call1.type = "function"
    mock_tool_call1.function.name = "dummy_tool"
    mock_tool_call1.function.arguments = '{"x": 5}'
    mock_response1.choices[0].message.tool_calls = [mock_tool_call1]
    mock_response1.usage = MagicMock()
    mock_response1.usage.prompt_tokens = 10
    mock_response1.usage.completion_tokens = 5
    mock_response1.usage.total_tokens = 15

    mock_response2 = MagicMock()
    mock_response2.choices = [MagicMock()]
    mock_response2.choices[0].message.content = ""
    mock_tool_call2 = MagicMock()
    mock_tool_call2.id = "call_2"
    mock_tool_call2.type = "function"
    mock_tool_call2.function.name = "dummy_tool"
    mock_tool_call2.function.arguments = '{"x": 6}'
    mock_response2.choices[0].message.tool_calls = [mock_tool_call2]
    mock_response2.usage = MagicMock()
    mock_response2.usage.prompt_tokens = 15
    mock_response2.usage.completion_tokens = 8
    mock_response2.usage.total_tokens = 23

    mock_response3 = MagicMock()
    mock_response3.choices = [MagicMock()]
    mock_response3.choices[0].message.content = "Final result is 7"
    mock_response3.choices[0].message.tool_calls = None
    mock_response3.usage = MagicMock()
    mock_response3.usage.prompt_tokens = 20
    mock_response3.usage.completion_tokens = 10
    mock_response3.usage.total_tokens = 30

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        # Need 3 responses: first call with tool_calls, second call with tool_calls, final call without tool_calls
        mock_call._get_resp = Mock(
            side_effect=[mock_response1, mock_response2, mock_response3]
        )
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Add 1 twice to 5"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("test-model")
        # This should now handle multiple tool rounds automatically
        result = chat("Add 1 twice to 5", tools=[dummy_tool])

        assert result == "Final result is 7"

        # Verify the history shows multiple tool executions
        history = chat.history
        # Should have: system, user, assistant (tool call), tool result, assistant (tool call), tool result, assistant (final)
        assert len(history) >= 7
        assert history[-1]["content"] == "Final result is 7"


def test_chat_with_web_online_tag():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Web search response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].message.annotations = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 15
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 35

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "What is the latest AI news?"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("openai/gpt-4o:online")
        result = chat("What is the latest AI news?")

        assert result == "Web search response"
        assert len(chat.web_citations) == 0  # No annotations in this mock


def test_chat_with_web_plugin():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Web plugin response"
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].message.annotations = None
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 12
    mock_response.usage.completion_tokens = 18
    mock_response.usage.total_tokens = 30

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Search for AI developments"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("openai/gpt-4o")
        extra_body = {
            "plugins": [
                {
                    "id": "web",
                    "max_results": 10,
                    "search_prompt": "Only trustworthy sources",
                }
            ]
        }
        result = chat("Search for AI developments", extra_body=extra_body)

        assert result == "Web plugin response"
        assert chat.usage["total_tokens"] == 30


def test_chat_web_citations_tracking():
    # Mock annotation object
    mock_annotation = MagicMock()
    mock_annotation.url_citation = {
        "title": "AI News Article",
        "url": "https://example.com/ai-news",
        "content": "Latest AI developments...",
        "start_index": 10,
        "end_index": 50,
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[
        0
    ].message.content = "Based on recent sources, AI is advancing rapidly."
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].message.annotations = [mock_annotation]
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 20
    mock_response.usage.completion_tokens = 25
    mock_response.usage.total_tokens = 45

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "What's new in AI?"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("openai/gpt-4o:online")
        result = chat("What's new in AI?")

        assert result == "Based on recent sources, AI is advancing rapidly."

        # Test web citations are properly tracked
        assert len(chat.web_citations) == 1
        citation = chat.web_citations[0]
        assert citation["title"] == "AI News Article"
        assert citation["url"] == "https://example.com/ai-news"
        assert citation["content"] == "Latest AI developments..."

        # Test that start_index and end_index are filtered out
        assert "start_index" not in citation
        assert "end_index" not in citation


def test_chat_web_citations_multiple():
    # Mock multiple annotation objects
    mock_annotation1 = MagicMock()
    mock_annotation1.url_citation = {
        "title": "First AI Article",
        "url": "https://example1.com",
        "content": "First content...",
        "start_index": 0,
        "end_index": 20,
    }

    mock_annotation2 = MagicMock()
    mock_annotation2.url_citation = {
        "title": "Second AI Article",
        "url": "https://example2.com",
        "content": "Second content...",
        "start_index": 30,
        "end_index": 60,
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[
        0
    ].message.content = "AI research shows multiple developments."
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].message.annotations = [mock_annotation1, mock_annotation2]
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 25
    mock_response.usage.completion_tokens = 30
    mock_response.usage.total_tokens = 55

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call.construct_user_message = Mock(
            return_value={"role": "user", "content": "Latest AI research?"}
        )
        mock_call_class.return_value = mock_call

        chat = Chat("openai/gpt-4o:online")
        result = chat("Latest AI research?")

        assert result == "AI research shows multiple developments."

        # Test multiple web citations are tracked
        assert len(chat.web_citations) == 2

        citation1 = chat.web_citations[0]
        assert citation1["title"] == "First AI Article"
        assert citation1["url"] == "https://example1.com"

        citation2 = chat.web_citations[1]
        assert citation2["title"] == "Second AI Article"
        assert citation2["url"] == "https://example2.com"


def test_chat_web_citations_accumulate():
    # Test that web citations accumulate across multiple calls
    def create_mock_response(title, url):
        mock_annotation = MagicMock()
        mock_annotation.url_citation = {
            "title": title,
            "url": url,
            "content": "Content...",
            "start_index": 0,
            "end_index": 10,
        }

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = f"Response about {title}"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.annotations = [mock_annotation]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15
        mock_response.usage.total_tokens = 25
        return mock_response

    with patch("irouter.chat.Call") as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(
            side_effect=[
                create_mock_response("Article 1", "https://site1.com"),
                create_mock_response("Article 2", "https://site2.com"),
            ]
        )
        mock_call.construct_user_message = Mock(
            side_effect=[
                {"role": "user", "content": "First query"},
                {"role": "user", "content": "Second query"},
            ]
        )
        mock_call_class.return_value = mock_call

        chat = Chat("openai/gpt-4o:online")

        # First call
        chat("First query")
        assert len(chat.web_citations) == 1
        assert chat.web_citations[0]["title"] == "Article 1"

        # Second call should accumulate citations
        chat("Second query")
        assert len(chat.web_citations) == 2
        assert chat.web_citations[0]["title"] == "Article 1"
        assert chat.web_citations[1]["title"] == "Article 2"
