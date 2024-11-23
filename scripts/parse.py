import os
import re
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extract text from a single PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
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
    
    for filename, text in text_dict.items():
        # Find all matches in the text
        matches = re.finditer(pattern, text)
        
        for match in matches:
            character = match.group(1)  # The character name
            quote = match.group(2).strip()  # The following sentence
            
            if quote:  # Only add if there's actual text
                quotes.append(quote.replace("\n", ""))
    
    return quotes

if __name__ == "__main__":
    # Specify your directory containing PDFs
    pdf_directory = "."
    
    # Process all PDFs
    extracted_texts = process_pdf_directory(pdf_directory)

    # Find character quotes
    quotes = find_character_quotes(extracted_texts)

    # save quotes to a file
    with open("oenomaus_quotes.txt", "w") as f:
        for quote in quotes:
            f.write(quote + "\n")
    