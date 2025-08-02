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
    assert quiz_type.lower() in ["identification", "situational"], "Invalid quiz_type"

    system_prompt = f"""
        You are an AI that generates {quiz_type.lower()} quiz questions.

        Your task is to create EXACTLY {question_count} questions based on the input text.

        ⚠️ FOLLOW THESE RULES:

        - Each question MUST include:
        - "question": <string>
        - "answer_format": "{answer_format}"

        - Only generate questions using answer_format = "{answer_format}"

        - DO NOT use any other format. Only "{answer_format}" is allowed.

        - If answer_format is "Multiple Choice":
        - Add a "choices" list with 4 strings
        - Add "answer_index" as an integer (0–3) indicating the correct answer

        - If answer_format is "No Choices" or "Essay":
        - DO NOT include "choices"
        - DO NOT include "answer_index"

        🧠 FORMAT EXAMPLES:

        If answer_format is "Multiple Choice":
        {{
        "input": "<original input text>",
        "output": [
            {{
            "question": "What is the capital of France?",
            "choices": ["Berlin", "Madrid", "Paris", "Rome"],
            "answer_index": 2,
            "answer_format": "Multiple Choice"
            }}
        ]
        }}

        If answer_format is "No Choices":
        {{
        "input": "<original input text>",
        "output": [
            {{
            "question": "Why is the sky blue?",
            "answer_format": "No Choices"
            }}
        ]
        }}

        ⚠️ STRICT OUTPUT RULES:
        - Only return raw JSON (no markdown, no code blocks, no commentary)
        - The number of questions MUST be exactly {question_count}
        - Each question MUST have "answer_format": "{answer_format}" (no others)

        🌐 Use the same language as the input text.
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

        if isinstance(parsed, list):
            print("⚠️ Model returned a raw list. Wrapping it manually.")
            return {
                "input": input,
                "output": parsed
            }


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

def generate_questions_but_with_long_text(text: str, quiz_type: str, question_count: int, answer_format: str):
    chunks = split_text(text)
    total_chunks = len(chunks)
    questions_count_per_chunk = question_count // total_chunks
    remainder = question_count % total_chunks

    all_questions = []

    for index, chunk in enumerate(chunks):
        q_count = questions_count_per_chunk + (1 if index < remainder else 0)

        result = generate_questions(chunk, quiz_type, q_count, answer_format)

        if isinstance(result, dict) and "output" in result:
            all_questions.extend(result["output"])
        elif isinstance(result, dict) and "error" in result:
            print("❌ Error from Groq:", result["error"])
            print("🔎 Full response:", result.get("response") or result.get("raw_output"))
        else:
            print("⚠️ Unexpected result type:", type(result))
            print(result)

    return {
        "input": text,
        "output": all_questions[:question_count]
    }

#print(type(generate_questions("Cristiano Ronaldo is the top leading goal scorer")), f'\n content: \n {generate_questions("Cristiano Ronaldo is the top leading goal scorer")}')