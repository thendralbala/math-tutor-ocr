import os
import json
import base64
import time
from glob import glob
from PIL import Image
from mistralai import Mistral
from dotenv import load_dotenv, find_dotenv

# --- CONFIGURATION ---
load_dotenv(find_dotenv())
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
OUTPUT_DIR = os.path.join(DATA_DIR, "processed")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Ensure folders exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# --- HELPER: VISION CHECK (Same as before) ---
def is_useful_image(client, image_path):
    # 1. Size Check
    try:
        with Image.open(image_path) as img:
            if img.width < 50 or img.height < 50: return False
    except: return False

    # 2. API Check
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        
        time.sleep(1) # Rate limit protection
        resp = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[{
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Is this a useful diagram (graph/geometry/shape)? Answer YES or NO. Answer NO for blank grids/lines."},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64}"}
                ]
            }]
        )
        return "YES" in resp.choices[0].message.content.upper()
    except:
        return True # Default to keep if error

# --- MAIN EXTRACTION LOGIC ---
def process_single_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    print(f"\n📄 Processing: {filename}...")
    
    # 1. Mistral OCR
    with open(pdf_path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": f"data:application/pdf;base64,{pdf_b64}"},
        include_image_base64=True
    )

    full_text = ""
    valid_images = {}

    # 2. Save & Filter Images
    print("   ...filtering images")
    for page in ocr_response.pages:
        full_text += f"\n\n--- Page {page.index} ---\n\n{page.markdown}"
        for img in page.images:
            img_filename = f"{filename.split('.')[0]}_{img.id}.png"
            img_path = os.path.join(IMAGES_DIR, img_filename)
            
            # Save temporarily
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(img.image_base64.split(",")[-1]))
            
            # Check if useful
            if is_useful_image(client, img_path):
                valid_images[img.id] = f"data/images/{img_filename}" # Store RELATIVE path for App
            else:
                os.remove(img_path) # Delete junk

    # 3. Structure to JSON
    print("   ...structuring JSON")
    prompt = f"""
    Extract math questions from this text into JSON.
    Valid Image IDs: {list(valid_images.keys())}
    
    Structure:
    {{
        "title": "Exam Paper Title (e.g. 2024 Paper 1)",
        "year": 2024,
        "questions": [
            {{
                "id": "q1",
                "topic": "Algebra",
                "text": "Question text with LaTeX",
                "image_id": "img_id_from_list_or_null"
            }}
        ]
    }}
    
    Text: {full_text}
    """
    
    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(chat_response.choices[0].message.content)
    
    # Link Image Paths
    if "questions" in data:
        for q in data["questions"]:
            if q.get("image_id") in valid_images:
                q["image_url"] = valid_images[q["image_id"]]
            else:
                q["image_url"] = None

    # 4. Save JSON
    json_filename = filename.replace(".pdf", ".json")
    output_path = os.path.join(OUTPUT_DIR, json_filename)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Saved to {output_path}")

# --- RUN LOOP ---
if __name__ == "__main__":
    pdf_files = glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"Found {len(pdf_files)} PDFs.")
    for pdf in pdf_files:
        process_single_pdf(pdf)