import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import streamlit_js_eval
from PIL import Image
import os
import json
from glob import glob
from openai import OpenAI
from src.tutor_engine import get_ai_feedback, load_questions

# Initialize session state 
if 'feedback_storage' not in st.session_state:
    st.session_state['feedback_storage'] = {}

st.set_page_config(layout='wide', page_title="Leaving Cert Math Tutor")

# Setup API Client with basic error checking
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OpenAI API Key. Please set in your environment variables.")
    st.stop()

client = OpenAI(api_key=api_key)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
json_files = glob(os.path.join(DATA_DIR, "*.json"))

if not json_files:
    st.error("No processed data found. Please run the extraction first.")
    st.stop()

# Create a mapping
paper_map = {}

for f in json_files:
    name = os.path.basename(f).replace(".json", "").replace("_", " ").title()
    paper_map[name] = f


# Sidebar Selection
st.sidebar.title("Select Exam Paper")
selected_paper_name = st.sidebar.selectbox("Choose Paper:", list(paper_map.keys()))


# Load the specific JSON file selected
current_paper_path = paper_map[selected_paper_name]
with open(current_paper_path, "r") as f:
    paper_data = json.load(f)

# MAIN UI
st.title(f"{paper_data.get('title', selected_paper_name)}")

canvas_width = 700

questions = paper_data.get("questions", [])

for q in questions:
        with st.container():
            # Header & Topic
            st.subheader(f"Question {q.get('id', 'Unknown')}")
            st.caption(f"Topic: {q.get('topic', 'General')}")
            
            # A. Display Text
            st.markdown(q.get('text', ''))

            # B. Display Extracted Image (The new addition)
            # We check if 'image_url' exists in the JSON and if the file actually exists
            if q.get("image_url"):
                if os.path.exists(q["image_url"]):
                    st.image(q["image_url"], width=500)
                else:
                    st.warning(f"Diagram missing at {q['image_url']}")

            st.write("### Your Solution")

            # C. Unique Canvas
            # We use the Question ID to ensure every canvas is unique
            canvas_key = f"canvas_{selected_paper_name}_{q.get('id')}"

            canvas_result = st_canvas(
                stroke_width=3, 
                stroke_color="#000", 
                background_color="#eee",
                height=400, 
                width=canvas_width, 
                drawing_mode="freedraw", 
                key=canvas_key
            )

            # D. AI Analysis Button
            if st.button(f"Analyze Question {q.get('id')}", key=f"btn_{canvas_key}"):
                if canvas_result.image_data is not None:
                    # Convert canvas to PIL Image
                    img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').convert("RGB")
                    
                    with st.spinner("Tutor is reviewing your steps..."):
                        # We pass the text and the canvas image to the AI
                        feedback = get_ai_feedback(img, q.get('text', ''), client)
                        st.session_state.feedback_storage[canvas_key] = feedback
                else:
                    st.warning("Please write your solution first!")

            # E. Display Feedback
            if canvas_key in st.session_state.feedback_storage:
                st.markdown("### Tutor Feedback")
                st.info(st.session_state.feedback_storage[canvas_key])

            st.divider()