

import PyPDF2
import logging
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path):
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n\n"
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def process_all_pdfs(self, pdf_paths):
       
        results = {}
    
        for pdf_path in tqdm(pdf_paths, desc="Extracting text from PDFs"):
            text = self.extract_text_from_pdf(pdf_path)
            
            if text:
                results[pdf_path] = text
            else:
                logger.warning(f"No t text extracted from {pdf_path}")
        
    
        return results
    
    def chunk_text(self, text, chunk_size=1000, overlap=200):
      
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk:
                chunks.append(chunk)
            
            start += chunk_size - overlap
        
        return chunks