import io
import base64
import os
import json
import numpy as np
from mistralai import Mistral, SystemMessage, UserMessage
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION & INITIALIZATION ---
load_dotenv()

def get_mistral_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables.")
    return Mistral(api_key=api_key)

try:
    VECTOR_STORE_PATH = "data/processed/textbook_vectors.npy"
    METADATA_PATH = "data/processed/textbook_metadata.json"
    
    textbook_vectors = np.load(VECTOR_STORE_PATH)
    with open(METADATA_PATH, "r") as f:
        textbook_metadata = json.load(f)
except FileNotFoundError:
    textbook_vectors = None
    textbook_metadata = None
    print("Warning: Vector store not found. Running without RAG.")

# --- RAG RETRIEVAL FUNCTION ---
def find_relevant_pages(query_text, client, top_k=3):
    if textbook_vectors is None or textbook_metadata is None:
        return []

    try:
        # 1. Embed the query
        response = client.embeddings.create(
            model="mistral-embed",
            inputs=[query_text]
        )
        query_embedding = np.array(response.data[0].embedding).reshape(1, -1)

        # 2. Calculate similarity
        similarities = cosine_similarity(query_embedding, textbook_vectors)[0]

        # 3. Get top_k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_pages = [textbook_metadata[i] for i in top_indices]
        return relevant_pages

    except Exception as e:
        print(f"Error finding relevant pages: {e}")
        return []

# --- CORE TUTORING FUNCTION ---
def get_ai_feedback(image, question_text, client):
    """
    Converts image to base64, finds relevant textbook pages, and fetches Socratic feedback.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 1. Find relevant textbook pages
    query_for_retrieval = f"Question: {question_text}\n\nStudent's attempt: [Image analysis]"
    relevant_pages = find_relevant_pages(query_for_retrieval, client)

    # 2. Build the context for the prompt
    context_str = ""
    if relevant_pages:
        context_str += "\n\n--- RELEVANT TEXTBOOK CONTENT ---\n"
        for page in relevant_pages:
            context_str += f"Page {page['page_number']}:\n"
            context_str += f"Text: {page['text']}\n"
            # We can't display images directly in the text prompt, but we can note their existence.
            if page.get('image_paths'):
                context_str += f"Note: This page also contains {len(page['image_paths'])} image(s).\n\n"
        context_str += "---------------------------------\n"


    # 3. Construct the full prompt
    system_prompt = (
        "You are a Leaving Cert Math tutor. "
        "You will be provided with a specific math question, an image of a student's attempt, "
        "and some relevant pages from their textbook.\n\n"
        "STRICT RULES:\n"
        "1. RELEVANCE CHECK: If the student's work is irrelevant to the question, state that "
        "the work appears irrelevant and do not provide math feedback.\n"
        "2. USE THE TEXTBOOK: First, review the provided textbook pages. Your primary goal is to "
        "guide the student using concepts explained in their own textbook.\n"
        "3. SOCRATIC FEEDBACK: Do not give the answer. Ask guiding questions that lead the student to "
        "their own solution, referencing the textbook content. For example: 'Good start! On page "
        "{page_number} of your textbook, it mentions the cosine rule. How might that apply here?'\n"
        "4. EXPLICIT REFERENCES: You MUST reference the textbook page number when you use its content.\n"
        "5. LATEX: Always put a space before and after inline dollar signs (e.g., $ x $). "
        "Never wrap LaTeX in parentheses; put parentheses inside the math block: $ (x+1) $.\n"
        "6. Use $$ for centered equations."
    )
    
    user_content = [
        {"type": "text", "text": f"Question: {question_text}\n\nAnalyze my steps in the image, using the provided textbook context below.\n{context_str}"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
    ]

    # 4. Get feedback from Mistral
    try:
        response = client.chat(
            model="mistral-large-latest", # Using a more powerful model for better reasoning
            messages=[
                SystemMessage(content=system_prompt),
                UserMessage(content=user_content)
            ],
            max_tokens=700,
        )
        feedback = response.choices[0].message.content
        return feedback, relevant_pages # Return pages for display in the app

    except Exception as e:
        return f"Error getting AI feedback: {str(e)}", []


def load_questions():
    """Helper function to load questions from the JSON file"""
    # This might need to be adjusted or removed depending on the new app structure
    path = os.path.join(os.path.dirname(__file__),"..","data","questions.json")
    with open(path, "r") as f:
        return json.load(f)
