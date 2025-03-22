import streamlit as st
import os
import tempfile
import zipfile
from io import BytesIO
import validators
import pyperclip
from loguru import logger as log
from main import ocr_processing, ocr_markdown_extraction

# Configure Streamlit page
st.set_page_config(
    page_title="PDF to Markdown Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and description
st.title("PDF to Markdown Converter")
st.markdown(
    """
    Convert PDF documents to Markdown format using Mistral's OCR technology.
    You can either upload PDF files or provide URLs to PDF documents.
    """
)

# Initialize session state
if "converted_files" not in st.session_state:
    st.session_state.converted_files = {}


def process_document(document_input, is_url=True, filename=None):
    """Process a document and store results in session state."""
    try:
        with st.spinner("Processing document..."):
            # Process the document
            ocr_response = ocr_processing(document_input, is_url=is_url)
            markdown_text = ocr_markdown_extraction(ocr_response)

            # Store the result
            key = filename or document_input
            st.session_state.converted_files[key] = markdown_text
            return True
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        log.error(f"Error processing document: {e}")
        return False


def copy_to_clipboard(text):
    """Copy text to clipboard with error handling."""
    try:
        pyperclip.copy(text)
        st.success("Copied to clipboard!")
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {str(e)}")


# Input method selection
input_method = st.radio("Choose input method:", ["Upload PDF files", "Enter PDF URLs"])

if input_method == "Upload PDF files":
    uploaded_files = st.file_uploader(
        "Upload PDF files", type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Process the file
            if process_document(tmp_path, is_url=False, filename=uploaded_file.name):
                os.unlink(tmp_path)  # Clean up temp file

else:  # URL input
    url_input = st.text_area("Enter PDF URLs (one per line)")
    if url_input:
        urls = [url.strip() for url in url_input.split("\n") if url.strip()]
        for url in urls:
            if validators.url(url):
                process_document(url, is_url=True)
            else:
                st.error(f"Invalid URL: {url}")

# Display results
if st.session_state.converted_files:
    st.markdown("### Converted Documents")

    # Create tabs for each document
    tabs = st.tabs(list(st.session_state.converted_files.keys()))
    for tab, (filename, content) in zip(tabs, st.session_state.converted_files.items()):
        with tab:
            st.markdown("#### Preview")
            st.text_area(
                "Markdown content", value=content, height=300, key=f"preview_{filename}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy to clipboard", key=f"copy_{filename}"):
                    copy_to_clipboard(content)

            with col2:
                # Download individual file
                if st.download_button(
                    "Download Markdown",
                    content,
                    file_name=f"{os.path.splitext(filename)[0]}.md",
                    mime="text/markdown",
                    key=f"download_{filename}",
                ):
                    st.success(f"Downloaded {filename}")

    # Download all files as ZIP
    if len(st.session_state.converted_files) > 1:
        st.markdown("### Download All Files")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in st.session_state.converted_files.items():
                zip_file.writestr(f"{os.path.splitext(filename)[0]}.md", content)

        if st.download_button(
            "Download All as ZIP",
            zip_buffer.getvalue(),
            file_name="converted_documents.zip",
            mime="application/zip",
        ):
            st.success("Downloaded all files as ZIP")

# Clear results button
if st.session_state.converted_files:
    if st.button("Clear All"):
        st.session_state.converted_files = {}
        st.rerun()
