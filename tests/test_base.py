from unittest.mock import patch
from irouter.base import get_all_models, history_to_markdown, nb_markdown


def test_get_all_models():
    mock_data = {
        "data": [
            {"canonical_slug": "my_provider/model1", "name": "Model One"},
            {"canonical_slug": "my_provider/model2", "name": "Model Two"},
        ]
    }

    with patch("irouter.base.urljson", return_value=mock_data):
        slugs = get_all_models(slug=True)
        names = get_all_models(slug=False)

        assert slugs == ["my_provider/model1", "my_provider/model2"]
        assert names == ["Model One", "Model Two"]


def test_history_to_markdown():
    history = {
        "test_model": [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    }

    expected = (
        "**System:** You are helpful\n\n**User:** Hello\n\n**Assistant:** Hi there!"
    )
    result = history_to_markdown(history, ipython=False)
    assert result == expected

    with patch("irouter.base.display") as mock_display:
        nb_markdown("test")
        mock_display.assert_called_once()
