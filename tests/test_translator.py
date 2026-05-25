import pytest
from unittest.mock import MagicMock, patch

from app.translator import Translator, SUPPORTED_LANGUAGES

def test_supported_languages():
    """
    Test that the supported languages property returns the expected dictionary.
    """
    assert "fr" in SUPPORTED_LANGUAGES
    assert "de" in SUPPORTED_LANGUAGES
    assert "es" in SUPPORTED_LANGUAGES

    assert SUPPORTED_LANGUAGES["fr"] == "Helsinki-NLP/opus-mt-en-fr"
    assert SUPPORTED_LANGUAGES["de"] == "Helsinki-NLP/opus-mt-en-de"
    assert SUPPORTED_LANGUAGES["es"] == "Helsinki-NLP/opus-mt-en-es"

def test_model_cached_after_first_load():
    """
    Test that the model is cached after the first load.
    The _get_model method should only load the model once per language.
    """
    translator = Translator()

    # Mock the from_pretrained methods to track calls
    with patch("app.translator.MarianTokenizer.from_pretrained", return_value=MagicMock()) as mock_tokenizer, \
         patch("app.translator.MarianMTModel.from_pretrained", return_value=MagicMock()) as mock_model:

        mock_model.return_value = MagicMock()
        mock_tokenizer.return_value = MagicMock()

        # Call _get_model twice for the same language to load and then use the cached model
        translator._get_model("fr")
        translator._get_model("fr")

        # The from_pretrained methods should only be called once for the same language
        assert mock_tokenizer.call_count == 1
        assert mock_model.call_count == 1
        