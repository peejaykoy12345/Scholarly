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

def generate_questions(input: str, quiz_type: str, question_count: int):
    assert quiz_type.lower() in ["multiple choice", "situational"], "Invalid quiz_type"

    system_prompt = f"""
        You are an AI that generates quizzes based on provided content. Your task is to create {question_count} {quiz_type.lower()} questions from the input text.

        ⚠️ Respond ONLY in the following pure JSON format (no markdown, no explanations, no extra text):

        {{
        "input": "<original input text here>",
        "output": [
            {{
            "question": "What is the capital of France?",
            "choices": ["Berlin", "Madrid", "Paris", "Rome"],
            "answer_index": 2
            }},
            ...
        ]
        }}

        📝 Notes:
        - The number of items in "output" must exactly be {question_count}.
        - The "choices" list must always have exactly 4 unique options.
        - Only one choice should be correct (indicated by "answer_index").
        - Do NOT include explanations or non-JSON content.
        - DO NOT ADD ``` OR ANY SPECIAL CHARACTERS JUST PLAIN WORDS LIKE STRINGS

        📘 Special Instructions:
        If quiz_type is "situational":
        - Frame each question as a realistic or practical scenario where the user must make a decision or judgment.
        - Use real-life contexts such as daily decisions, ethical dilemmas, school/work situations, etc.
        - The situation must be clearly described, and the question should test critical thinking or understanding of the scenario.
        - Keep it concise but meaningful.
    """


    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        content = response.json()['choices'][0]['message']['content']
        parsed = json.loads(content)
        print(parsed)
        return parsed

    except KeyError:
        return {
            "error": "❌ Response missing 'choices'",
            "response": response.json()
        }

    except json.JSONDecodeError:
        return {
            "error": "⚠️ Response was not valid JSON",
            "raw_output": content
        }


#print(type(generate_questions("Cristiano Ronaldo is the top leading goal scorer")), f'\n content: \n {generate_questions("Cristiano Ronaldo is the top leading goal scorer")}')