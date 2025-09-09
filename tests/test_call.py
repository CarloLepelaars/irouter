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
        mock_detect.side_effect = [
            "image_url",
            "text",
            "local_image",
            "local_audio",
            "local_pdf",
            "pdf_url",
        ]

        result = call.construct_content(
            [
                "https://example.com/image.jpg",
                "What is in the image?",
                "local_image.png",
                "audio.wav",
                "document.pdf",
                "https://example.com/doc.pdf",
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
            {
                "type": "input_audio",
                "input_audio": {
                    "data": "base64data",
                    "format": "wav",
                },
            },
            {
                "type": "file",
                "file": {
                    "filename": "document.pdf",
                    "file_data": "data:application/pdf;base64,base64data",
                },
            },
            {
                "type": "file",
                "file": {
                    "filename": "document.pdf",
                    "file_data": "https://example.com/doc.pdf",
                },
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


def test_call_with_extra_body():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("test-model")
        extra_body = {
            "provider": {"require_parameters": True},
            "transforms": ["middle-out"],
        }
        result = call("Hello", extra_body=extra_body)

        assert result == "Test response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["extra_body"] == extra_body


def test_call_with_kwargs():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("test-model")
        result = call("Hello", temperature=0.7, max_tokens=100)

        assert result == "Test response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["max_tokens"] == 100


def test_call_with_extra_headers():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("test-model")
        extra_headers = {"HTTP-Referer": "https://mysite.com", "X-Title": "My App"}
        result = call("Hello", extra_headers=extra_headers)

        assert result == "Test response"
        call_args = mock_client.chat.completions.create.call_args
        # Verify that extra_headers are merged with BASE_HEADERS
        from irouter.base import BASE_HEADERS

        expected_headers = {**BASE_HEADERS, **extra_headers}
        assert call_args[1]["extra_headers"] == expected_headers


def test_call_with_plugins():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("test-model")
        plugins = [{"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}]
        result = call("Hello", extra_body={"plugins": plugins})

        assert result == "Test response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["extra_body"]["plugins"] == plugins


def test_call_with_audio():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Audio transcription"

    with (
        patch("irouter.call.OpenAI") as mock_openai,
        patch("irouter.call.detect_content_type") as mock_detect,
        patch("irouter.call.encode_base64", return_value="base64audio"),
    ):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        mock_detect.side_effect = ["local_audio", "text"]

        call = Call("test-model")
        result = call(["audio.mp3", "Transcribe this audio"])

        assert result == "Audio transcription"

        # Verify the message structure sent to API
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]

        user_message = messages[0]
        assert user_message["role"] == "user"
        assert len(user_message["content"]) == 2
        assert user_message["content"][0]["type"] == "input_audio"
        assert user_message["content"][0]["input_audio"]["data"] == "base64audio"
        assert user_message["content"][0]["input_audio"]["format"] == "mp3"
        assert user_message["content"][1]["type"] == "text"


def test_call_with_pdf():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "PDF analysis"

    with (
        patch("irouter.call.OpenAI") as mock_openai,
        patch("irouter.call.detect_content_type") as mock_detect,
        patch("irouter.call.encode_base64", return_value="base64pdf"),
    ):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        mock_detect.side_effect = ["local_pdf", "text"]

        call = Call("test-model")
        result = call(["document.pdf", "What are the main points?"])

        assert result == "PDF analysis"

        # Verify the message structure sent to API
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]

        user_message = messages[0]
        assert user_message["role"] == "user"
        assert len(user_message["content"]) == 2
        assert user_message["content"][0]["type"] == "file"
        assert user_message["content"][0]["file"]["filename"] == "document.pdf"
        assert (
            user_message["content"][0]["file"]["file_data"]
            == "data:application/pdf;base64,base64pdf"
        )
        assert user_message["content"][1]["type"] == "text"


def test_call_with_web_online_tag():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Web search response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("openai/gpt-4o:online")
        result = call("What is the latest news about AI?")

        assert result == "Web search response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "openai/gpt-4o:online"


def test_call_with_web_plugin():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Web plugin response"

    with patch("irouter.call.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        call = Call("openai/gpt-4o")
        extra_body = {
            "plugins": [
                {
                    "id": "web",
                    "max_results": 5,
                    "search_prompt": "Only trustworthy sources",
                }
            ]
        }
        result = call("Search for latest AI developments", extra_body=extra_body)

        assert result == "Web plugin response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["extra_body"]["plugins"][0]["id"] == "web"
        assert call_args[1]["extra_body"]["plugins"][0]["max_results"] == 5


def test_call_with_audio_url():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Audio URL transcription"

    with (
        patch("irouter.call.OpenAI") as mock_openai,
        patch("irouter.call.detect_content_type") as mock_detect,
        patch("irouter.call.download_and_encode_url", return_value="base64audiourl"),
    ):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        mock_detect.side_effect = ["audio_url", "text"]

        call = Call("test-model")
        result = call(
            [
                "https://www.bird-sounds.net/birdmedia/241/860.mp3",
                "Transcribe this audio",
            ]
        )

        assert result == "Audio URL transcription"

        # Verify the message structure sent to API
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]

        user_message = messages[0]
        assert user_message["role"] == "user"
        assert len(user_message["content"]) == 2
        assert user_message["content"][0]["type"] == "input_audio"
        assert user_message["content"][0]["input_audio"]["data"] == "base64audiourl"
        assert user_message["content"][0]["input_audio"]["format"] == "mp3"
        assert user_message["content"][1]["type"] == "text"

    # Test with WAV URL
    with (
        patch("irouter.call.OpenAI") as mock_openai,
        patch("irouter.call.detect_content_type") as mock_detect,
        patch("irouter.call.download_and_encode_url", return_value="base64wav"),
    ):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        mock_detect.side_effect = ["audio_url", "text"]

        call = Call("test-model")
        result = call(["https://example.com/audio.wav", "What is said?"])

        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_message = messages[0]
        assert user_message["content"][0]["input_audio"]["format"] == "wav"
