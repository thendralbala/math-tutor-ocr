import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import streamlit_js_eval
from PIL import Image
import os
import sys
from openai import OpenAI
#from tutor_utils import get_ai_feedback, load_questions
import io
import base64
from openai import OpenAI
import os
import json

if 'feedback_storage' not in st.session_state:
    st.session_state['feedback_storage'] = {}

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
    with open(os.path.join("data", "questions.json"), "r") as f:
        return json.load(f)

# Setup API Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


exam_data = load_questions()

# Layout configuration
st.set_page_config(layout='wide', page_title="Leaving Cert Math Tutor")

# Year selection sidebar
selected_year = st.sidebar.selectbox("Select Exam Year:", list(exam_data.keys()))
st.title(f"📝 {selected_year} Questions")
window_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH')

if window_width:
    canvas_width = min(int(window_width * 0.9), 800)

    questions = exam_data.get(selected_year, [])

    for q in questions:
        st.subheader(f"Question {q['topic']}")
        st.markdown(q['text'])

        # Unique keys for each canvas
        canvas_key = f"canvas_{selected_year}_{q['id']}"

        canvas_result = st_canvas(
            stroke_width=3, 
            stroke_color="#000", 
            background_color="#eee",
            height=400, 
            width=canvas_width, 
            drawing_mode="freedraw", 
            key=canvas_key
        )

        if st.button(f"Analyze Question {q['id']}", key = f"btn_{canvas_key}"):
            if canvas_result.image_data is not None:
                # Convert canvas to PIL Image
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').convert("RGB")
                
                with st.spinner("Tutor is reviewing your steps..."):
                    feedback = get_ai_feedback(img,q['text'],client)
                    st.session_state.feedback_storage[canvas_key] = feedback
            else:
                st.warning("Please write your solution first!")

        if canvas_key in st.session_state.feedback_storage:
            st.markdown("### Tutor Feedback")
            st.info(st.session_state.feedback_storage[canvas_key])

        st.divider()