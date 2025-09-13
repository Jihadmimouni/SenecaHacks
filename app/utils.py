"""
Utility functions for processing health data, creating embeddings, and managing RAG operations.
"""

import json
import os
from typing import List, Dict, Optional

import pandas as pd
import orjson
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import faiss
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from .embeddings import get_embedding

def load_and_process_data(data_dir: str = "./data") -> List[Document]:
    """
    Load and process all data files from JSON, CSV, and FitBit datasets.
    
    Args:
        data_dir (str): Directory containing the data directories
        
    Returns:
        List[Document]: List of processed documents with metadata
    """
    # Initialize storage for all user data
    user_data = {}
    
    # Define dataset structures
    datasets = {
        'small': [
            'fitness-activities.json',
            'fitness-nutrition.json',
            'fitness-sleep.json',
            'fitness-users.json'
        ],
        'medium': [
            'fitness-activities.json',
            'fitness-measurements.json',
            'fitness-users.json',
            'fitness-workouts.json'
        ],
        'large': [
            'activities.json',
            'heart_rate.json',
            'measurements.json',
            'nutrition.json',
            'sleep.json',
            'users.json',
            'workouts.json'
        ]
    }
    
    # Load JSON files from each dataset
    for dataset_size, files in datasets.items():
        dataset_dir = os.path.join(data_dir, dataset_size)
        for file in files:
            file_path = os.path.join(dataset_dir, file)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    # Use orjson for faster JSON parsing
                    data = orjson.loads(f.read())
                    for user_id, user_info in data.items():
                        if user_id not in user_data:
                            user_data[user_id] = {}
                        # Add dataset source to help track data origin
                        user_info['data_source'] = f"{dataset_size}/{file}"
                        user_data[user_id].update(user_info)
    
    # Load nutrition CSV data if available
    nutrition_csv = os.path.join(data_dir, 'extra', 'nutrition-data.csv')
    if os.path.exists(nutrition_csv):
        df = pd.read_csv(nutrition_csv)
        for _, row in df.iterrows():
            user_id = str(row['user_id'])
            if user_id not in user_data:
                user_data[user_id] = {}
            nutrition_data = row.to_dict()
            nutrition_data['data_source'] = 'extra/nutrition-data.csv'
            user_data[user_id].update(nutrition_data)
    
    # Load FitBit data
    fitbit_dir = os.path.join(data_dir, 'extra', 'FitBit Fitness Tracker Data')
    fitbit_files = [
        'dailyActivity_merged.csv',
        'heartrate_seconds_merged.csv',
        'hourlyCalories_merged.csv',
        'hourlyIntensities_merged.csv',
        'hourlySteps_merged.csv',
        'minuteCaloriesNarrow_merged.csv'
    ]
    
    for file in fitbit_files:
        file_path = os.path.join(fitbit_dir, 'Fitabase Data 3.12.16-4.11.16', file)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Convert 'Id' to user_id if present
            if 'Id' in df.columns:
                df['user_id'] = df['Id'].astype(str)
            
            # Group by user_id and aggregate data
            grouped = df.groupby('user_id').agg({
                'Calories': 'mean' if 'Calories' in df.columns else None,
                'Steps': 'sum' if 'Steps' in df.columns else None,
                'Value': 'mean' if 'Value' in df.columns else None,
                'HeartRate': 'mean' if 'HeartRate' in df.columns else None,
                'Intensity': 'mean' if 'Intensity' in df.columns else None
            }).dropna(axis=1, how='all')
            
            for user_id, row in grouped.iterrows():
                if user_id not in user_data:
                    user_data[user_id] = {}
                fitbit_data = row.to_dict()
                fitbit_data['data_source'] = f'fitbit/{file}'
                user_data[user_id].update(fitbit_data)
    
    # Create documents with metadata
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    for user_id, data in user_data.items():
        # Calculate fitness level based on available metrics
        fitness_level = calculate_fitness_level(data)
        # Extract or determine user goals
        goals = determine_user_goals(data)
        # Calculate BMI if height and weight are available
        bmi = calculate_bmi(data)
        
        # Create a comprehensive health summary
        content = create_health_summary(data)
        
        # Split content into chunks
        chunks = text_splitter.split_text(content)
        
        # Create Document objects for each chunk
        for chunk in chunks:
            doc = Document(
                page_content=chunk,
                metadata={
                    'user_id': user_id,
                    'fitness_level': fitness_level,
                    'goal': goals,
                    'bmi': bmi
                }
            )
            documents.append(doc)
    
    return documents

