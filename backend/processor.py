import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langdetect import detect, DetectorFactory
import os

DetectorFactory.seed = 42

class PDFProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def extract_text(self, pdf_path):
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error extracting text: {e}")
        return text

    def detect_language(self, text):
        try:
            # Use a sample of text for faster detection if it's very long
            sample = text[:2000] if len(text) > 2000 else text
            return detect(sample)
        except:
            return "en"  # Default to English

    def get_chunks(self, text):
        return self.text_splitter.split_text(text)

    def process_pdf(self, pdf_path):
        text = self.extract_text(pdf_path)
        if not text.strip():
            return None, None, None
        
        lang = self.detect_language(text)
        chunks = self.get_chunks(text)
        return text, chunks, lang
