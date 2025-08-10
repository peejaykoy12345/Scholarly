"""from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import load_dataset

model_name = 'google/flan-t5-small'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer.save_pretrained("models")
print('tokenizersaved')

dataset = load_dataset('json', data_files='AI/datasets/quiz_training.json')

def preprocess(example):
    qa = example['output'][0]
    question = qa['question']
    choices = qa['choices']
    answer_index = qa['answer_index']
    output_str = f"Q: {question}\nOptions: {', '.join(choices)}\nAnswer: {choices[answer_index]}"
    return {
        "input": example["input"],
        "output": output_str,
        "correct_index": answer_index
    }

processed = dataset['train'].map(preprocess)

def tokenize(batch):
    inputs = batch["input"]
    targets = batch["output"]
    if isinstance(inputs, str):
        inputs = [inputs]
    if isinstance(targets, str):
        targets = [targets]
    return tokenizer(inputs, text_target=targets, truncation=True, padding="max_length", max_length=512)

tokenized = processed.map(tokenize, batched=True)
tokenized.set_format('torch')

args = TrainingArguments(
    output_dir='models',
    per_device_train_batch_size=4,
    num_train_epochs=4,
    save_steps=500,
    logging_dir='logs',
    logging_steps=50
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized
)

trainer.train()"""