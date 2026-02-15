import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
import logging
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)


class EmbeddingsBuilder:
    def __init__(self, model_name='paraphrase-multilingual-mpnet-base-v2'):
       
        logger.info(f"მოდელის ჩატვირთვა: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        
        persist_dir = Path("data/vectordb")
        persist_dir.mkdir(parents=True, exist_ok=True)
        
      
        logger.info(f" ChromaDB - განსაზღვრა  : {persist_dir}")
        self.chroma_client = chromadb.PersistentClient(path=str(persist_dir))
        
       
        self.collection = self.chroma_client.get_or_create_collection(
            name="georgian_tax_docs",
            metadata={"description": "Georgian tax and customs documents"}
        )
        
    
    def chunk_text(self, text, chunk_size=500, overlap=100):
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start += chunk_size - overlap
        
        return chunks
    
    def build_vector_database(self, extracted_texts_file):
       
        # ტექსტების ჩატვირთვა
        with open(extracted_texts_file, 'r', encoding='utf-8') as f:
            extracted_texts = json.load(f)
        
        
        all_chunks = []
        all_metadata = []
        
        for pdf_path, text in tqdm(extracted_texts.items(), desc="Processing documents"):
            doc_name = Path(pdf_path).name
            chunks = self.chunk_text(text)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'source': doc_name,
                    'source_path': pdf_path,
                    'chunk_id': i,
                    'total_chunks': len(chunks)
                })
        
        
    
        logger.info("ემბედინგის გენერრირება: ")
        embeddings = self.model.encode(all_chunks, show_progress_bar=True, batch_size=32)
        

        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=all_chunks,
            metadatas=all_metadata,
            ids=[f"chunk_{i}" for i in range(len(all_chunks))]
        )
    

        count = self.collection.count()
        logger.info("შენახულია!")
        
        return len(all_chunks)