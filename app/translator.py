import asyncio
import logging
from typing import Dict, Tuple
import torch
from transformers import MarianMTModel, MarianTokenizer


# logger setup
logger = logging.getLogger(__name__)

# Language dictionary to multiple language from huggingFace
SUPPORTED_LANGUAGES = {
    "fr": "Helsinki-NLP/opus-mt-en-fr",  # French
    "de": "Helsinki-NLP/opus-mt-en-de",  # German
    "es": "Helsinki-NLP/opus-mt-en-es",  # Spanish
}


class Translator:
    """
    Handles loading models and running inference for MarianMT translation models.
    Models are loaded lazily and cached.
    """

    def __init__(self):
        # Cache stores (tokenizer, model) tuple by the selected language key.
        self.models: Dict[str, Tuple[MarianTokenizer, MarianMTModel]] = {}

    def get_model(self, target_language: str) -> Tuple[MarianTokenizer, MarianMTModel]:
        # Returns the tokenizer and model for the selected language.
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{target_language}' not supported. "
                f"Select from the available: {list(SUPPORTED_LANGUAGES.keys())}"
            )

        if target_language not in self.models:
            model_name = SUPPORTED_LANGUAGES[target_language]
            logger.info(f"Loading model for language '{target_language}': {model_name}")

            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            model.eval()

            self.models[target_language] = (tokenizer, model)
            logger.info(f"Model for '{target_language}' loaded and cached.")

        return self.models[target_language]

    def run_inference(self, text: str, target_language: str) -> str:
        # Full tokenize - generate - decode pipeline.
        tokenizer, model = self.get_model(target_language)

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            translated_tokens = model.generate(**inputs)

        output = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return output

    async def translate(self, text: str, target_language: str) -> str:
        # Async interface for translation.
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.run_inference,
            text,
            target_language,
        )
        return result

    @property
    def supported_languages(self) -> Dict[str, str]:
        # Show supported languages.
        return SUPPORTED_LANGUAGES



    
