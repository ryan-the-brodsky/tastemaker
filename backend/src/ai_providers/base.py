"""
Base abstractions for AI providers.

Defines the interface that all AI providers must implement, along with
shared data types for messages, responses, and model tiers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ModelTier(Enum):
    """
    Model capability tiers that abstract away specific model names.

    Each provider maps these tiers to their equivalent models:
    - COST_EFFECTIVE: Fast, cheap models for simple tasks (Claude Haiku, GPT-5.1-codex-mini)
    - CAPABLE: Balanced models for most tasks (Claude Sonnet, GPT-5.1)
    - FLAGSHIP: Most capable models for complex tasks (Claude Opus, GPT-5.2)
    """
    COST_EFFECTIVE = "cost_effective"
    CAPABLE = "capable"
    FLAGSHIP = "flagship"


@dataclass
class AIMessage:
    """A message in a conversation with an AI model."""
    role: str  # "user", "assistant", or "system"
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class ImageContent:
    """Image content for vision API calls."""
    data: str  # Base64-encoded image data
    media_type: str  # e.g., "image/png", "image/jpeg"

    @classmethod
    def from_base64(cls, base64_data: str, media_type: str = "image/png") -> "ImageContent":
        """Create ImageContent from base64-encoded data."""
        return cls(data=base64_data, media_type=media_type)

    @classmethod
    def from_file(cls, file_path: str) -> "ImageContent":
        """Create ImageContent from a file path."""
        import base64
        from pathlib import Path

        path = Path(file_path)
        suffix = path.suffix.lower()
        media_type = "image/png" if suffix == ".png" else "image/jpeg"

        with open(file_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        return cls(data=data, media_type=media_type)


@dataclass
class AIResponse:
    """Response from an AI model."""
    content: str  # The text content of the response
    model: str  # The actual model used
    input_tokens: int = 0
    output_tokens: int = 0
    raw_response: Optional[Any] = None  # Original provider response for debugging

    @property
    def total_tokens(self) -> int:
        """Total tokens used in the request."""
        return self.input_tokens + self.output_tokens


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    Implementations must provide:
    - complete(): Standard text completion
    - complete_with_vision(): Completion with image input
    - test_connection(): Verify API connectivity
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'anthropic', 'openai')."""
        pass

    @abstractmethod
    def complete(
        self,
        messages: List[AIMessage],
        model_tier: ModelTier = ModelTier.COST_EFFECTIVE,
        max_tokens: int = 1500,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        """
        Generate a completion from the AI model.

        Args:
            messages: List of conversation messages
            model_tier: Which tier of model to use
            max_tokens: Maximum tokens in the response
            system_prompt: Optional system prompt for context

        Returns:
            AIResponse with the generated content
        """
        pass

    @abstractmethod
    def complete_with_vision(
        self,
        text_prompt: str,
        images: List[ImageContent],
        model_tier: ModelTier = ModelTier.CAPABLE,
        max_tokens: int = 1500,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        """
        Generate a completion with image inputs (vision API).

        Args:
            text_prompt: The text prompt to send with the images
            images: List of images to analyze
            model_tier: Which tier of model to use (vision requires CAPABLE+)
            max_tokens: Maximum tokens in the response
            system_prompt: Optional system prompt for context

        Returns:
            AIResponse with the generated content
        """
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test that the API connection works.

        Returns:
            Dict with 'success' bool and relevant status info
        """
        pass

    @abstractmethod
    def get_model_for_tier(self, tier: ModelTier) -> str:
        """
        Get the actual model name for a given tier.

        Args:
            tier: The model tier

        Returns:
            The specific model identifier for this provider
        """
        pass
