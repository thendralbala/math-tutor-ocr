import pytest
from unittest.mock import MagicMock, patch
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import json

# Add the src directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tutor_engine import get_ai_feedback, find_relevant_pages
from mistralai import SystemMessage, UserMessage

@pytest.fixture
def mock_mistral_client():
    """Create a mock Mistral client."""
    mock_client = MagicMock()
    # Mock the chat completions response
    mock_chat_response = MagicMock()
    mock_chat_response.choices[0].message.content = "This is a mock feedback."
    mock_client.chat.complete.return_value = mock_chat_response
    
    # Mock the embeddings response
    mock_embedding = [0.1] * 1024  # Assuming embedding dimension is 1024
    mock_embeddings_response = MagicMock()
    mock_embeddings_response.data[0].embedding = mock_embedding
    mock_client.embeddings.create.return_value = mock_embeddings_response
    
    
    return mock_client

@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = Image.new('RGB', (600, 300), color = 'white')
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    d.text((10,10), "x = 5", fill=(0,0,0), font=font)
    return img

@pytest.fixture(scope="module")
def setup_vector_store():
    """Create dummy vector store variables for testing."""
    # Create dummy vector store data
    dummy_vectors = np.random.rand(5, 1024).astype(np.float32)
    dummy_metadata = [
        {"page_number": 1, "text": "This is page 1.", "image_paths": []},
        {"page_number": 2, "text": "This is page 2.", "image_paths": []},
        {"page_number": 3, "text": "This is page 3.", "image_paths": []},
        {"page_number": 4, "text": "This is page 4.", "image_paths": []},
        {"page_number": 5, "text": "This is page 5.", "image_paths": []},
    ]

    with patch('src.tutor_engine.textbook_vectors', dummy_vectors), \
         patch('src.tutor_engine.textbook_metadata', dummy_metadata):
        yield


def test_get_ai_feedback(mock_mistral_client, sample_image, setup_vector_store):
    """Test the get_ai_feedback function."""
    question = "What is the value of x?"
    feedback, relevant_pages = get_ai_feedback(sample_image, question, mock_mistral_client)

    assert feedback == "This is a mock feedback."
    assert isinstance(relevant_pages, list)

def test_find_relevant_pages(mock_mistral_client, setup_vector_store):
    """Test the find_relevant_pages function."""
    query = "test query"
    relevant_pages = find_relevant_pages(query, mock_mistral_client)
    
    assert isinstance(relevant_pages, list)
    assert len(relevant_pages) <= 3 
    if relevant_pages:
        assert "page_number" in relevant_pages[0]
        assert "text" in relevant_pages[0]

def test_get_ai_feedback_no_rag(mock_mistral_client, sample_image):
    """Test get_ai_feedback when vector store is not available."""
    # Temporarily hide the vector store by patching the module variables
    with patch('src.tutor_engine.textbook_vectors', None), \
         patch('src.tutor_engine.textbook_metadata', None):
        feedback, relevant_pages = get_ai_feedback(sample_image, "A question", mock_mistral_client)
    
    assert feedback == "This is a mock feedback."
    assert relevant_pages == []
