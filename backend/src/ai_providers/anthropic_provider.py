"""
Anthropic Claude AI provider implementation.

Wraps the Anthropic SDK to implement the AIProvider interface.
"""
from typing import List, Optional, Dict, Any

import anthropic

from .base import AIProvider, AIMessage, AIResponse, ImageContent, ModelTier


class AnthropicProvider(AIProvider):
    """
    Anthropic Claude provider implementation.

    Model tier mapping:
    - COST_EFFECTIVE: claude-haiku-4-5-20251001 (fast, cheap)
    - CAPABLE: claude-sonnet-4-6 (balanced)
    - FLAGSHIP: claude-opus-4-6 (most capable)
    """

    # Model mapping for each tier
    MODEL_MAP = {
        ModelTier.COST_EFFECTIVE: "claude-haiku-4-5-20251001",
        ModelTier.CAPABLE: "claude-sonnet-4-6",
        ModelTier.FLAGSHIP: "claude-opus-4-6",
    }

    def __init__(self, api_key: str):
        """
        Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key
        """
        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def name(self) -> str:
        return "anthropic"

    def get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the Claude model name for a tier."""
        return self.MODEL_MAP[tier]

    def complete(
        self,
        messages: List[AIMessage],
        model_tier: ModelTier = ModelTier.COST_EFFECTIVE,
        max_tokens: int = 1500,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        """
        Generate a completion using Claude.

        Anthropic API uses a separate 'system' parameter rather than including
        system messages in the messages array.
        """
        model = self.get_model_for_tier(model_tier)

        # Convert messages to Anthropic format (excluding system messages)
        anthropic_messages = []
        for msg in messages:
            if msg.role != "system":
                anthropic_messages.append({"role": msg.role, "content": msg.content})

        # Build API call kwargs
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": anthropic_messages,
        }

        # Add system prompt if provided
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)

        return AIResponse(
            content=response.content[0].text,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            raw_response=response,
        )

    def complete_with_vision(
        self,
        text_prompt: str,
        images: List[ImageContent],
        model_tier: ModelTier = ModelTier.CAPABLE,
        max_tokens: int = 1500,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        """
        Generate a completion with image inputs using Claude Vision.

        Claude's vision API accepts images as part of the message content array.
        """
        model = self.get_model_for_tier(model_tier)

        # Build content array with images first, then text
        content = []

        for image in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image.media_type,
                    "data": image.data,
                }
            })

        content.append({
            "type": "text",
            "text": text_prompt,
        })

        # Build API call kwargs
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)

        return AIResponse(
            content=response.content[0].text,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            raw_response=response,
        )

    def test_connection(self) -> Dict[str, Any]:
        """Test the Anthropic API connection."""
        try:
            model = self.get_model_for_tier(ModelTier.COST_EFFECTIVE)
            response = self._client.messages.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}]
            )
            return {
                "success": True,
                "provider": self.name,
                "message": response.content[0].text,
                "model": model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            }
        except anthropic.APIError as e:
            return {
                "success": False,
                "provider": self.name,
                "error": str(e),
            }
        except Exception as e:
            return {
                "success": False,
                "provider": self.name,
                "error": f"Unexpected error: {str(e)}",
            }
