# src/services/bedrock_service.py
import boto3
import json
import logging
import os

from src.services.inventory_service import get_all_products, build_context

logger = logging.getLogger(__name__)

REGION   = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20240620-v1:0")
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

SYSTEM_PROMPT = (
    "You are a senior inventory analyst AI assistant. "
    "You provide concise, accurate, data-driven recommendations. "
    "You only use the inventory data provided - never invent products or stock levels. "
    "Always respond in English unless instructed otherwise."
)


def _call_bedrock(prompt: str, max_tokens: int = 600) -> str:
    try:
        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {"role": "user", "content": [{"text": prompt}]}
            ],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": 0.3,
            }
        )

        content = response["output"]["message"]["content"][0]["text"]

        if not content or not content.strip():
            return "The AI returned an empty response. Please try again."

        logger.info(f"Bedrock response - model: {MODEL_ID}, tokens: {response['usage']}")
        return content.strip()

    except Exception as e:
        logger.error(f"Bedrock error: {e}")
        return f"AI service temporarily unavailable: {type(e).__name__}"


def get_bedrock_summary() -> dict:
    inventory = get_all_products()

    if not inventory:
        return {"summary": "No inventory data available.", "source": "bedrock"}

    context = build_context(inventory)
    prompt = (
        "Analyze this inventory and provide a concise executive summary (3-4 sentences max):\n\n"
        f"{context}\n\n"
        "Cover: overall inventory health, top risks, and the single most important action to take now."
    )

    return {
        "summary": _call_bedrock(prompt),
        "source":  "bedrock",
        "model":   MODEL_ID
    }


def get_bedrock_copilot(question: str) -> dict:
    if not question or not question.strip():
        return {"answer": "Please provide a question.", "source": "bedrock"}

    inventory = get_all_products()

    if not inventory:
        return {"answer": "No inventory data available.", "source": "bedrock"}

    context = build_context(inventory)
    prompt = (
        f"Inventory data:\n{context}\n\n"
        "Classification rules:\n"
        "- stock == 0 -> CRITICAL (restock immediately)\n"
        "- stock < reorder_level -> HIGH RISK (restock soon)\n"
        "- stock >= reorder_level -> OK (monitor)\n\n"
        f"User question: {question.strip()}\n\n"
        "Respond using this structure:\n"
        "1. CRITICAL PRODUCTS (if any) - product -> action + reason\n"
        "2. HIGH RISK PRODUCTS (if any) - product -> action + reason\n"
        "3. OK PRODUCTS - product -> status\n"
        "4. RECOMMENDATION - one clear action to take now\n\n"
        "Be concise. Only reference products from the data above."
    )

    return {
        "answer": _call_bedrock(prompt),
        "source": "bedrock",
        "model":  MODEL_ID
    }