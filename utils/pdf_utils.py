from PyPDF2 import PdfReader
import requests
from io import BytesIO

# Function to extract text from a PDF file given a file path or URL
def extract_text_from_pdf(source):
    try:
        # Check if the source is a URL
        if source.startswith('http://') or source.startswith('https://'):
            response = requests.get(source)
            if response.status_code == 200:
                pdf_file = BytesIO(response.content)
            else:
                print(f"Failed to download PDF from {source}")
                return ''
        else:
            # Assume source is a local file path
            if not os.path.isfile(source):
                print(f"File not found: {source}")
                return ''
            pdf_file = open(source, 'rb')
        
        reader = PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
        pdf_file.close()
        return text
    except Exception as e:
        print(f"Error reading PDF from {source}: {e}")
        return ''

# Function to identify the field containing the PDF file path or URL
def find_pdf_field(example):
    for field_name, value in example.items():
        # Check if the value is a string containing '.pdf'
        if isinstance(value, str) and '.pdf' in value.lower():
            return field_name
    return None