from __future__ import annotations

from typing import Optional

from .base import ImageProvider
from .openai_compatible import OpenAICompatibleImageProvider


def create_image_provider(*, api_key: Optional[str], base_url: Optional[str]) -> ImageProvider:
    return OpenAICompatibleImageProvider(api_key=api_key, base_url=base_url)
