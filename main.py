import os
from mistralai import Mistral
from loguru import logger as log
import time
from dotenv import load_dotenv

load_dotenv()


def ocr_processing(document_url: str = None) -> dict:
    log.info("Starting OCR processing")
    if document_url is None:
        raise ValueError("Document URL is required")
    try:
        start = time.time()
        api_key = os.environ["MISTRAL_API_KEY"]
        client = Mistral(api_key=api_key)

        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": document_url,  # Use the parameter here
            },
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

    document = "https://arxiv.org/pdf/2201.04234"
    ocr_response = ocr_processing(document)
    markdown_text = ocr_markdown_extraction(ocr_response)

    # Write the complete markdown to a file
    # check if the file exists
    if os.path.exists("ocr_output.md"):
        os.remove("ocr_output.md")

    # Write the markdown to a file
    with open("ocr_output.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)

    log.info(f"\nOCR response: {markdown_text}")  # Fixed newline character


if __name__ == "__main__":
    main()
