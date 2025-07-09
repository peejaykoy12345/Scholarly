from transformers.pipelines import pipeline

#summarize_long_text = pipeline("summarization", model="pszemraj/led-large-book-summary")
#summarize_medium_sized_text = pipeline("summarization", model="facebook/bart-large-cnn")
summarize_short_sized_text = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return "No input provided"
    try:
        #if len(text.strip()) <= 30:
        return summarize_short_sized_text(text)[0]['summary_text']
        #if len(text.strip()) <= 4000:
            #return summarize_medium_sized_text(text)[0]['summary_text']
        #else:
            #return summarize_long_text(text)[0]['summary_text']
    except Exception as e:
        return f"Error summarizing: {str(e)}"
    
    
