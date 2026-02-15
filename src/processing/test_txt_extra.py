# test_text_extraction
from pdf_processor import PDFProcessor
from pathlib import Path
import json




with open("../../data/raw/metadata.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


successful_docs = [d for d in documents if d.get('download_status') == 'success']
pdf_paths = [d['pdf_path'] for d in successful_docs]



processor = PDFProcessor()
extracted_texts = processor.process_all_pdfs(pdf_paths)


if extracted_texts:
    first_pdf = list(extracted_texts.keys())[0]
    first_text = extracted_texts[first_pdf]
    
   


output_file = Path("../../data/processed/extracted_texts.json")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(extracted_texts, f, ensure_ascii=False, indent=2)
