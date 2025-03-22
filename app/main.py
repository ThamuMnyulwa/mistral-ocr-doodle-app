import os
from mistralai import Mistral
from loguru import logger as log
import time
from dotenv import load_dotenv
import requests
import base64

load_dotenv()


def encode_file_to_base64(file_path):
    """Encode a file to base64."""
    with open(file_path, "rb") as file:
        content = file.read()
        return (
            f"data:application/pdf;base64,{base64.b64encode(content).decode('utf-8')}"
        )


def ocr_processing(document_input: str, is_url: bool = True) -> dict:
    """
    Process document through OCR.
    Args:
        document_input: Either a URL or a local file path
        is_url: Boolean indicating if the input is a URL (True) or local file path (False)
    """
    log.info("Starting OCR processing")
    if document_input is None:
        raise ValueError("Document input is required")

    try:
        start = time.time()
        api_key = os.environ["MISTRAL_API_KEY"]
        client = Mistral(api_key=api_key)

        # For local files, first upload them
        if not is_url:
            with open(document_input, "rb") as file:
                uploaded_file = client.files.upload(
                    file={
                        "file_name": os.path.basename(document_input),
                        "content": file,
                    },
                    purpose="ocr",
                )
                # Get signed URL for the uploaded file
                signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
                document_input = signed_url.url

        # Process document using document_url type
        document = {"type": "document_url", "document_url": document_input}

        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document=document,
            include_image_base64=True,
        )

        end = time.time()
        log.success(f"OCR processing time: {end - start} seconds")
        return ocr_response
    except Exception as e:
        log.error(f"Error in OCR processing: {e}")
        raise e


def ocr_markdown_extraction(ocr_response) -> str:
    log.info("Starting OCR Markdown extraction")
    try:
        markdown_output = ""
        # Directly iterate over the pages attribute
        for page in ocr_response.pages:
            markdown_output += page.markdown + "\n\n"
        log.success("OCR Markdown extraction successful")
        return markdown_output
    except Exception as e:
        log.error(f"Error during Markdown extraction: {e}")
        raise e


def main():
    log.info("Hello from mistral-ocr-doodle-app!")

    # Example usage with URL
    document_url = "https://arxiv.org/pdf/2201.04234"
    ocr_response = ocr_processing(document_url, is_url=True)
    markdown_text = ocr_markdown_extraction(ocr_response)

    # Write the complete markdown to a file
    if os.path.exists("ocr_output.md"):
        os.remove("ocr_output.md")

    # Write the markdown to a file
    with open("ocr_output.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)

    log.info(f"\nOCR response: {markdown_text}")


if __name__ == "__main__":
    main()
