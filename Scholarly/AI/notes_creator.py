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
    system_prompt = f"""
        You are an AI assistant that generates study notes using the "{notes_type}" note-taking method.

        Instructions:

        If the method is "Cornell":
        - Format the output in two clearly labeled sections:
        Cue Column:
        - (Helpful questions based on the input)
        - Do NOT include the summarization part as it is handle by another function
        
        Note-taking Area:
        - (Answers to the questions above, in the same order)

        If the method is "Outline":
        - Format the output using hierarchical bullet points like:
        - Main idea
            - Supporting detail
            - Supporting detail

        If the method is "Summarize":
        - Summarize it but dont remove the key ideas

        Rules:
        ❌ Do NOT explain the method.
        ❌ Do NOT include summaries, commentary, or greetings.
        ❌ Do NOT use special formatting such as ##, **, ``` or any other formatting styles that cant be read by an ordinary text editor
        ✅ Just return the notes in the correct format based on the specified method.
        ✅ Each word or letter should be able to be read by a normal text editor
        ✅ If needing bullet points use - as bullet points e.g:
            - Dog
            - Cat
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
    if method == "Extract Text":
        return text

    chunks = split_text(text)
    all_notes = []

    if method == "Summarize":

        for chunk in chunks:
            summary = summarize(chunk)
            all_notes.append(summary)
        return "\n".join(all_notes)

    else:
        for chunk in chunks:
            note = generate_notes(chunk, method)
            all_notes.append(note)

        combined_notes = "\n".join(all_notes)

        if method == "Cornell method":
            summary = summarize(text)  
            return combined_notes + "\n\nSummary:\n" + summary

        return combined_notes

