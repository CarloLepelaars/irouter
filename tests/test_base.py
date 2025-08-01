from unittest.mock import patch, mock_open
from irouter.base import (
    get_all_models,
    history_to_markdown,
    nb_markdown,
    detect_content_type,
    encode_base64,
)


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


def test_detect_content_type():
    # Test image URLs
    assert detect_content_type("https://example.com/image.jpg") == "image_url"
    assert detect_content_type("http://example.com/photo.jpeg") == "image_url"
    assert detect_content_type("https://site.com/pic.png") == "image_url"
    assert detect_content_type("https://test.com/img.webp") == "image_url"

    # Test non-image URLs
    assert detect_content_type("https://example.com/page.html") == "text"
    assert detect_content_type("https://example.com/doc.pdf") == "pdf_url"

    # Test local images (mock file existence)
    with patch("irouter.base.Path.exists", return_value=True):
        assert detect_content_type("local_image.jpg") == "local_image"
        assert detect_content_type("./folder/pic.png") == "local_image"
        assert detect_content_type("/path/to/image.webp") == "local_image"

    # Test non-existent local files
    with patch("irouter.base.Path.exists", return_value=False):
        assert detect_content_type("nonexistent.jpg") == "text"
        assert detect_content_type("missing.png") == "text"
        assert detect_content_type("missing.pdf") == "local_pdf"

    # Test text content
    assert detect_content_type("Hello world") == "text"
    assert detect_content_type("What is in the image?") == "text"
    assert detect_content_type("") == "text"

    # Test non-string input
    assert detect_content_type(123) == "text"
    assert detect_content_type(None) == "text"


def test_encode_base64():
    mock_file_content = b"fake image data"
    expected_base64 = "ZmFrZSBpbWFnZSBkYXRh"  # base64 of "fake image data"

    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        result = encode_base64("test_image.jpg")
        assert result == expected_base64
