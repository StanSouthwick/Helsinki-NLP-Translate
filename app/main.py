import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas import LanguagesResponse, TranslationRequest, TranslationResponse
from app.translator import Translator
from app.safeguards import check_input, check_output
from app.monitoring import instrument_app
from app.schemas import EvaluationRequest, EvaluationResponse
from app.evaluation import calculate_bleu, interpret_bleu

# Configure logging for the whole application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Manages application startup and shutdown.
    # Translator created once and shared across all requests via app.state.
    
    logger.info("Starting up the translation service...")
    app.state.translator = Translator()
    logger.info("Translator initialised and ready.")

    yield  # Application runs here — handling requests

    # Shutdown — release resources, close connections if needed
    logger.info("Shutting down the translation service...")


# Create the FastAPI application instance
app = FastAPI(
    title="Helsinki-NLP Translation API",
    description="Production translation API using MarianMT — Helsinki-NLP OPUS-MT models",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach Prometheus monitoring — automatically adds GET /metrics endpoint
instrument_app(app)

# 3 endpoints: health, supported languages, translate


@app.get("/health")
async def health_check():
    
    # Simple liveness check.
    # Load balancers and orchestrators ping this to verify the service is alive.
    
    return {"status": "healthy"}


@app.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages(request: Request):
    """
    Returns all supported language codes and their model identifiers.
    """
    translator = request.app.state.translator
    return LanguagesResponse(
        supported_languages=translator.supported_languages
    )

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: Request, request_body: TranslationRequest):
    """
    Main translation endpoint.
    Accepts English text and a target language code.
    Returns translated text with metadata.
    """
    translator = request.app.state.translator

    # Validate language is supported before anything else
    # Explicit early check prevents KeyError downstream
    if request_body.target_language not in translator.supported_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{request_body.target_language}' not supported. "
                   f"Choose from: {list(translator.supported_languages.keys())}"
        )

    # Validate input is safe before sending to the model
    check_input(request_body.text)

    try:
        translated_text = await translator.translate(
            text=request_body.text,
            target_language=request_body.target_language,
        )
    except ValueError as e:
        # Fallback error handling for any unexpected ValueError
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Validate output is safe before returning to caller
    check_output(translated_text)

    # Safe to look up now — language already validated above
    model_used = translator.supported_languages[request_body.target_language]

    return TranslationResponse(
        original_text=request_body.text,
        translated_text=translated_text,
        target_language=request_body.target_language,
        model_used=model_used,
    )

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_translation(request_body: EvaluationRequest):
    """
    Evaluates a machine translation against a human reference using BLEU score.
    Returns the BLEU score and an interpretation of the translation quality.
    """
    bleu_score = calculate_bleu(
        translated_text=request_body.translated_text,
        reference_text=request_body.reference_text,
    )
    interpretation = interpret_bleu(bleu_score)

    return EvaluationResponse(
        source_text=request_body.source_text,
        translated_text=request_body.translated_text,
        reference_text=request_body.reference_text,
        bleu_score=bleu_score,
        interpretation=interpretation,
    )
    return EvaluationResponse(
        source_text=request_body.source_text,
        translated_text=request_body.translated_text,
        reference_text=request_body.reference_text,
        bleu_score=bleu_score,
        interpretation=interpretation,
    )
        
    
