import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import streamlit_js_eval
from PIL import Image
import os
from openai import OpenAI


from src.tutor_engine import get_ai_feedback, load_questions

# Initialize session state 
if 'feedback_storage' not in st.session_state:
    st.session_state['feedback_storage'] = {}

# Setup API Client with basic error checking
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OpenAI API Key. Please set in your environment variables.")
    st.stop()

client = OpenAI(api_key=api_key)

exam_data = load_questions()

# Layout configuration
st.set_page_config(layout='wide', page_title="Leaving Cert Math Tutor")
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