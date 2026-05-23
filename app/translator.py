import asyncio
import logging
from functools import lru_cache
from typing import Optional
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
    Handels Loading model and inference of MarianMT tranlation models for selected language
    Models are laoded when called and cached 
    Statup is fast and models and loaded when slected
    """

    def __init__(self):
        # Cache stores (tokenizer, model) tupel by the keyed selected langauge 
        self.models: dict = {}
    
    def get_model (
            self, target_language: str
    ) -> tuple[MarianTokenizer, MarianMTModel]:
         # Returns the Tokenizer and model for the selected model

         if target_language not in SUPPORTED_LANGUAGES:
             raise ValueError(
                 f"Language "{target_language}" not supported. "
                 f"Select from the available: "{list(SUPPORTED_LANGUAGES.keys())}
             )
         
         # Loads into cache if not already in there
         if target_language not in self.models:
             model_name = SUPPORTED_LANGUAGES[target_language]
             logger.info(f"Loading model for language "{target_language}": " {model_name})

             tokenizer = MarianTokenizer.from_pretrained(model_name)
             model = MarianMTModel.from_pretrained(model_name)

             # Eval model to disable droput layers that is only needed for training
             # Otehrwise different outputs each call
             model.eval()

             self.models[target_language] = (tokenizer, model)
             logger.info(f"Model for "{target_language}" laoded and cached.")

        return self.models[target_language]

    def run_inference (self, text: str, target_language: str) -> str:
        # Full tokenise - generate - decode pipeline 
        # Synchronous function to be called in run_in_executor

        tokenizer, model = self.get_model(target_language)

        # Tokenise the input message
        #return_tensors="pt" - returns PyTorch tensors
        # padding handles batches of different lengths
        # truncation prevents errors of long inputs

        inputs = tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512

        )
             
    # Disable gradient to reduce memory usage and improve speeds 
    # Inference not training

        with torch.no_grad():
            translated_token = model.generate(**inputs)
        
        # Decode output tokens into readable string - special toekn removes end-of-sequence marker
        output = tokenizer.decode(translated_toekns[0], skip_special_toekns=True)
        return result
    
    async def translate(self, text: str, target_language: str) -> str:
        # async interface for translate
        # offloads CPU-bound inference to thread pool using run_in_executor so no blockages happen

        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            None,
            self.run_inference,
            text,
            target_language

        )
        return result
    
    @property
    def_supported_languages(self) -> dict:
        # Show supported languages
        return SUPPORTED_LANGUAGES



    
