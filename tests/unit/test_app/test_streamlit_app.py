import pytest
from unittest.mock import patch, Mock, mock_open
import streamlit as st
import tempfile
import os
from io import BytesIO


# Mock the entire streamlit module
@pytest.fixture(autouse=True)
def mock_streamlit():
    with (
        patch("streamlit.set_page_config"),
        patch("streamlit.title"),
        patch("streamlit.markdown"),
        patch("streamlit.radio", return_value="Browser Input"),
        patch("streamlit.container"),
        patch("streamlit.text_area"),
        patch("streamlit.button"),
        patch("streamlit.spinner"),
        patch("streamlit.error"),
        patch("streamlit.success"),
        patch("streamlit.warning"),
        patch("streamlit.file_uploader"),
        patch("streamlit.columns", return_value=[Mock(), Mock()]),
        patch("streamlit.session_state", {}),
    ):
        yield


@pytest.fixture
def mock_ocr_functions():
    with (
        patch("app.streamlit_app.ocr_processing") as mock_process,
        patch("app.streamlit_app.ocr_markdown_extraction") as mock_extract,
    ):
        mock_process.return_value = Mock()
        mock_extract.return_value = "Converted markdown"
        yield mock_process, mock_extract


def test_browser_input_processing(mock_ocr_functions):
    mock_process, mock_extract = mock_ocr_functions

    # Mock the temporary file
    mock_temp = Mock()
    mock_temp.name = "temp.txt"

    with (
        patch("tempfile.NamedTemporaryFile", return_value=mock_temp),
        patch("os.unlink"),
    ):

        # Simulate browser input processing
        st.session_state.input_method = "Browser Input"
        st.text_area.return_value = "Test input"
        st.button.return_value = True  # Simulate button click

        # Import and run the streamlit app
        import app.streamlit_app

        # Verify OCR processing was called correctly
        mock_process.assert_called_once()
        mock_extract.assert_called_once()
        assert st.session_state.get("converted_text") == "Converted markdown"


def test_pdf_upload_processing(mock_ocr_functions):
    mock_process, mock_extract = mock_ocr_functions

    # Mock PDF file
    mock_pdf = Mock()
    mock_pdf.name = "test.pdf"
    mock_pdf.read.return_value = b"PDF content"

    # Mock the temporary file
    mock_temp = Mock()
    mock_temp.name = "temp.pdf"

    with (
        patch("tempfile.NamedTemporaryFile", return_value=mock_temp),
        patch("os.unlink"),
    ):

        # Simulate PDF upload processing
        st.session_state.input_method = "PDF Upload"
        st.file_uploader.return_value = [mock_pdf]
        st.button.return_value = True  # Simulate button click

        # Import and run the streamlit app
        import app.streamlit_app

        # Verify OCR processing was called correctly
        mock_process.assert_called_once()
        mock_extract.assert_called_once()
        assert "test.pdf" in st.session_state.get("converted_text", "")


def test_error_handling(mock_ocr_functions):
    mock_process, _ = mock_ocr_functions
    mock_process.side_effect = Exception("Test error")

    # Mock the temporary file
    mock_temp = Mock()
    mock_temp.name = "temp.txt"

    with (
        patch("tempfile.NamedTemporaryFile", return_value=mock_temp),
        patch("os.unlink"),
    ):

        # Simulate browser input processing with error
        st.session_state.input_method = "Browser Input"
        st.text_area.return_value = "Test input"
        st.button.return_value = True  # Simulate button click

        # Import and run the streamlit app
        import app.streamlit_app

        # Verify error was displayed
        st.error.assert_called_with("Error converting text: Test error")


def test_clipboard_operations():
    with patch("pyperclip.copy") as mock_copy:
        # Simulate successful copy
        mock_copy.return_value = None
        st.session_state.converted_text = "Test content"
        st.button.return_value = True  # Simulate copy button click

        # Import and run the streamlit app
        import app.streamlit_app

        # Verify copy operation
        mock_copy.assert_called_once_with("Test content")
        st.success.assert_called_with("Copied to clipboard!")

        # Simulate copy failure
        mock_copy.side_effect = Exception("Copy failed")

        # Import and run the streamlit app again
        import app.streamlit_app

        # Verify error handling
        st.error.assert_called_with(
            "Failed to copy to clipboard. Please copy manually."
        )
