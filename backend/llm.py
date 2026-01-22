from __future__ import annotations

import hashlib
import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import httpx
from sqlalchemy.orm import Session

from .token_mapper import TokenMapper, TokenMetrics
from .models import Prompt
from .security import scrub_pii

try:
    from .ptil import PTILEncoder
except ImportError:
    try:
        from backend.ptil import PTILEncoder
    except ImportError:
        PTILEncoder = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.api_key:
            return "Error: OPENAI_API_KEY not configured."
            
        model = model or "gpt-4o-mini"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            return f"OpenAI API Error: {str(e)}"
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.api_key:
            return "Error: ANTHROPIC_API_KEY not configured."
            
        model = model or "claude-3-5-sonnet-20240620"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
        except httpx.HTTPError as e:
            return f"Anthropic API Error: {str(e)}"
        except Exception as e:
            return f"Error calling Anthropic: {str(e)}"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.api_key:
            return "Error: GEMINI_API_KEY not configured."

        model_name = model or "gemini-1.5-flash"
        
        # Fix for generic "gemini" model name
        if model_name.lower().strip() == "gemini":
            model_name = "gemini-1.5-flash"

        # Fallback if an invalid model name (like 'gpt-4') is passed by mistake
        if "gemini" not in model_name.lower():
            model_name = "gemini-1.5-flash"

        url = f"{self.base_url}/models/{model_name}:generateContent"
        params = {"key": self.api_key}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, params=params, json=payload)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates") or []
                if not candidates:
                    return "Gemini API Error: no candidates returned."
                content = candidates[0].get("content") or {}
                parts = content.get("parts") or []
                if not parts:
                    return "Gemini API Error: no content parts returned."
                text = parts[0].get("text")
                if not text:
                    return "Gemini API Error: empty content."
                return text
        except httpx.HTTPError as e:
            return f"Gemini API Error: {str(e)}"
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"


def get_provider(name: str, api_key: Optional[str] = None) -> LLMProvider:
    lowered = name.lower()
    if "openai" in lowered:
        return OpenAIProvider(api_key=api_key)
    if "anthropic" in lowered or "claude" in lowered:
        return AnthropicProvider(api_key=api_key)
    if "gemini" in lowered:
        return GeminiProvider(api_key=api_key)
    raise ValueError(f"Unsupported provider: {name}")


@dataclass
class ExecuteResult:
    provider: str
    model: Optional[str]
    raw_text: str
    compressed_text: str
    output: str
    tokens: TokenMetrics
    analysis: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    drift_detected: bool = False
    pii_found: bool = False
    confidence_score: float = 1.0


@dataclass
class OptimizationResult:
    raw_text: str
    compressed_text: str
    tokens: TokenMetrics
    analysis: Optional[List[Dict[str, Any]]]
    suggestions: List[str]
    pii_found: bool
    confidence_score: float = 1.0


def generate_suggestions(raw_text: str, metrics: TokenMetrics) -> List[str]:
    suggestions = []
    
    # Heuristic 1: Passive Voice
    # Simple regex for "be" verb + past participle (ed/en)
    # This is a naive approximation but serves the demo purpose
    passive_pattern = r'\b(am|is|are|was|were|be|been|being)\s+\w+(ed|en)\b'
    if re.search(passive_pattern, raw_text, re.IGNORECASE):
        suggestions.append("Replace passive voice with active ROOTs to save ~4 tokens per instance.")
        
    # Heuristic 2: Politeness Markers
    politeness = ["please", "could you", "would you", "kindly", "i would like"]
    if any(p in raw_text.lower() for p in politeness):
        suggestions.append("Remove politeness markers (e.g., 'Please', 'Could you'). PTIL handles intent directly.")
        
    # Heuristic 3: Low Savings Ratio
    if metrics.savings_ratio < 0.10 and metrics.raw_tokens > 20:
        suggestions.append("Low compression ratio. Try restructuring prompt with explicit ROLES and ROOT actions.")
        
    # Heuristic 4: Redundant "Act as"
    if "act as" in raw_text.lower() or "you are a" in raw_text.lower():
        suggestions.append("Replace 'Act as...' descriptions with direct ROLE definitions (e.g., ROLE:Expert).")
        
    return suggestions


