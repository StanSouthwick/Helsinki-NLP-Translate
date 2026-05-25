from transformers import MarianMTModel, MarianTokenizer

models = [
    "Helsinki-NLP/opus-mt-en-fr",
    "Helsinki-NLP/opus-mt-en-de",
    "Helsinki-NLP/opus-mt-en-es",
]

for model_name in models:
    print(f"Downloading {model_name}...")
    MarianMTModel.from_pretrained(model_name)
    MarianTokenizer.from_pretrained(model_name)
    print(f"Downloaded {model_name}")

print("All models downloaded successfully")