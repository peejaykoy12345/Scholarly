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

system_prompt = """
You are a quiz-generating AI. Given a fact, generate a multiple choice question about it.
Respond only in the following JSON format:

{
    "input": "<original input>",
    "output": [
        {
            "question": "<generated question>",
            "choices": ["<A>", "<B>", "<C>", "<D>"],
            "answer_index": <index_of_correct_choice>
        }
    ]
}

Only return valid JSON. Do not add explanations.
"""

def generate_questions(input: str):
    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input}
        ],
        "temperature": 0.7,
        "max_tokens": 512
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
            "response": content
        }

#print(type(generate_questions("Cristiano Ronaldo is the top leading goal scorer")), f'\n content: \n {generate_questions("Cristiano Ronaldo is the top leading goal scorer")}')