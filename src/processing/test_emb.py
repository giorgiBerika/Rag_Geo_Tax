# build_vector_db

from embeddings_builder import EmbeddingsBuilder
from pathlib import Path



builder = EmbeddingsBuilder()


extracted_texts_file = Path("../../data/processed/extracted_texts.json")

if not extracted_texts_file.exists():
    print("შეცდომა")
else:
    total_chunks = builder.build_vector_database(extracted_texts_file)
    
   