def create_vector_store(documents: List[Document], index_path: str = "faiss_index") -> faiss.Index:
    """
    Create a FAISS vector store from documents.
    
    Args:
        documents (List[Document]): List of documents to index
        index_path (str): Path to save the FAISS index
        
    Returns:
        faiss.Index: FAISS index for vector similarity search
    """
    # Get embeddings for all documents
    embeddings = []
    for doc in documents:
        embedding = get_embedding(doc.page_content)
        embeddings.append(embedding)
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings).astype('float32')
    
    # Create FAISS index
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to the index
    index.add(embeddings_array)
    
    # Save index for later use
    faiss.write_index(index, index_path)
    
    return index

def generate_hypothetical_document(question: str) -> str:
    """
    Generate a hypothetical document using OpenAI API to answer a question.
    
    Args:
        question (str): The question to generate a document for
        
    Returns:
        str: Generated hypothetical document
    """
    client = OpenAI()
    
    prompt = f"""Generate a detailed, factual document that could answer this question: {question}
    The document should be written in a formal, objective style and include relevant details
    that would be found in a health and fitness dataset. Focus on quantitative metrics
    and specific health indicators."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a health data analyst creating objective, data-focused documents."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def self_rag_prompt(question: str, retrieved_docs: List[Document]) -> Dict:
    """
    Create a self-reflective RAG prompt and evaluate the response quality.
    
    Args:
        question (str): User's question
        retrieved_docs (List[Document]): Retrieved relevant documents
        
    Returns:
        Dict: Response with self-evaluation metrics
    """
    # Combine document contents with metadata
    context = "\n\n".join([
        f"Document {i+1}:\n{doc.page_content}\nMetadata: {doc.metadata}"
        for i, doc in enumerate(retrieved_docs)
    ])
    
    client = OpenAI()
    
    prompt = f"""Analyze the following question and context, then provide a detailed evaluation:

    Context:
    {context}

    Question: {question}

    Please provide:
    1. Do we need additional information retrieval? (Yes/No)
    2. Is the available information sufficient? (Yes/No)
    3. Would answering require any speculation? (Yes/No)
    4. Based on the above, provide a precise answer using ONLY the given information.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a precise analytical assistant that only uses provided information."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    # Parse response to extract evaluation metrics
    answer = response.choices[0].message.content
    
    # Extract yes/no answers
    needs_retrieval = "yes" in answer.lower().split("\n")[0].lower()
    sufficient_info = "yes" in answer.lower().split("\n")[1].lower()
    has_hallucination = "yes" in answer.lower().split("\n")[2].lower()
    
    return {
        "needs_retrieval": needs_retrieval,
        "sufficient_info": sufficient_info,
        "has_hallucination": has_hallucination,
        "answer": answer.split("\n")[-1]  # Get the final answer
    }

# Helper functions

