from anthropic import Anthropic
import chromadb
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class GeorgianTaxRAGAgent:
    def __init__(self, api_key):
      
       
        self.client = Anthropic(api_key=api_key)
        
        self.embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        
       
        self.chroma_client = chromadb.PersistentClient(path="data/vectordb")
        
        self.collection = self.chroma_client.get_collection("georgian_tax_docs")
    
    
    def retrieve_context(self, query, top_k=5):
     
    
        query_embedding = self.embedder.encode([query])[0]
        
    
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        return results
    
    def format_context(self, results):
       
        context = ""
        
        for i in range(len(results['documents'][0])):
            doc_text = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            
            context += f"\n--- დოკუმენტი {i+1} ---\n"
            context += f"წყარო: {metadata['source']}\n"
            context += f"ნაწილი: {metadata['chunk_id'] + 1}/{metadata['total_chunks']}\n"
            context += f"{doc_text}\n"
        
        return context
    
    def answer_question(self, question, max_tokens=2000):
      
        logger.info(f"Question: {question}")
        
        
        results = self.retrieve_context(question, top_k=5)
        context = self.format_context(results)
        
       
        prompt = f"""შენ ხარ ასისტენტი საქართველოს საგადასახადო და საბაჟო ადმინისტრირების თემაზე.

კონტექსტი დოკუმენტებიდან:
{context}

კითხვა: {question}

გთხოვთ უპასუხოთ კითხვას ქართულად და ᲧᲝᲕᲔᲚᲗᲕᲘᲡ მიუთითოთ წყარო. 

მნიშვნელოვანი:
- პასუხი უნდა იყოს ზუსტი და დაფუძნებული მხოლოდ მოწოდებულ დოკუმენტებზე
- თითოეული ფაქტის შემდეგ მიუთითეთ წყარო: [წყარო: დოკუმენტის სახელი]
- თუ პასუხი არ არის დოკუმენტებში, გამოაცხადეთ ეს მკაფიოდ
- პასუხი უნდა იყოს მკაფიო და გასაგები"""
        
        
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.content[0].text
        
        
        
        return {
            'answer': answer,
            'sources': [meta['source'] for meta in results['metadatas'][0]],
            'context_used': len(results['documents'][0])
        }

