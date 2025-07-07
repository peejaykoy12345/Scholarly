from transformers.pipelines import pipeline

summarize = pipeline("summarization", model="pszemraj/led-large-book-summary")

def summarize_text(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return "No input provided"
    try:
        return summarize(text)[0]['summary_text']
    except Exception as e:
        return f"Error summarizing: {str(e)}"
    
# Unused for now
'''def split_text(text, max_chars=1000):
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        chunks.append(text[start:end])
        start = end

    return chunks
    
def summarize_long_text(text: str) -> str:
    chunks = split_text(text)
    summarized = []
    summarized_text = ""

    for _, chunk in enumerate(chunks):
        summarized.append(summarize_text(chunk))

    for i in range(len(summarized)):
        summarized_text +=  summarized[i] 

    return summarized_text if len(summarized) > 0 else "None"'''

