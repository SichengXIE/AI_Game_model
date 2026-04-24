from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Mapping

from .contracts import ChatRequest, ChatResponse, ProviderConfig


class OpenAICompatibleClient:
    def __init__(self, provider: ProviderConfig):
        self.provider = provider

    def build_payload(self, request: ChatRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model or self.provider.default_model,
            "messages": [message.to_payload() for message in request.messages],
        }

        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.response_format is not None:
            payload["response_format"] = request.response_format

        payload.update(dict(self.provider.extra_body))
        payload.update(dict(request.extra_body))
        return payload

    def complete(self, request: ChatRequest) -> ChatResponse:
        api_key = os.environ.get(self.provider.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing API key environment variable: {self.provider.api_key_env}"
            )

        payload = self.build_payload(request)
        raw_response = self._post_json(
            url=self._chat_completions_url(),
            payload=payload,
            api_key=api_key,
            timeout_seconds=self.provider.timeout_seconds,
            extra_headers=self.provider.extra_headers,
        )
        content = _extract_message_content(raw_response)
        return ChatResponse(
            provider_id=self.provider.id,
            model=str(payload["model"]),
            content=content,
            raw=raw_response,
        )

    def _chat_completions_url(self) -> str:
        return f"{self.provider.base_url.rstrip('/')}/chat/completions"

    @staticmethod
    def _post_json(
        url: str,
        payload: Mapping[str, Any],
        api_key: str,
        timeout_seconds: int,
        extra_headers: Mapping[str, str],
    ) -> Mapping[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **dict(extra_headers),
        }
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            response_body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Provider request failed with HTTP {error.code}: {response_body}"
            ) from error


def _extract_message_content(raw_response: Mapping[str, Any]) -> str:
    choices = raw_response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("Provider response did not include choices.")

    first_choice = choices[0]
    if not isinstance(first_choice, Mapping):
        raise RuntimeError("Provider response choice is not an object.")

    message = first_choice.get("message")
    if not isinstance(message, Mapping):
        raise RuntimeError("Provider response choice did not include a message.")

    content = message.get("content")
    if not isinstance(content, str):
        raise RuntimeError("Provider response message content is not text.")

    return content
