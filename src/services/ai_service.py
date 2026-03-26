# src/services/ai_service.py
import logging
from openai import OpenAI, OpenAIError
from src.services.inventory_service import get_all_products, build_context

logger = logging.getLogger(__name__)
client = OpenAI()  # Lee OPENAI_API_KEY del entorno automáticamente

SYSTEM_PROMPT = """You are a senior inventory analyst AI assistant.
You provide concise, accurate, data-driven recommendations.
You only use the inventory data provided — never invent products or stock levels.
Always respond in English unless instructed otherwise."""


def _call_openai(messages: list[dict], max_tokens: int = 600) -> str:
    """
    Wrapper centralizado para llamadas a OpenAI.
    Maneja errores de red, rate limits y respuestas vacías.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,  # Más consistente — menos "creativo"
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            return "The AI returned an empty response. Please try again."
        return content.strip()
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return f"AI service temporarily unavailable. Error: {type(e).__name__}"
    except Exception as e:
        logger.error(f"Unexpected error calling OpenAI: {e}")
        return "An unexpected error occurred. Please try again."


def get_ai_summary() -> dict:
    """Genera un resumen ejecutivo del estado del inventario."""
    inventory = get_all_products()

    if not inventory:
        return {"summary": "No inventory data available to analyze."}

    context = build_context(inventory)
    prompt = f"""Analyze this inventory and provide a concise executive summary (3-4 sentences max):

{context}

Cover: overall inventory health, top risks, and the single most important action to take now."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    return {"summary": _call_openai(messages)}


def get_copilot_answer(question: str) -> dict:
    """Responde preguntas sobre el inventario con contexto completo."""
    if not question or not question.strip():
        return {"answer": "Please provide a question."}

    inventory = get_all_products()

    if not inventory:
        return {"answer": "No inventory data available."}

    context = build_context(inventory)
    prompt = f"""Inventory data:
{context}

Classification rules:
- stock == 0 → CRITICAL (restock immediately)
- stock < reorder_level → HIGH RISK (restock soon)
- stock >= reorder_level → OK (monitor)

User question: {question.strip()}

Respond using this structure:
1. CRITICAL PRODUCTS (if any) — product → action + reason
2. HIGH RISK PRODUCTS (if any) — product → action + reason
3. OK PRODUCTS — product → status
4. RECOMMENDATION — one clear action to take now

Be concise. Only reference products from the data above."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    return {"answer": _call_openai(messages)}