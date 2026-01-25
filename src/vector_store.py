import os
import json
import numpy as np
from mistralai import Mistral
from dotenv import load_dotenv
import time

def create_vector_store():
    """
    Creates a vector store from the processed textbook data using Mistral embeddings, with resume support.
    """
    # --- CONFIGURATION ---
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables.")
    
    client = Mistral(api_key=api_key)

    processed_data_path = "data/processed/textbook.json"
    vector_store_path = "data/processed/textbook_vectors.npy"
    metadata_path = "data/processed/textbook_metadata.json"

    if not os.path.exists(processed_data_path):
        raise FileNotFoundError(f"{processed_data_path} not found. Please run the processing script first.")

    with open(processed_data_path, "r") as f:
        processed_data = json.load(f)

    # --- RESUME LOGIC ---
    embeddings = []
    metadata = []
    start_page = 0
    if os.path.exists(vector_store_path) and os.path.exists(metadata_path):
        print("Existing vector store found, attempting to resume...")
        embeddings = list(np.load(vector_store_path))
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        if metadata:
            start_page = metadata[-1]["page_number"]
    
    print(f"Starting or resuming from page {start_page + 1}")


    # --- CREATE EMBEDDINGS ---
    print("Creating embeddings for textbook pages using Mistral...")
    for page in processed_data:
        if page["page_number"] <= start_page:
            continue

        text_to_embed = f"Page {page['page_number']}: {page['text']}"
        try:
            time.sleep(1) # Add a delay to avoid rate limiting
            response = client.embeddings.create(
                model="mistral-embed",
                inputs=[text_to_embed]
            )
            embeddings.append(response.data[0].embedding)
            metadata.append({
                "page_number": page["page_number"],
                "text": page["text"],
                "image_paths": page["image_paths"]
            })

            # Save progress after each embedding
            np.save(vector_store_path, np.array(embeddings))
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)
            print(f"Processed page {page['page_number']}")

        except Exception as e:
            print(f"Error creating embedding for page {page['page_number']}: {e}")

    # --- SAVE VECTOR STORE ---
    if embeddings:
        print(f"Vector store created with {len(embeddings)} embeddings.")
        print(f"Embeddings saved to: {vector_store_path}")
        print(f"Metadata saved to: {metadata_path}")
    else:
        print("No embeddings were created.")

if __name__ == "__main__":
    create_vector_store()
