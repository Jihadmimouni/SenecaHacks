"""
FastAPI application for health data RAG system.
Supports HyDE and Self-RAG for improved response quality.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import faiss

from .utils import (
    load_and_process_data,
    create_vector_store,
    generate_hypothetical_document,
    self_rag_prompt
)
from .embeddings import get_embedding

# Load environment variables
load_dotenv()

# Validate API keys
if bool(os.getenv("OPENAI_API_KEY")) == bool(os.getenv("PERPLEXITY_API_KEY")):
    raise ValueError("Exactly one of OPENAI_API_KEY or PERPLEXITY_API_KEY must be set")

# Initialize FastAPI app
app = FastAPI(
    title="Health RAG API",
    description="RAG system for health data with HyDE and Self-RAG support",
    version="1.0.0"
)

# Initialize data and vector store on startup
@app.on_event("startup")
async def startup_event():
    global documents, vector_store
    
    # Load and process documents
    documents = load_and_process_data()
    
    # Create vector store
    vector_store = create_vector_store(documents)

# Input model for questions
class QuestionInput(BaseModel):
    question: str
    use_hyde: bool = False
    use_self_rag: bool = True
    fitness_level: Optional[str] = None
    goal: Optional[str] = None

# Response model
class RAGResponse(BaseModel):
    answer: str
    source_documents: List[dict]
    self_rag_evaluation: Optional[dict] = None

@app.post("/ask", response_model=RAGResponse)
async def ask_question(input_data: QuestionInput):
    """
    Process a question using RAG with optional HyDE and Self-RAG.
    
    Args:
        input_data (QuestionInput): Question and processing options
    
    Returns:
        RAGResponse: Answer, source documents, and evaluation metrics
    """
    try:
        # Generate hypothetical document if HyDE is enabled
        if input_data.use_hyde:
            hyde_doc = generate_hypothetical_document(input_data.question)
            query_text = hyde_doc
        else:
            query_text = input_data.question
        
        # Get query embedding
        query_embedding = get_embedding(query_text)
        
        # Search in FAISS
        D, I = vector_store.search(query_embedding.reshape(1, -1), k=5)
        
        # Get relevant documents
        retrieved_docs = [documents[i] for i in I[0]]
        
        # Filter by metadata if specified
        if input_data.fitness_level or input_data.goal:
            retrieved_docs = [
                doc for doc in retrieved_docs
                if (not input_data.fitness_level or doc.metadata['fitness_level'] == input_data.fitness_level)
                and (not input_data.goal or input_data.goal in doc.metadata['goal'])
            ]
        
        # Process with Self-RAG if enabled
        if input_data.use_self_rag:
            rag_result = self_rag_prompt(input_data.question, retrieved_docs)
            answer = rag_result['answer']
            self_rag_evaluation = {
                'needs_retrieval': rag_result['needs_retrieval'],
                'sufficient_info': rag_result['sufficient_info'],
                'has_hallucination': rag_result['has_hallucination']
            }
        else:
            # Use simple completion if Self-RAG is disabled
            from openai import OpenAI
            client = OpenAI()
            
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a health analysis assistant. Answer based only on the provided information."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {input_data.question}"}
                ],
                temperature=0.2
            )
            answer = response.choices[0].message.content
            self_rag_evaluation = None
        
        # Prepare source documents for response
        source_docs = [
            {
                'user_id': doc.metadata['user_id'],
                'fitness_level': doc.metadata['fitness_level'],
                'bmi': doc.metadata['bmi'],
                'content': doc.page_content[:200] + "..."  # Truncate for brevity
            }
            for doc in retrieved_docs
        ]
        
        return RAGResponse(
            answer=answer,
            source_documents=source_docs,
            self_rag_evaluation=self_rag_evaluation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Check the health status of the API.
    """
    return {
        "status": "healthy",
        "vector_store": "initialized" if 'vector_store' in globals() else "not_initialized",
        "documents_loaded": "yes" if 'documents' in globals() else "no"
    }
