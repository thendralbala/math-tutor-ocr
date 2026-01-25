import os
import json
import base64
from mistralai import Mistral
from dotenv import load_dotenv

def process_textbook(pdf_path, images_output_dir, processed_output_path):
    """
    Processes a textbook PDF using Mistral's OCR, extracting images and text for each page,
    with resume support.
    """
    # --- CONFIGURATION ---
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables.")
    
    client = Mistral(api_key=api_key)

    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # 1. Mistral OCR
    print(f"📄 Processing: {os.path.basename(pdf_path)}...")
    with open(pdf_path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": f"data:application/pdf;base64,{pdf_b64}"},
        include_image_base64=True
    )

    processed_data = []
    start_page = 0
    if os.path.exists(processed_output_path):
        with open(processed_output_path, "r") as f:
            try:
                processed_data = json.load(f)
                if processed_data:
                    start_page = processed_data[-1]["page_number"]
            except json.JSONDecodeError:
                print("Could not decode existing JSON, starting from scratch.")
    
    print(f"Starting or resuming from page {start_page + 1}")

    # 2. Process pages
    for page in ocr_response.pages:
        page_number = page.index + 1
        if page_number <= start_page:
            continue
            
        print(f"   ...processing page {page_number}/{len(ocr_response.pages)}")

        # Save images from the page
        image_paths = []
        for img in page.images:
            img_filename = f"page_{page_number}_{img.id}.png"
            img_path = os.path.join(images_output_dir, img_filename)
            
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(img.image_base64.split(",")[-1]))
            image_paths.append(img_path)

        page_content = {
            "page_number": page_number,
            "text": page.markdown,
            "image_paths": image_paths
        }
        processed_data.append(page_content)

        # 3. Save JSON progress
        with open(processed_output_path, "w") as f:
            json.dump(processed_data, f, indent=4)

    print(f"Finished processing. Saved {len(processed_data)} pages to {processed_output_path}")

if __name__ == "__main__":
    PDF_PATH = "data/textbooks/texts_and_tests_4.pdf"
    IMAGES_OUTPUT_DIR = "data/textbook_images"
    PROCESSED_OUTPUT_PATH = "data/processed/textbook.json"
    process_textbook(PDF_PATH, IMAGES_OUTPUT_DIR, PROCESSED_OUTPUT_PATH)

