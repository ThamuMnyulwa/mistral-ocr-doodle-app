import pytest
from unittest.mock import patch, Mock, mock_open
import os
import base64
from app.main import ocr_processing, ocr_markdown_extraction, encode_file_to_base64


# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
        yield


@pytest.fixture
def mock_mistral_client():
    with patch("app.main.Mistral") as mock_client:
        instance = mock_client.return_value
        instance.ocr.process.return_value = Mock(
            pages=[Mock(markdown="Test markdown 1"), Mock(markdown="Test markdown 2")]
        )
        yield instance


def test_encode_file_to_base64():
    test_content = b"test content"
    expected_b64 = base64.b64encode(test_content).decode("utf-8")

    with patch("builtins.open", mock_open(read_data=test_content)):
        result = encode_file_to_base64("test.pdf")
        assert result == expected_b64


def test_ocr_processing_with_url(mock_mistral_client):
    # Test URL processing
    result = ocr_processing("https://example.com/test.pdf", is_url=True)

    # Verify the correct document format was used
    mock_mistral_client.ocr.process.assert_called_once_with(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": "https://example.com/test.pdf",
        },
        include_image_base64=True,
    )

    assert result == mock_mistral_client.ocr.process.return_value


def test_ocr_processing_with_local_file(mock_mistral_client):
    test_content = b"test content"
    expected_b64 = base64.b64encode(test_content).decode("utf-8")

    with patch("builtins.open", mock_open(read_data=test_content)):
        result = ocr_processing("test.pdf", is_url=False)

    # Verify the correct document format was used
    mock_mistral_client.ocr.process.assert_called_once_with(
        model="mistral-ocr-latest",
        document={"type": "document_base64", "document_base64": expected_b64},
        include_image_base64=True,
    )

    assert result == mock_mistral_client.ocr.process.return_value


def test_ocr_processing_with_none_input():
    with pytest.raises(ValueError, match="Document input is required"):
        ocr_processing(None)


def test_ocr_markdown_extraction():
    mock_response = Mock()
    mock_response.pages = [
        Mock(markdown="Test markdown 1"),
        Mock(markdown="Test markdown 2"),
    ]

    result = ocr_markdown_extraction(mock_response)
    expected = "Test markdown 1\n\nTest markdown 2\n\n"

    assert result == expected


def test_ocr_markdown_extraction_empty():
    mock_response = Mock()
    mock_response.pages = []

    result = ocr_markdown_extraction(mock_response)
    assert result == ""


def test_ocr_processing_error_handling(mock_mistral_client):
    mock_mistral_client.ocr.process.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        ocr_processing("test.pdf", is_url=False)
