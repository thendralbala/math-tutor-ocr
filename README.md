---
title: Leaving Cert Math Tutor
emoji: 📐
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.52.2
app_file: app.py
pinned: false
---

# 📝 Leaving Cert Math Tutor

An educational platform designed to help Irish secondary students master Leaving Certificate Mathematics. Using Generative AI, the platform provides personalized, Socratic feedback on handwritten or digital solutions to exam-style questions.

## Overview
The Leaving Cert Math Tutor bridge the gap between static practice and private tutoring. Instead of just providing the final answer, the AI analyzes the student's step-by-step logic and provides guiding questions to help them find the solution themselves.

### Key Features

- **Interactive Canvas:** Draw or write your math solutions directly in the browser using a digital whiteboard.

- **Socratic Tutoring:** Powered by Mistral AI, the tutor identifies specific errors and asks guiding questions rather than giving away the answer.

- **Relevance Checking:** Automatically detects if the student's work matches the assigned question to ensure focused learning.

- **RAG-Powered Feedback:** Uses a Retrieval-Augmented Generation (RAG) pipeline to reference the student's own textbook in the feedback.

- **Past Paper Integration:** Access curated questions from previous Leaving Cert exams.



## Technical Stack

- **Frontend:** [Streamlit](https://streamlit.io/)

- **AI Engine:** [Mistral AI](https://mistral.ai/) (Pixtral-12B and Mistral-Embed)

- **Drawing Interface:** `streamlit-drawable-canvas`

- **Vector Store:** NumPy & scikit-learn

- **Deployment:** Hugging Face Spaces via GitHub Actions



## Prerequisites

- Python 3.8+

- Mistral API Key



## Local Installation



1. **Clone the repository:**

   ```bash

   git clone https://github.com/thendralbala/math-tutor-ocr.git

   cd math-tutor-ocr

   ```



2. **Set up a virtual environment:**

   ```bash

   python -m venv venv

   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```



3. **Install dependencies:**

   ```bash

   pip install -r requirements.txt

   ```



4. **Set up Environment Variables:**

   Create a `.env` file in the root directory and add your Mistral API key:

   ```env

   MISTRAL_API_KEY=your_mistral_api_key_here

   ```



5. **Run the application:**

   ```bash

   streamlit run app.py

   ```
