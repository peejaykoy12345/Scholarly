from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import load_dataset

model_name = 'google/flan-t5-small'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

dataset = load_dataset('json', data_files='datasets/quiz_training.json')

def tokenize(batch):
    return tokenizer(batch['input'], text_target=batch['output'], truncation=True, padding='max_length', max_length=512)

tokenized = dataset.map(tokenize, batched=True)
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
    train_dataset=tokenized['train']
)

trainer.train()