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

def generate_notes(input: str, notes_type: str) -> str:
    system_prompt = """
You are an AI assistant that generates study notes based on a specified note-taking method.

Currently, only the Cornell note-taking method is supported.

When the user provides input material and specifies "Cornell" as the notes_type, return the notes in a Cornell-style format excluding the summary.

Format the output with two clear sections:
Cue Column:
- (a list of helpful questions derived from the input)

Note-taking Area:
- (answers to the questions written above, aligned in the same order)

⚠️ Do not include summaries.
❌ Do not explain the Cornell method.
❌ Do not add commentary, greetings, or titles.
✅ Just generate helpful Q&A pairs from the content.

Example:
---
Cue Column:
- What is gravity?
- Why do objects fall to Earth?
- How does gravity affect space?

Note-taking Area:
- Gravity is a force that pulls objects toward one another.
- Objects fall to Earth due to the gravitational pull of the planet.
- Gravity affects the orbits of planets and the motion of galaxies.
---
"""

    if notes_type != "Cornell method":
        return "Error: Unsupported note-taking method."

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

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error generating notes: {response.status_code} - {response.text}"

def split_text(text: str, chunk_size: int = 1000): 
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def summarize(text: str) -> str:
    summary_prompt = """
You are a helpful AI that summarizes large chunks of academic or technical text.

Given the input, produce a clear, concise summary in 2–4 sentences. 
Avoid repeating the structure or formatting of the original input. 
Focus on core ideas and main takeaways. No titles, no commentary.
"""

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.5,
        "max_tokens": 4096
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error generating summary: {response.status_code} - {response.text}"

def generate_notes_using_ai(text: str, method: str) -> str:
    chunks = split_text(text)
    all_notes = []

    for chunk in chunks:
        note = generate_notes(chunk, method)
        all_notes.append(note)

    combined_notes = "\n".join(all_notes)

    if method == "Cornell method":
        summary = summarize(text)
        return combined_notes + "\n\nSummary:\n" + summary
    
    return combined_notes
