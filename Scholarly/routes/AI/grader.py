import requests
from os import getenv
from dotenv import load_dotenv

load_dotenv()
api_key = getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def grade_paper(question: str, answer: str, answer_format: str) -> dict:
    system_prompt = f"""
    You are an AI grading assistant.

    The Answer Format should be {answer_format} if not automatically WRONG and say wrong answer format in the explanation

    Given a quiz question and a student's answer, respond ONLY in the following JSON format:

    {
      "result": "Correct" or "Wrong",
      "correct_answer": "What could be a possible correct answer?",
      "explanation": "Explain why it is correct or wrong."
    }

    ⚠️ STRICT RULES:
    - NO markdown, backticks, or formatting like ```json.
    - Only return plain JSON as text. No extra commentary.
    - The "result" must be either "Correct" or "Wrong".
    - Keep the explanation clear and short.
    - Be as fair as possible 
    """

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}\nAnswer: {answer}"}
        ],
        "temperature": 0.3,
        "max_tokens": 512
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        return {
            "error": str(e),
            "raw_output": response.text
        }
