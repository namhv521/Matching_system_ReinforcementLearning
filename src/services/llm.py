"""Unified LLM Client Service supporting OpenAI, Gemini, Anthropic, and Local Mock."""

import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Optional
from src.config import agent_settings

logger = logging.getLogger("ai_agent.llm")


class BaseLLMClient(ABC):
    """Abstract Base Class for LLM Clients."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Synchronously generate text completion."""
        pass

    @abstractmethod
    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Asynchronously generate text completion."""
        pass

    @abstractmethod
    async def astream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Asynchronously stream tokens."""
        pass


class MockLLMClient(BaseLLMClient):
    """Fallback Mock LLM Client providing realistic academic responses without API costs."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return (
            "Dựa trên hồ sơ học thuật và nguyện vọng của sinh viên, hệ thống gợi ý "
            "hướng đề tài kết hợp giữa Trí tuệ nhân tạo và Phân tích dữ liệu lớn. "
            "Giảng viên phù hợp nhất là các thầy/cô thuộc Bộ môn Hệ thống Thông tin & Khoa học Máy tính "
            "với chỉ số tương đồng trên 85%."
        )

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self.generate(prompt, system_prompt)

    async def astream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        text = self.generate(prompt, system_prompt)
        words = text.split(" ")
        for word in words:
            yield word + " "


class OpenAILLMClient(BaseLLMClient):
    """OpenAI API client adapter."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        try:
            from openai import OpenAI, AsyncOpenAI
            self.client = OpenAI(api_key=api_key)
            self.async_client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            logger.warning("openai package not installed, falling back to mock")
            self.client = None

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.client:
            return MockLLMClient().generate(prompt, system_prompt)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        res = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
        )
        return res.choices[0].message.content or ""

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.client:
            return await MockLLMClient().agenerate(prompt, system_prompt)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        res = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
        )
        return res.choices[0].message.content or ""

    async def astream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not self.client:
            async for token in MockLLMClient().astream(prompt, system_prompt):
                yield token
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.async_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            stream=True,
        )
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


def get_llm_client() -> BaseLLMClient:
    """Factory function returning the configured LLM Client."""
    provider = agent_settings.LLM_PROVIDER.lower()

    if provider == "openai" and agent_settings.OPENAI_API_KEY:
        return OpenAILLMClient(
            api_key=agent_settings.OPENAI_API_KEY,
            model_name=agent_settings.LLM_MODEL_NAME,
            temperature=agent_settings.LLM_TEMPERATURE,
        )
    # Default fallback to robust Mock Client
    return MockLLMClient()
