# Scholarly 📚🧠

Scholarly is a Flask-based AI-powered study tool that lets users:

- 📝 Write & store notes
- 🤖 Auto-generate quizzes from notes (via Groq API)
- ✅ Take & grade quizzes (Multiple Choice, Essay, etc.)
- 📊 View quiz results and feedback

## Features

AI quiz generation using Groq LLM
Essay and multiple choice grading
Flashcard generation from notes using LLaMA
Session-based preview & saving
Quick quizzes without saving
Clean Bootstrap-based UI

## Setup

```bash
git clone https://github.com/your-username/scholarly.git
cd scholarly
pip install -r requirements.txt
```

Make a .env file in the root directory:
GROQ_API_KEY=yourgroqkey

then run:

python run.py or gunicorn run:app

## Tech Stack
Python, Flask, SQLAlchemy

Groq API (LLaMA model)

Bootstrap & Jinja2 templates