---
title: Leaving Cert Math Tutor
emoji: 📐
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 0.5.0
app_file: app.py
pinned: false
---

# 📝 Leaving Cert Math Tutor

An educational platform designed to help Irish secondary students master Leaving Certificate Mathematics. Using Generative AI, the platform provides personalized, Socratic feedback on handwritten or digital solutions to exam-style questions.

## Overview
The Leaving Cert Math Tutor bridge the gap between static practice and private tutoring. Instead of just providing the final answer, the AI analyzes the student's step-by-step logic and provides guiding questions to help them find the solution themselves.

### Key Features
- **Interactive Canvas:** Draw or write your math solutions directly in the browser using a digital whiteboard.
- **Socratic Tutoring:** Powered by GPT-4o-mini, the tutor identifies specific errors and asks guiding questions rather than giving away the answer.
- **Relevance Checking:** Automatically detects if the student's work matches the assigned question to ensure focused learning.
- **Past Paper Integration:** Access curated questions from previous Leaving Cert exams (currently supporting 2023 and 2024).

## Technical Stack
- **Frontend:** [Streamlit](https://streamlit.io/)
- **AI Engine:** [OpenAI API](https://openai.com/) (GPT-4o-mini)
- **Drawing Interface:** `streamlit-drawable-canvas`
- **Deployment:** Hugging Face Spaces via GitHub Actions

## Prerequisites
- Python 3.8+
- OpenAI API Key

## Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/thendralbala/lcert-math-tutor.git](https://github.com/thendralbala/lcert-math-tutor.git)
   cd lcert-math-tutor

## Prototype

Access the prototype application at: [https://huggingface.co/spaces/thendralbala/lcert-math-tutor](https://huggingface.co/spaces/thendralbala/lcert-math-tutor)