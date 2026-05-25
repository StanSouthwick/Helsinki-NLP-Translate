import logging

import sacrebleu

logger = logging.getLogger(__name__)


def interpret_bleu(score: float) -> str:
    """
    Converts a raw BLEU score into a human readable interpretation.
    Thresholds based on standard MT research conventions.
    """
    if score >= 0.7:
        return "Excellent — very close to human translation quality"
    elif score >= 0.5:
        return "Good — mostly accurate with minor differences"
    elif score >= 0.3:
        return "Reasonable — meaning preserved but phrasing differs"
    elif score >= 0.1:
        return "Poor — significant translation errors present"
    else:
        return "Very poor — translation does not match reference"


def calculate_bleu(translated_text: str, reference_text: str) -> float:
    """
    Calculates BLEU score between a machine translation and a human reference.
    sacrebleu expects a list of hypotheses and a list of reference lists.
    Returns a float between 0 and 1 — normalised from sacrebleu's 0-100 scale.
    """
    result = sacrebleu.corpus_bleu(
        hypotheses=[translated_text],
        references=[[reference_text]]
    )

    # sacrebleu returns 0-100, normalise to 0-1 for consistency
    normalised = round(result.score / 100, 4)
    logger.info(f"BLEU score calculated: {normalised} — {interpret_bleu(normalised)}")
    return normalised
