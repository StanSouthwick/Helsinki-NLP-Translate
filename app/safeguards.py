import logging
import re

from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Patterns that suggest prompt injection attempts
# Someone embedding instructions in the input to manipulate the model
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"disregard.*instructions",
    r"you are now",
    r"act as",
    r"pretend you",
    r"system prompt",
]

def check_input(text: str) -> None:
    """
    Checks the input text for potential prompt injection patterns.
    Raises HTTPException with 400 status if any suspicious patterns are found.
    """
    # Check 1 - empty or whitespace-only input
    if not text.strip():
        logger.warning("Received empty or whitespace-only input.")
        raise HTTPException(status_code=422,
                            detail="Input text cannot be empty."
                            )
    # Check 2 - input that is too long for the model
    if len(text) > 512:
        logger.warning(f"Received input that exceeds max length: {len(text)} characters.")
        raise HTTPException(status_code=422,
                            detail="Input text exceeds maximum length of 512 characters."
                            )
    # Check 3 - patterns that suggest prompt injection attempts
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"Potential prompt injection detected in input: '{text}'")
            raise HTTPException(status_code=422,
                                detail="Input contains disallowed content"
                                )
    logger.info("Input text passed safety checks.")

def check_output(text: str) -> None:
    """
    Checks the output text for potential issues before returning to the caller.
    Raises HTTPException with 500 status if any suspicious patterns are found.
    """
    # Check 1 - empty or whitespace-only output (model failed to generate a response)
    if not text.strip():
        logger.error("Model generated empty or whitespace-only output.")
        raise HTTPException(status_code=500,
                            detail="Model failed to generate a valid translation."
                            )
    
    # Check 2 - output that is too long (unexpectedly verbose response)
    if len(text) > 512:
        logger.error(f"Model generated output that exceeds max length: {len(text)} characters.")
        raise HTTPException(status_code=500,
                            detail="Model generated output exceeds maximum expected length."
                            )
    
    # Check 3 - output too short (model may have failed to translate properly)
    if len(text) < 5:
        logger.error(f"Model generated output that is unexpectedly short: '{text}'")
        raise HTTPException(status_code=500,
                            detail="Model generated output is too short to be a valid translation."
                            )
    
    logger.info("Output text passed safety checks.")