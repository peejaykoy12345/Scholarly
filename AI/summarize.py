from transformers.pipelines import pipeline

#summarize_long_text = pipeline("summarization", model="pszemraj/led-large-book-summary")
#summarize_medium_sized_text = pipeline("summarization", model="facebook/bart-large-cnn")
summarize_short_sized_text = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return "No input provided"
    try:
        result = summarize_short_sized_text(text)
        print("Summarizer raw result:", result)
        if not result:
            return "⚠️ Summarizer returned nothing."
        return result[0]['summary_text']
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Error summarizing: {str(e)}"
    
def split_text(text, max_chars=1000):
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

    return summarized_text if len(summarized) > 0 else "None"