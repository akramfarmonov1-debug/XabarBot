import PyPDF2
import docx
import pandas as pd
import re
from io import BytesIO

def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return clean_text(text)
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file_content):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return clean_text(text)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_csv(file_content):
    """Extract text from CSV file"""
    try:
        df = pd.read_csv(BytesIO(file_content))
        text = df.to_string(index=False)
        return clean_text(text)
    except Exception as e:
        return f"Error extracting CSV: {str(e)}"

def extract_text_from_txt(file_content):
    """Extract text from TXT file"""
    try:
        text = file_content.decode('utf-8')
        return clean_text(text)
    except UnicodeDecodeError:
        try:
            text = file_content.decode('cp1251')
            return clean_text(text)
        except Exception as e:
            return f"Error extracting TXT: {str(e)}"
    except Exception as e:
        return f"Error extracting TXT: {str(e)}"

def clean_text(text):
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    return text.strip()

def parse_file(file_content, filename):
    """Parse file based on extension and extract text"""
    extension = filename.lower().split('.')[-1]
    
    if extension == 'pdf':
        return extract_text_from_pdf(file_content)
    elif extension == 'docx':
        return extract_text_from_docx(file_content)
    elif extension == 'csv':
        return extract_text_from_csv(file_content)
    elif extension == 'txt':
        return extract_text_from_txt(file_content)
    else:
        return "Unsupported file format"