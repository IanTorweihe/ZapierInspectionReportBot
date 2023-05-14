import requests
from io import BytesIO
import pypdf

def extract_pdf_txt(url):
    """
    Extracts text from a PDF file from a given URL using pypdf library.

    Args:
        url (str): The URL of the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # raise an error if the request was unsuccessful

        with BytesIO(response.content) as pdf_bytes:
            pdf_reader = pypdf.PdfReader(pdf_bytes)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            #print(text)
            return text #return extracted text

    except requests.exceptions.RequestException:
        return "Error downloading PDF in pdf_parser.py."   
