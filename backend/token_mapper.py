from __future__ import annotations

from dataclasses import dataclass

try:
    import tiktoken  # type: ignore
except ImportError:
    tiktoken = None


@dataclass
class TokenMetrics:
    raw_tokens: int
    compressed_tokens: int
    savings: int
    savings_ratio: float


class TokenMapper:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def _encode(self, text: str) -> list[int]:
        if not text:
            return []
        if tiktoken is None:
            return list(range(len(text.split())))
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except Exception:
            encoding = tiktoken.get_encoding("cl100k_base")
        return encoding.encode(text)

    def count_tokens(self, text: str) -> int:
        return len(self._encode(text))

    def compare(self, raw: str, compressed: str) -> TokenMetrics:
        raw_tokens = self.count_tokens(raw)
        compressed_tokens = self.count_tokens(compressed)
        savings = raw_tokens - compressed_tokens
        ratio = savings / raw_tokens if raw_tokens else 0.0
        return TokenMetrics(
            raw_tokens=raw_tokens,
            compressed_tokens=compressed_tokens,
            savings=savings,
            savings_ratio=ratio,
        )