def analyze_prompt(
    raw_text: str,
    model: str = "gpt-4o-mini",
    language: Optional[str] = None,
    format: str = "verbose",
) -> OptimizationResult:
    # 1. PII Scrubbing
    scrubbed_text, found_pii = scrub_pii(raw_text)
    
    # 2. Semantic Compression & Analysis
    analysis = None
    compressed = scrubbed_text
    confidence = 1.0
    
    if PTILEncoder is not None:
        encoder = PTILEncoder(language=language)
        compressed, confidence = encoder.encode_and_serialize(scrubbed_text, format=format)
        
        # Extract structured analysis
        try:
            cscs = encoder.encode(scrubbed_text)
            analysis = []
            for csc in cscs:
                analysis.append({
                    "root": csc.root.value if hasattr(csc.root, "value") else str(csc.root),
                    "ops": [op.value if hasattr(op, "value") else str(op) for op in csc.ops],
                    "roles": {
                        (k.value if hasattr(k, "value") else str(k)): (v.text if hasattr(v, "text") else str(v)) 
                        for k, v in csc.roles.items()
                    },
                    "meta": (csc.meta.value if hasattr(csc.meta, "value") else str(csc.meta)) if csc.meta else None
                })
        except Exception:
            pass

        if not compressed:
            compressed = scrubbed_text
            
    else:
        compressed = scrubbed_text

    # 3. Token Mapping
    token_mapper = TokenMapper(model=model)
    metrics = token_mapper.compare(scrubbed_text, compressed)
    
    # 4. Generate Suggestions
    suggestions = generate_suggestions(scrubbed_text, metrics)

    return OptimizationResult(
        raw_text=raw_text if not found_pii else scrubbed_text,
        compressed_text=compressed,
        tokens=metrics,
        analysis=analysis,
        suggestions=suggestions,
        pii_found=found_pii,
        confidence_score=confidence
    )


def execute(
    raw_text: str,
    provider_name: str,
    db: Session,
    model: Optional[str] = None,
    language: Optional[str] = None,
    format: str = "verbose",
    provider_key: Optional[str] = None,
) -> ExecuteResult:
    # 1. Analyze Prompt (Scrub, Compress, Stats, Suggestions)
    opt_result = analyze_prompt(
        raw_text=raw_text, 
        model=model or "gpt-4o-mini",
        language=language, 
        format=format
    )
    
    # 2. Drift Detection
    drift_detected = False
    
    # Calculate hashes
    raw_hash = hashlib.sha256(opt_result.raw_text.encode()).hexdigest()
    csc_hash = hashlib.sha256(opt_result.compressed_text.encode()).hexdigest()
    
    # Check against DB
    existing_prompt = db.query(Prompt).filter(Prompt.hash == raw_hash).first()
    if existing_prompt:
        if existing_prompt.last_csc_hash != csc_hash:
            drift_detected = True
            existing_prompt.drift_count += 1
            existing_prompt.last_csc_hash = csc_hash
            existing_prompt.last_csc_content = opt_result.compressed_text
    else:
        # Create new prompt tracking
        new_prompt = Prompt(
            hash=raw_hash,
            raw_text=opt_result.raw_text,
            last_csc_hash=csc_hash,
            last_csc_content=opt_result.compressed_text
        )
        db.add(new_prompt)

    # 3. LLM Execution
    provider = get_provider(provider_name, api_key=provider_key)
    output = provider.generate(opt_result.compressed_text, model=model)

    return ExecuteResult(
        provider=provider_name,
        model=model,
        raw_text=opt_result.raw_text,
        compressed_text=opt_result.compressed_text,
        output=output,
        tokens=opt_result.tokens,
        analysis=opt_result.analysis,
        suggestions=opt_result.suggestions,
        drift_detected=drift_detected,
        pii_found=opt_result.pii_found,
        confidence_score=opt_result.confidence_score
    )
