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

        Your job is to assess if the student's answer matches the expected answer format: "{answer_format}".

        If the answer format is incorrect, mark it as Wrong and mention this in the explanation.

        You must return ONLY a raw JSON object in the exact format below:

        {{
        "result": "Correct" or "Wrong",
        "correct_answer": "What could be a possible correct answer?",
        "explanation": "Explain why it is correct or wrong."
        }}

        STRICT RULES:
        - Do NOT use markdown or code formatting like ```json.
        - Do NOT include any commentary, tips, or extra text.
        - The "result" field must ONLY be "Correct" or "Wrong".
        - The explanation must be short and clear.
        - Match the language and intent of the question.
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
