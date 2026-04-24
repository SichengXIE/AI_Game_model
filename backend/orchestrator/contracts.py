from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Optional, Sequence


OrchestrationStatus = Literal["ready", "needs_clarification", "invalid"]


@dataclass(frozen=True)
class ClarifyingQuestion:
    id: str
    question: str
    reason: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ClarifyingQuestion":
        return cls(
            id=str(data.get("id", "")),
            question=str(data.get("question", "")),
            reason=str(data.get("reason", "")),
        )


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class OrchestrationRequest:
    user_prompt: str
    provider_id: Optional[str] = None
    model: Optional[str] = None
    user_constraints: Mapping[str, Any] = field(default_factory=dict)
    existing_answers: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestrationResult:
    status: OrchestrationStatus
    asset_spec: Optional[Mapping[str, Any]] = None
    design_explanation: str = ""
    template_rationale: Sequence[str] = field(default_factory=tuple)
    questions: Sequence[ClarifyingQuestion] = field(default_factory=tuple)
    validation_issues: Sequence[ValidationIssue] = field(default_factory=tuple)
    provider_id: Optional[str] = None
    model: Optional[str] = None
    raw_model_content: str = ""

    @property
    def is_ready(self) -> bool:
        return self.status == "ready" and self.asset_spec is not None
