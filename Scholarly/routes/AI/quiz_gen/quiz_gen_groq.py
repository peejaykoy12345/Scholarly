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

def generate_questions(input: str, quiz_type: str, question_count: int, answer_format: str):
    assert quiz_type.lower() in ["multiple choice", "situational"], "Invalid quiz_type"

    system_prompt = f"""
        You are an AI that generates quizzes based on provided content. Your task is to create {question_count} {quiz_type.lower()} questions from the input text.

        ⚠️ Respond ONLY in the following pure JSON format (no markdown, no explanations, no extra text):

        If answer_format is "Multiple Choice":
        {{
        "input": "<original input text here>",
        "output": [
            {{
            "question": "What is the capital of France?",
            "choices": ["Berlin", "Madrid", "Paris", "Rome"],
            "answer_index": 2,
            "answer_format": "Multiple Choice"
            }}
        ]
        }}

        If answer_format is "No Choices" or "Essay":
        {{
        "input": "<original input text here>",
        "output": [
            {{
            "question": "Why is the sky blue?",
            "answer_format": "No Choices"
            }},
            {{
            "question": "Describe how a bill becomes a law.",
            "answer_format": "Essay"
            }}
        ]
        }}

        📝 Notes:
        - The number of items in "output" must exactly be {question_count}.
        - Each question object must include "question" and "answer_format".
        - For "Multiple Choice":
            - Add exactly 4 options in "choices".
            - Add an integer "answer_index" (0–3).
        - For "No Choices" or "Essay":
            - DO NOT include "choices" or "answer_index".
        - All questions must match the `answer_format` value: "{answer_format}".

        🌐 Language Note:
        - If the input text is in another language, generate the questions and answers in that same language.

        📘 Situational Instructions:
        If quiz_type is "situational":
        - Frame questions as real-life or practical situations requiring critical thinking.
        - Focus on decision-making, ethics, or problem-solving in daily or academic settings.
        - Keep it concise but meaningful.

        🚫 STRICTLY FORBIDDEN:
        - No markdown, no backticks, no explanations.
        - Only return valid raw JSON as shown above.
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
            "error": f"⚠️ Response was not valid JSON content = {content}",
            "raw_output": content
        }

def split_text(text: str, chunk_size: int = 1000): 
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_questions_but_with_long_text(text: str, quiz_type: str, question_count: int):
    chunks = split_text(text)
    total_chunks = len(chunks)
    questions_count_per_chunk = question_count // total_chunks
    remainder = question_count % total_chunks

    all_questions = []

    for index, chunk in enumerate(chunks):
        q_count = questions_count_per_chunk + (1 if index < remainder else 0)

        result = generate_questions(chunk, quiz_type, q_count)
        if "output" in result:
            all_questions.extend(result["output"])
        else:
            print("Error:", result["error"])

    return {
        "input": text,
        "output": all_questions[:question_count]
    }

#print(type(generate_questions("Cristiano Ronaldo is the top leading goal scorer")), f'\n content: \n {generate_questions("Cristiano Ronaldo is the top leading goal scorer")}')