import os
import re
from pathlib import Path

from PyPDF2 import PdfReader

SCRIPT_DIR = Path(__file__).resolve().parent
QUOTES_PATH = SCRIPT_DIR.parent / "resources" / "oenomaus_quotes.txt"


def extract_text_from_pdf(pdf_path):
    """Extract text from a single PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    # deliberately broad: a single unreadable or malformed PDF should be skipped
    # rather than abort the whole directory walk
    except Exception as e:  # noqa: BLE001
        print(f"Error processing {pdf_path}: {e}")
        return ""

def process_pdf_directory(directory_path):
    """Process all PDF files in a directory."""
    all_text = {}
    
    # Walk through directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                
                # Extract text from PDF
                text = extract_text_from_pdf(pdf_path)
                all_text[file] = text
    
    return all_text

def find_character_quotes(text_dict):
    """
    Find sentences following 'OENOMAUS' or 'DOCTORE' in the text.
    Returns a list of tuples containing (character, quote, filename).
    """
    quotes = []
    
    # Regex pattern to find OENOMAUS/DOCTORE and the following sentence
    pattern = r'(OENOMAUS|DOCTORE)\s*(?:\(.*?\))?\s*([^.!?]*[.!?])'
    
    for text in text_dict.values():
        # Find all matches in the text
        matches = re.finditer(pattern, text)

        for match in matches:
            quote = match.group(2).strip()  # The sentence following the character name

            if quote:

                # check if there are any words with full capital letters
                if any(word.isupper() for word in quote.split()):
                    continue

                # if there is a '(', take all characters after the '('
                if '(' in quote:
                    quote = quote.split('(')[1].strip()

                if ')' in quote:
                    quote = quote.split(')')[0].strip()

                # only add if there is more than a few characters
                if len(quote) < 5:
                    continue

                # only add if starts with a capital letter
                if not quote[0].isupper():
                    continue

                # don't add if it begins with ’ or ,
                if quote.startswith(("’", ",")):
                    continue

                quotes.append(quote.replace("\n", ""))
    
    return quotes

if __name__ == "__main__":
    # Process all PDFs
    extracted_texts = process_pdf_directory(SCRIPT_DIR)

    # Find character quotes
    quotes = find_character_quotes(extracted_texts)

    # save quotes to a file
    with open(QUOTES_PATH, "w") as f:
        f.writelines(quote + "\n" for quote in quotes)
