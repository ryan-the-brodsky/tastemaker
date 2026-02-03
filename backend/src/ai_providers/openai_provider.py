"""
OpenAI GPT AI provider implementation.

Wraps the OpenAI SDK to implement the AIProvider interface.
"""
from typing import List, Optional, Dict, Any

import openai

from .base import AIProvider, AIMessage, AIResponse, ImageContent, ModelTier


class OpenAIProvider(AIProvider):
    """
    OpenAI GPT provider implementation.

    Model tier mapping:
    - COST_EFFECTIVE: gpt-4o-mini (fast, cheap)
    - CAPABLE: gpt-4o (balanced)
    - FLAGSHIP: gpt-4o (most capable - same as CAPABLE for now)

    Note: Model names may need updating as OpenAI releases newer models.
    """

    # Model mapping for each tier
    MODEL_MAP = {
        ModelTier.COST_EFFECTIVE: "gpt-4o-mini",
        ModelTier.CAPABLE: "gpt-4o",
        ModelTier.FLAGSHIP: "gpt-4o",  # Update when GPT-5 is available
    }

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
        """
        self._client = openai.OpenAI(api_key=api_key)

    @property
    def name(self) -> str:
        return "openai"

    def get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the GPT model name for a tier."""
        return self.MODEL_MAP[tier]

    def complete(
        self,
        messages: List[AIMessage],
        model_tier: ModelTier = ModelTier.COST_EFFECTIVE,
        max_tokens: int = 1500,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        """
        Generate a completion using GPT.

        OpenAI API accepts system messages as the first message in the array.
        """
        model = self.get_model_for_tier(model_tier)

        # Build messages array with system prompt first if provided
        openai_messages = []

        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            if msg.role == "system" and system_prompt:
                # Skip system messages if we already added system_prompt
                continue
            openai_messages.append({"role": msg.role, "content": msg.content})

        response = self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=openai_messages,
        )

        return AIResponse(
            content=response.choices[0].message.content,
            model=model,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
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
        Generate a completion with image inputs using GPT Vision.

        OpenAI's vision API uses a content array with image_url objects.
        Base64 images are passed as data URLs.
        """
        model = self.get_model_for_tier(model_tier)

        # Build content array with images first, then text
        content = []

        for image in images:
            # OpenAI expects data URLs for base64 images
            data_url = f"data:{image.media_type};base64,{image.data}"
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": data_url,
                }
            })

        content.append({
            "type": "text",
            "text": text_prompt,
        })

        # Build messages array
        openai_messages = []

        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        openai_messages.append({"role": "user", "content": content})

        response = self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=openai_messages,
        )

        return AIResponse(
            content=response.choices[0].message.content,
            model=model,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            raw_response=response,
        )

    def test_connection(self) -> Dict[str, Any]:
        """Test the OpenAI API connection."""
        try:
            model = self.get_model_for_tier(ModelTier.COST_EFFECTIVE)
            response = self._client.chat.completions.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}]
            )
            return {
                "success": True,
                "provider": self.name,
                "message": response.choices[0].message.content,
                "model": model,
                "tokens_used": (response.usage.prompt_tokens + response.usage.completion_tokens) if response.usage else 0,
            }
        except openai.APIError as e:
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
