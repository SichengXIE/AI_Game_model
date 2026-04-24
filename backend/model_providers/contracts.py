from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Optional, Sequence


Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str

    def to_payload(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class ChatRequest:
    messages: Sequence[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    response_format: Optional[Mapping[str, Any]] = None
    extra_body: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatResponse:
    provider_id: str
    model: str
    content: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class ProviderConfig:
    id: str
    display_name: str
    api_style: Literal["openai_chat_completions"]
    base_url: str
    api_key_env: str
    default_model: str
    enabled: bool = True
    supports_json_schema: bool = False
    supports_streaming: bool = False
    timeout_seconds: int = 60
    extra_headers: Mapping[str, str] = field(default_factory=dict)
    extra_body: Mapping[str, Any] = field(default_factory=dict)
    notes: Sequence[str] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ProviderConfig":
        return cls(
            id=str(data["id"]),
            display_name=str(data["display_name"]),
            api_style="openai_chat_completions",
            base_url=str(data["base_url"]),
            api_key_env=str(data["api_key_env"]),
            default_model=str(data["default_model"]),
            enabled=bool(data.get("enabled", True)),
            supports_json_schema=bool(data.get("supports_json_schema", False)),
            supports_streaming=bool(data.get("supports_streaming", False)),
            timeout_seconds=int(data.get("timeout_seconds", 60)),
            extra_headers=dict(data.get("extra_headers", {})),
            extra_body=dict(data.get("extra_body", {})),
            notes=tuple(data.get("notes", ())),
        )
