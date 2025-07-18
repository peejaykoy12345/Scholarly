import requests
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()
api_key = getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def generate_flashcards_using_ai(input: str, flashcards_count: int) -> dict:
    system_prompt = f"""
    You are an AI that creates flashcards to help students study.

    Your task: Generate EXACTLY {flashcards_count} flashcards based on the input text.

    ⚠️ Format Requirements:
    - Return only raw JSON (no markdown/code/comments)
    - DO NOT USE ``` AS IT WILL RUIN THE DECODING PROCESS AND THROW AN ERROR
    - The output must be a dictionary with this structure:
    {{
      "input": "<the original input text>",
      "output": [
        {{
          "question": "What is...",
          "answer": "The answer is..."
        }}
      ]
    }}
    - The number of flashcards must match {flashcards_count}.
    - Each flashcard must have a "question" and "answer" field.
    - Do not include extra commentary or fields.

    🌐 Use the same language as the input.
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
            "error": "❌ Response missing 'output'",
            "response": response.json()
        }

    except json.JSONDecodeError:
        return {
            "error": f"⚠️ Response was not valid JSON content = {content}",
            "raw_output": content
        }


def split_text(text: str, chunk_size: int = 1000): 
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_flashcards(text: str, flashcards_count: int) -> dict:
    chunks = split_text(text)
    total_chunks = len(chunks)
    questions_count_per_chunk = flashcards_count // total_chunks
    remainder = flashcards_count % total_chunks

    all_questions = []

    for index, chunk in enumerate(chunks):
        f_count = questions_count_per_chunk + (1 if index < remainder else 0)

        result = generate_flashcards_using_ai(chunk, f_count)
        if "output" in result:
            all_questions.extend(result["output"])
        else:
            print("Error:", result["error"])

    return {
        "input": text,
        "output": all_questions[:flashcards_count]
    }