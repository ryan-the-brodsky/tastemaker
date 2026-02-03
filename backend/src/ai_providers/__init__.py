"""
AI Providers Package

Provides an abstraction layer for AI model providers (Anthropic, OpenAI).
Allows switching between providers via configuration without changing application code.

Usage:
    from ai_providers import get_default_provider, AIMessage, ModelTier

    provider = get_default_provider()
    response = provider.complete(
        messages=[AIMessage(role="user", content="Hello!")],
        model_tier=ModelTier.COST_EFFECTIVE
    )
    print(response.content)
"""
from typing import Optional

from .base import AIProvider, AIMessage, AIResponse, ImageContent, ModelTier
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider

__all__ = [
    # Base types
    "AIProvider",
    "AIMessage",
    "AIResponse",
    "ImageContent",
    "ModelTier",
    # Provider implementations
    "AnthropicProvider",
    "OpenAIProvider",
    # Factory functions
    "get_provider",
    "get_default_provider",
]

# Cached default provider singleton
_default_provider: Optional[AIProvider] = None


def get_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AIProvider:
    """
    Get an AI provider instance by name.

    Args:
        provider_name: Provider name ('anthropic' or 'openai'). If not specified,
                      uses the configured default from settings.
        api_key: API key for the provider. If not specified, uses the key from settings.

    Returns:
        An AIProvider instance

    Raises:
        ValueError: If the provider is not supported or API key is missing
    """
    from config import settings

    # Determine which provider to use
    if provider_name is None:
        provider_name = _get_default_provider_name()

    provider_name = provider_name.lower()

    # Get the appropriate API key
    if provider_name == "anthropic":
        key = api_key or settings.anthropic_api_key
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured. "
                "Please add your API key to .env file. "
                "Get a key at: https://console.anthropic.com/"
            )
        return AnthropicProvider(api_key=key)

    elif provider_name == "openai":
        key = api_key or settings.openai_api_key
        if not key:
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Please add your API key to .env file. "
                "Get a key at: https://platform.openai.com/api-keys"
            )
        return OpenAIProvider(api_key=key)

    else:
        raise ValueError(
            f"Unknown AI provider: {provider_name}. "
            "Supported providers: anthropic, openai"
        )


def get_default_provider() -> AIProvider:
    """
    Get the default AI provider as a cached singleton.

    Provider selection priority:
    1. Explicit AI_PROVIDER setting (if set and API key available)
    2. Anthropic (if ANTHROPIC_API_KEY is set)
    3. OpenAI (if OPENAI_API_KEY is set)

    Returns:
        The default AIProvider instance

    Raises:
        ValueError: If no AI provider is configured
    """
    global _default_provider

    if _default_provider is None:
        provider_name = _get_default_provider_name()
        _default_provider = get_provider(provider_name)

    return _default_provider


def reset_default_provider() -> None:
    """
    Reset the cached default provider.

    Useful for testing or when settings change.
    """
    global _default_provider
    _default_provider = None


def _get_default_provider_name() -> str:
    """
    Determine the default provider name based on settings.

    Priority:
    1. Explicit AI_PROVIDER setting (if set and API key available)
    2. Anthropic (if ANTHROPIC_API_KEY is set)
    3. OpenAI (if OPENAI_API_KEY is set)
    """
    from config import settings

    # Check explicit preference
    if settings.ai_provider:
        preferred = settings.ai_provider.lower()
        # Verify the preferred provider has an API key
        if preferred == "anthropic" and settings.has_anthropic_api_key:
            return "anthropic"
        elif preferred == "openai" and settings.has_openai_api_key:
            return "openai"
        # Fall through to auto-detect if preferred provider's key isn't set

    # Auto-detect based on available API keys
    if settings.has_anthropic_api_key:
        return "anthropic"
    elif settings.has_openai_api_key:
        return "openai"

    raise ValueError(
        "No AI provider configured. "
        "Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file."
    )


def has_any_provider() -> bool:
    """
    Check if any AI provider is configured.

    Returns:
        True if at least one API key is set
    """
    from config import settings
    return settings.has_anthropic_api_key or settings.has_openai_api_key
