import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import streamlit_js_eval
from PIL import Image
import base64
import io
import os
from openai import OpenAI

# 1. Setup API Client
# On Hugging Face, this will automatically pull from your "Secrets"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(layout="wide", page_title="Math Tutor MVP")

def get_ai_feedback(image):
    # Convert PIL image to base64 string
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Leaving Cert Math tutor. A student has uploaded their workout. "
                               "1. Convert their work to LaTeX. "
                               "2. Check for logic errors. "
                               "3. If wrong, give a subtle hint about the step they missed. Don't just give the answer."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze my math steps:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ],
                }
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Layout ---
st.title("📝 Leaving Cert Math Tutor")
window_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH')

if window_width:
    canvas_width = min(int(window_width * 0.9), 800)
    canvas_result = st_canvas(
        stroke_width=3, stroke_color="#000", background_color="#eee",
        height=400, width=canvas_width, drawing_mode="freedraw", key="canvas"
    )

    if st.button("Analyze My Work", use_container_width=True):
        if canvas_result.image_data is not None:
            # Convert canvas to PIL Image
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').convert("RGB")
            
            with st.spinner("Tutor is reviewing your steps..."):
                feedback = get_ai_feedback(img)
                st.markdown("### Tutor Feedback")
                st.write(feedback)
        else:
            st.warning("Please write your solution first!")