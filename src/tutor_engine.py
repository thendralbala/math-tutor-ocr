import io
import base64
import os
import json
from openai import OpenAI

def get_ai_feedback(image, question_text,client):
    """
    Converts image to base64 and fetches Socratic feedback.
    Includes a check to ensure the student's work matches the assigned question.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a Leaving Cert Math tutor. "
                        "You will be provided with a specific math question and an image of a student's attempt.\n\n"
                        "STRICT RULES:\n"
                        "1. RELEVANCE CHECK: If the student's work is irrelevant to the question provided or "
                        "if they are solving a different problem entirely, explicitly state that the work "
                        "appears irrelevant to this specific question and do not provide math feedback.\n"
                        "2. SOCRATIC FEEDBACK: If relevant, do not give the answer. Ask guiding questions.\n"
                        "3. LATEX: Always put a space before and after inline dollar signs (e.g., $ x $). "
                        "Never wrap LaTeX in parentheses; put parentheses inside the math block: $ (x+1) $.\n"
                        "4. Use $$ for centered equations."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Question to solve: {question_text}\n\nAnalyze my math steps in the image:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ],
                }
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
def load_questions():
    """Helper function to load questions from the JSON file"""
    path = os.path.join(os.path.dirname(__file__),"..","data","questions.json")
    with open(path, "r") as f:
        return json.load(f)