def calculate_fitness_level(data: Dict) -> str:
    """
    Calculate fitness level based on various health metrics including:
    - Daily steps
    - Activity intensity
    - Heart rate patterns
    - Calories burned
    """
    scores = []
    
    # Score based on daily steps (if available)
    if 'Steps' in data:
        steps = float(data['Steps'])
        if steps >= 10000:  # Active
            scores.append(8)
        elif steps >= 7500:  # Moderately active
            scores.append(6)
        elif steps >= 5000:  # Lightly active
            scores.append(4)
        else:  # Sedentary
            scores.append(2)
    
    # Score based on activity intensity (if available)
    if 'Intensity' in data:
        intensity = float(data['Intensity'])
        scores.append(min(10, intensity * 2))  # Scale intensity to 0-10
    
    # Score based on heart rate patterns (if available)
    if 'HeartRate' in data:
        heart_rate = float(data['HeartRate'])
        if 60 <= heart_rate <= 100:  # Healthy resting heart rate
            scores.append(7)
        else:
            scores.append(4)
    
    # Score based on calories burned (if available)
    if 'Calories' in data:
        calories = float(data['Calories'])
        if calories >= 2500:
            scores.append(8)
        elif calories >= 2000:
            scores.append(6)
        elif calories >= 1500:
            scores.append(4)
        else:
            scores.append(2)
    
    # Use traditional metrics if available
    traditional_metrics = {
        'activity_score': data.get('activity_score'),
        'endurance_level': data.get('endurance_level'),
        'strength_score': data.get('strength_score')
    }
    
    for value in traditional_metrics.values():
        if value is not None:
            scores.append(float(value))
    
    # Calculate average score
    if not scores:  # If no metrics available
        return "unknown"
    
    avg_score = sum(scores) / len(scores)
    
    # Determine fitness level
    if avg_score >= 7.5:
        return "advanced"
    elif avg_score >= 5:
        return "intermediate"
    else:
        return "beginner"

def determine_user_goals(data: Dict) -> List[str]:
    """Determine user goals based on available data."""
    goals = []
    
    if data.get('endurance_focus', False):
        goals.append('endurance')
    if data.get('flexibility_focus', False):
        goals.append('flexibility')
    if data.get('strength_focus', False):
        goals.append('strength')
        
    return goals or ['general_fitness']  # Default if no specific goals found

def calculate_bmi(data: Dict) -> Optional[float]:
    """Calculate BMI if height and weight are available."""
    height = data.get('height')  # Expected in meters
    weight = data.get('weight')  # Expected in kg
    
    if height and weight and height > 0:
        bmi = weight / (height ** 2)
        return round(bmi, 1)
    return None

def create_health_summary(data: Dict) -> str:
    """Create a comprehensive health summary from user data."""
    summary_parts = []
    
    # Add basic information
    if 'age' in data:
        summary_parts.append(f"Age: {data['age']} years")
    if 'gender' in data:
        summary_parts.append(f"Gender: {data['gender']}")
    
    # Add physical metrics
    metrics = {
        'weight': 'kg',
        'height': 'm',
        'blood_pressure': 'mmHg',
        'heart_rate': 'bpm',
        'sleep_quality': '%'
    }
    for metric, unit in metrics.items():
        if metric in data:
            summary_parts.append(f"{metric.replace('_', ' ').title()}: {data[metric]} {unit}")
    
    # Add FitBit metrics
    fitbit_metrics = {
        'Calories': 'daily average calories',
        'Steps': 'total steps',
        'HeartRate': 'average heart rate (bpm)',
        'Intensity': 'average activity intensity'
    }
    for metric, label in fitbit_metrics.items():
        if metric in data:
            summary_parts.append(f"{label.title()}: {data[metric]:.1f}")
    
    # Add activity data
    if 'activity_data' in data:
        summary_parts.append("\nActivity Data:")
        for activity, value in data['activity_data'].items():
            summary_parts.append(f"- {activity}: {value}")
    
    # Add nutrition data if available
    nutrition_metrics = [
        'calories_intake',
        'protein_g',
        'carbs_g',
        'fat_g',
        'sugar_g',
        'fiber_g'
    ]
    has_nutrition = any(metric in data for metric in nutrition_metrics)
    if has_nutrition:
        summary_parts.append("\nNutrition Data:")
        for metric in nutrition_metrics:
            if metric in data:
                label = metric.replace('_', ' ').replace('g', ' grams')
                summary_parts.append(f"- {label.title()}: {data[metric]}")
    
    # Add data source for transparency
    if 'data_source' in data:
        summary_parts.append(f"\nSource: {data['data_source']}")
            
    return "\n".join(summary_parts)
