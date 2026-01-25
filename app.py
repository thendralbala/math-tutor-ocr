import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import json
from glob import glob
from src.tutor_engine import get_ai_feedback, get_mistral_client

# --- INITIALIZATION ---
st.set_page_config(layout='wide', page_title="Leaving Cert Math Tutor")

# Initialize session state for feedback and RAG results
if 'feedback_storage' not in st.session_state:
    st.session_state['feedback_storage'] = {}

# Setup Mistral Client
try:
    client = get_mistral_client()
except ValueError as e:
    st.error(e)
    st.stop()

# --- DATA LOADING ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
# Exclude the textbook data from the paper selection
json_files = [f for f in glob(os.path.join(DATA_DIR, "*.json")) if "textbook" not in f]


if not json_files:
    st.error("No processed exam paper data found. Please run the extraction scripts first.")
    st.stop()

# Create a mapping for exam papers
paper_map = {}
for f in json_files:
    name = os.path.basename(f).replace(".json", "").replace("_", " ").title()
    paper_map[name] = f

# --- SIDEBAR ---
st.sidebar.title("Select Exam Paper")
selected_paper_name = st.sidebar.selectbox("Choose Paper:", list(paper_map.keys()))

# Load the selected exam paper
current_paper_path = paper_map[selected_paper_name]
with open(current_paper_path, "r") as f:
    paper_data = json.load(f)

# --- MAIN UI ---
st.title(f"📚 {paper_data.get('title', selected_paper_name)}")
st.markdown("---")

questions = paper_data.get("questions", [])

if not questions:
    st.warning("This paper has no questions loaded.")
    st.stop()

for q in questions:
    # Use columns for a cleaner layout
    col1, col2 = st.columns([2, 3]) # Question on the left, canvas/feedback on the right

    with col1:
        st.subheader(f"Question {q.get('id', 'Unknown')}")
        st.caption(f"Topic: {q.get('topic', 'General')}")
        st.markdown(q.get('text', ''))

        if q.get("image_url") and os.path.exists(q["image_url"]):
            st.image(q["image_url"])
        
    with col2:
        st.write("#### Your Solution")
        canvas_key = f"canvas_{selected_paper_name}_{q.get('id')}"
        
        canvas_result = st_canvas(
            stroke_width=3,
            stroke_color="#000",
            background_color="#eee",
            height=300,
            width=600,
            drawing_mode="freedraw",
            key=canvas_key
        )

        analyze_button = st.button(f"Analyze My Solution for Q{q.get('id')}", key=f"btn_{canvas_key}")

        if analyze_button:
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').convert("RGB")
                
                with st.spinner("🧑‍🏫 Tutor is thinking..."):
                    # Get feedback and relevant pages from the RAG-powered engine
                    feedback, relevant_pages = get_ai_feedback(img, q.get('text', ''), client)
                    st.session_state.feedback_storage[canvas_key] = {
                        "feedback": feedback,
                        "pages": relevant_pages
                    }
            else:
                st.warning("Please write your solution on the canvas first!")

        # Display Tutor Feedback and Relevant Pages
        if canvas_key in st.session_state.feedback_storage:
            stored_data = st.session_state.feedback_storage[canvas_key]
            
            st.markdown("#### Tutor Feedback")
            st.info(stored_data.get("feedback", "No feedback available."))

            if stored_data.get("pages"):
                st.markdown("---")
                st.markdown("#### Relevant Textbook Pages")
                for page in stored_data["pages"]:
                    with st.expander(f"Page {page['page_number']}"):
                        st.markdown(page.get("text", "No text extracted for this page."))
                        if page.get("image_paths"):
                            for img_path in page["image_paths"]:
                                if os.path.exists(img_path):
                                    st.image(img_path)

    st.markdown("---")