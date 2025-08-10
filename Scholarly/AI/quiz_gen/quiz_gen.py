"""from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")  
model = T5ForConditionalGeneration.from_pretrained("AI/models/checkpoint-64", use_safetensors=True)

input_text = "input: In Python, the print() function is used to output text to the console."
input_ids = tokenizer(input_text, return_tensors="pt").input_ids

output_ids = model.generate(input_ids, max_length=128)
output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

print("🧠 Generated:", output_text)"""
