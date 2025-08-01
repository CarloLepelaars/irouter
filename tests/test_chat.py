from unittest.mock import patch, MagicMock, Mock
from irouter.chat import Chat


def test_response():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Chat response"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    
    with patch('irouter.chat.Call') as mock_call_class:
        mock_call = MagicMock()
        mock_call._get_resp = Mock(return_value=mock_response)
        mock_call_class.return_value = mock_call
        
        chat = Chat("test-model", system="Test system")
        
        assert chat.system == "Test system"
        assert "test-model" in chat.history
        assert chat.history["test-model"][0]["role"] == "system"
        assert chat.history["test-model"][0]["content"] == "Test system"
        
        result = chat("Hello")
        assert result == "Chat response"
        
        # Test history tracking
        assert len(chat.history["test-model"]) == 3
        assert chat.history["test-model"][1]["role"] == "user"
        assert chat.history["test-model"][1]["content"] == "Hello"
        assert chat.history["test-model"][2]["role"] == "assistant"
        assert chat.history["test-model"][2]["content"] == "Chat response"
        
        # Test usage tracking
        assert chat.usage["test-model"]["prompt_tokens"] == 10
        assert chat.usage["test-model"]["completion_tokens"] == 5
        assert chat.usage["test-model"]["total_tokens"] == 15
        
        # multiple LLMs
        multi_chat = Chat(["model1", "model2"])
        multi_result = multi_chat("Hello")
        assert isinstance(multi_result, list)
        assert len(multi_result) == 2