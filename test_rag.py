from rag_agent import GeorgianTaxRAGAgent
import os


api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    exit(1)


agent = GeorgianTaxRAGAgent(api_key)

test_questions = [
    "რა არის დღგ?",
    "როგორ ხდება დავების განხილვა?",
    "რა არის საგადასახადო შემოწმება?",
]



for i, question in enumerate(test_questions, 1):  
    result = agent.answer_question(question) 
   
    for source in set(result['sources']):
        print(f"  - {source}")
    
  


