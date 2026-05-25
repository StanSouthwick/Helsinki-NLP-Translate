from pydantic import BaseModel, Field
from typing import Dict

# Define expected input for the translation endpoint
class TranslationRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=512,
        description="The text to be translated. Must be between 1 and 512 characters to match the tokenizer's max_length.",
        json_schema_extra={"example": "Hello world!"}
    )
    target_language: str = Field(
        description="The target language for translation. Must be one of the supported languages.",
        json_schema_extra={"example": "fr"}
    )

class TranslationResponse(BaseModel):
    # Define the expected output for the translation endpoint
    original_text: str = Field(
        description="The original text that was translated.",
        json_schema_extra={"example": "Hello world!"}
    )
    translated_text: str = Field(
        description="The translated text in the target language.",
        json_schema_extra={"example": "Bonjour le monde!"}
    )
    target_language: str = Field(
        description="The target language for translation.",
        json_schema_extra={"example": "fr"}
    )
    model_used: str = Field(
        description="The name of the model used for translation.",
        json_schema_extra={"example": "Helsinki-NLP/opus-mt-en-fr"}
    )

class LanguagesResponse(BaseModel):
    # Define the expected output for the supported languages endpoint
    supported_languages: Dict = Field(
        description="A map of supported target languages for translation.",
        json_schema_extra={"example": {
            "fr": "Helsinki-NLP/opus-mt-en-fr",
            "de": "Helsinki-NLP/opus-mt-en-de",
            "es": "Helsinki-NLP/opus-mt-en-es"
        }})