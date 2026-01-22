"""
Tokenizer Compatibility Validator for PTIL semantic encoder.

This module provides validation capabilities to ensure CSC serialized output
is compatible with standard tokenizers (BPE, Unigram, WordPiece) and processes
without errors in existing LLM architectures.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from .models import CSC
from .csc_serializer import CSCSerializer


class TokenizerType(Enum):
    """Supported tokenizer types for compatibility testing."""
    BPE = "bpe"
    UNIGRAM = "unigram"
    WORDPIECE = "wordpiece"


@dataclass
class CompatibilityResult:
    """Results of tokenizer compatibility validation."""
    tokenizer_type: TokenizerType
    input_text: str
    is_compatible: bool
    token_count: int
    issues: List[str]
    processed_tokens: List[str]
    
    def __str__(self) -> str:
        status = "COMPATIBLE" if self.is_compatible else "INCOMPATIBLE"
        return (f"CompatibilityResult({self.tokenizer_type.value}: {status}, "
                f"tokens={self.token_count}, issues={len(self.issues)})")


class TokenizerCompatibilityValidator:
    """
    Validator for ensuring CSC output compatibility with standard tokenizers.
    
    Tests serialized CSC format against BPE, Unigram, and WordPiece tokenizer
    requirements to ensure seamless integration with existing LLM architectures.
    """
    
    def __init__(self):
        """Initialize the tokenizer compatibility validator."""
        self.logger = logging.getLogger(__name__)
        self.serializer = CSCSerializer()
        
        # Define problematic patterns for different tokenizers
        self._init_tokenizer_patterns()
    
    def _init_tokenizer_patterns(self):
        """Initialize tokenizer-specific problematic patterns."""
        
        # Common problematic patterns across tokenizers
        self.common_issues = {
            "control_chars": re.compile(r'[\x00-\x1f\x7f-\x9f]'),
            "excessive_whitespace": re.compile(r'\s{3,}'),
            "malformed_brackets": re.compile(r'[<>]{3,}|<[^>]*$|^[^<]*>'),
            "empty_tags": re.compile(r'<\s*>|<\s*=\s*>'),
        }
        
        # BPE-specific patterns
        self.bpe_issues = {
            "unicode_normalization": re.compile(r'[^\x00-\x7F]'),  # Non-ASCII chars
            "byte_pair_conflicts": re.compile(r'@@|##|\u0120'),  # Common BPE markers
        }
        
        # Unigram-specific patterns
        self.unigram_issues = {
            "sentence_piece_markers": re.compile(r'▁'),  # SentencePiece marker
            "probability_conflicts": re.compile(r'[^\w\s<>=|.-]'),  # Special chars
        }
        
        # WordPiece-specific patterns
        self.wordpiece_issues = {
            "continuation_markers": re.compile(r'##'),  # WordPiece continuation
            "vocab_oov": re.compile(r'[^\w\s<>=|.-]'),  # Out-of-vocabulary chars
        }
    
    def validate_csc_compatibility(self, csc: CSC, 
                                  tokenizer_types: Optional[List[TokenizerType]] = None) -> Dict[TokenizerType, CompatibilityResult]:
        """
        Validate CSC compatibility with specified tokenizers.
        
        Args:
            csc: CSC structure to validate
            tokenizer_types: List of tokenizer types to test (default: all)
            
        Returns:
            Dict[TokenizerType, CompatibilityResult]: Compatibility results per tokenizer
        """
        if tokenizer_types is None:
            tokenizer_types = list(TokenizerType)
        
        # Serialize CSC to text format
        serialized_text = self.serializer.serialize(csc)
        
        results = {}
        for tokenizer_type in tokenizer_types:
            try:
                result = self._validate_single_tokenizer(serialized_text, tokenizer_type)
                results[tokenizer_type] = result
            except Exception as e:
                self.logger.error(f"Validation failed for {tokenizer_type.value}: {e}")
                results[tokenizer_type] = CompatibilityResult(
                    tokenizer_type=tokenizer_type,
                    input_text=serialized_text,
                    is_compatible=False,
                    token_count=0,
                    issues=[f"Validation error: {e}"],
                    processed_tokens=[]
                )
        
        return results
    
    def validate_text_compatibility(self, text: str,
                                   tokenizer_types: Optional[List[TokenizerType]] = None) -> Dict[TokenizerType, CompatibilityResult]:
        """
        Validate serialized text compatibility with specified tokenizers.
        
        Args:
            text: Serialized CSC text to validate
            tokenizer_types: List of tokenizer types to test (default: all)
            
        Returns:
            Dict[TokenizerType, CompatibilityResult]: Compatibility results per tokenizer
        """
        if tokenizer_types is None:
            tokenizer_types = list(TokenizerType)
        
        results = {}
        for tokenizer_type in tokenizer_types:
            try:
                result = self._validate_single_tokenizer(text, tokenizer_type)
                results[tokenizer_type] = result
            except Exception as e:
                self.logger.error(f"Validation failed for {tokenizer_type.value}: {e}")
                results[tokenizer_type] = CompatibilityResult(
                    tokenizer_type=tokenizer_type,
                    input_text=text,
                    is_compatible=False,
                    token_count=0,
                    issues=[f"Validation error: {e}"],
                    processed_tokens=[]
                )
        
        return results
    
    def validate_batch_compatibility(self, texts: List[str],
                                    tokenizer_types: Optional[List[TokenizerType]] = None) -> Dict[str, Any]:
        """
        Validate compatibility for multiple serialized texts.
        
        Args:
            texts: List of serialized CSC texts to validate
            tokenizer_types: List of tokenizer types to test (default: all)
            
        Returns:
            Dict[str, Any]: Batch validation results with statistics
        """
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        if tokenizer_types is None:
            tokenizer_types = list(TokenizerType)
        
        all_results = []
        tokenizer_stats = {tokenizer_type: {"compatible": 0, "total": 0} 
                          for tokenizer_type in tokenizer_types}
        
        for text in texts:
            text_results = self.validate_text_compatibility(text, tokenizer_types)
            all_results.append(text_results)
            
            for tokenizer_type, result in text_results.items():
                tokenizer_stats[tokenizer_type]["total"] += 1
                if result.is_compatible:
                    tokenizer_stats[tokenizer_type]["compatible"] += 1
        
        # Calculate compatibility percentages
        compatibility_percentages = {}
        for tokenizer_type, stats in tokenizer_stats.items():
            if stats["total"] > 0:
                percentage = (stats["compatible"] / stats["total"]) * 100
                compatibility_percentages[tokenizer_type.value] = percentage
            else:
                compatibility_percentages[tokenizer_type.value] = 0.0
        
        # Determine overall compatibility (require 95% compatibility for each tokenizer)
        overall_compatible = all(
            percentage >= 95.0 for percentage in compatibility_percentages.values()
        )
        
        return {
            "overall_compatible": overall_compatible,
            "total_texts": len(texts),
            "tokenizer_stats": {
                tokenizer_type.value: stats for tokenizer_type, stats in tokenizer_stats.items()
            },
            "compatibility_percentages": compatibility_percentages,
            "detailed_results": all_results
        }
    
    def _validate_single_tokenizer(self, text: str, tokenizer_type: TokenizerType) -> CompatibilityResult:
        """
        Validate text against a single tokenizer type.
        
        Args:
            text: Text to validate
            tokenizer_type: Tokenizer type to validate against
            
        Returns:
            CompatibilityResult: Validation result
        """
        issues = []
        
        # Check common issues
        issues.extend(self._check_common_issues(text))
        
        # Check tokenizer-specific issues
        if tokenizer_type == TokenizerType.BPE:
            issues.extend(self._check_bpe_issues(text))
        elif tokenizer_type == TokenizerType.UNIGRAM:
            issues.extend(self._check_unigram_issues(text))
        elif tokenizer_type == TokenizerType.WORDPIECE:
            issues.extend(self._check_wordpiece_issues(text))
        
        # Simulate tokenization
        try:
            tokens = self._simulate_tokenization(text, tokenizer_type)
            token_count = len(tokens)
        except Exception as e:
            issues.append(f"Tokenization simulation failed: {e}")
            tokens = []
            token_count = 0
        
        # Check for tokenization-specific issues
        if tokens:
            issues.extend(self._check_tokenization_issues(tokens, tokenizer_type))
        
        is_compatible = len(issues) == 0
        
        return CompatibilityResult(
            tokenizer_type=tokenizer_type,
            input_text=text,
            is_compatible=is_compatible,
            token_count=token_count,
            issues=issues,
            processed_tokens=tokens
        )
    
    def _check_common_issues(self, text: str) -> List[str]:
        """Check for common tokenizer compatibility issues."""
        issues = []
        
        # Control characters
        if self.common_issues["control_chars"].search(text):
            issues.append("Contains control characters")
        
        # Excessive whitespace
        if self.common_issues["excessive_whitespace"].search(text):
            issues.append("Contains excessive whitespace")
        
        # Malformed brackets (CSC format validation)
        if self.common_issues["malformed_brackets"].search(text):
            issues.append("Contains malformed angle brackets")
        
        # Empty tags
        if self.common_issues["empty_tags"].search(text):
            issues.append("Contains empty tags")
        
        # Check for balanced angle brackets
        open_count = text.count('<')
        close_count = text.count('>')
        if open_count != close_count:
            issues.append(f"Unbalanced angle brackets: {open_count} < vs {close_count} >")
        
        return issues
    
    def _check_bpe_issues(self, text: str) -> List[str]:
        """Check for BPE-specific compatibility issues."""
        issues = []
        
        # Check for BPE marker conflicts
        if self.bpe_issues["byte_pair_conflicts"].search(text):
            issues.append("Contains BPE marker conflicts (@@, ##, or Ġ)")
        
        return issues
    
    def _check_unigram_issues(self, text: str) -> List[str]:
        """Check for Unigram-specific compatibility issues."""
        issues = []
        
        # Check for SentencePiece markers
        if self.unigram_issues["sentence_piece_markers"].search(text):
            issues.append("Contains SentencePiece markers (▁)")
        
        return issues
    
    def _check_wordpiece_issues(self, text: str) -> List[str]:
        """Check for WordPiece-specific compatibility issues."""
        issues = []
        
        # Check for WordPiece continuation markers
        if self.wordpiece_issues["continuation_markers"].search(text):
            issues.append("Contains WordPiece continuation markers (##)")
        
        return issues
    
    def _check_tokenization_issues(self, tokens: List[str], tokenizer_type: TokenizerType) -> List[str]:
        """Check for issues in tokenized output."""
        issues = []
        
        # Check for empty tokens
        if any(not token.strip() for token in tokens):
            issues.append("Tokenization produced empty tokens")
        
        # Check for excessively long tokens (>100 chars)
        long_tokens = [token for token in tokens if len(token) > 100]
        if long_tokens:
            issues.append(f"Tokenization produced {len(long_tokens)} excessively long tokens")
        
        # Check for tokens that might cause issues
        problematic_tokens = [token for token in tokens if self._is_problematic_token(token)]
        if problematic_tokens:
            issues.append(f"Tokenization produced {len(problematic_tokens)} problematic tokens")
        
        return issues
    
    def _is_problematic_token(self, token: str) -> bool:
        """Check if a token might cause processing issues."""
        # Check for tokens with only special characters (but allow short ones)
        if re.match(r'^[^\w\s]+$', token) and len(token) > 10:
            return True
        
        # Check for tokens with control characters
        if re.search(r'[\x00-\x1f\x7f-\x9f]', token):
            return True
        
        # Check for excessively long tokens with mixed content
        if len(token) > 50 and re.search(r'[^\x00-\x7F]', token) and re.search(r'[<>=|]', token):
            return True
        
        return False
    
    def _simulate_tokenization(self, text: str, tokenizer_type: TokenizerType) -> List[str]:
        """
        Simulate tokenization for compatibility testing.
        
        Args:
            text: Text to tokenize
            tokenizer_type: Type of tokenizer to simulate
            
        Returns:
            List[str]: Simulated tokens
        """
        if not text.strip():
            return []
        
        if tokenizer_type == TokenizerType.BPE:
            return self._simulate_bpe_tokenization(text)
        elif tokenizer_type == TokenizerType.UNIGRAM:
            return self._simulate_unigram_tokenization(text)
        elif tokenizer_type == TokenizerType.WORDPIECE:
            return self._simulate_wordpiece_tokenization(text)
        else:
            # Fallback to simple whitespace tokenization
            return text.split()
    
    def _simulate_bpe_tokenization(self, text: str) -> List[str]:
        """Simulate BPE tokenization."""
        # Split on whitespace and punctuation, then apply subword splitting
        import re
        
        # First split on whitespace
        words = text.split()
        tokens = []
        
        for word in words:
            # Split word into character-level tokens and apply BPE-like merging
            if re.match(r'^<[^>]*>$', word):
                # Keep CSC tags as single tokens
                tokens.append(word)
            else:
                # Apply subword splitting
                if len(word) <= 4:
                    tokens.append(word)
                else:
                    # Simulate BPE subword splitting
                    for i in range(0, len(word), 3):
                        subword = word[i:i+3]
                        if subword:
                            tokens.append(subword)
        
        return tokens
    
    def _simulate_unigram_tokenization(self, text: str) -> List[str]:
        """Simulate Unigram tokenization."""
        # Similar to BPE but with different splitting strategy
        import re
        
        words = text.split()
        tokens = []
        
        for word in words:
            if re.match(r'^<[^>]*>$', word):
                # Keep CSC tags as single tokens
                tokens.append(word)
            else:
                # Unigram tends to create longer subwords
                if len(word) <= 5:
                    tokens.append(word)
                else:
                    # Simulate Unigram subword splitting
                    for i in range(0, len(word), 4):
                        subword = word[i:i+4]
                        if subword:
                            tokens.append(subword)
        
        return tokens
    
    def _simulate_wordpiece_tokenization(self, text: str) -> List[str]:
        """Simulate WordPiece tokenization."""
        # WordPiece uses ## prefix for continuation tokens
        import re
        
        words = text.split()
        tokens = []
        
        for word in words:
            if re.match(r'^<[^>]*>$', word):
                # Keep CSC tags as single tokens
                tokens.append(word)
            else:
                # WordPiece subword splitting
                if len(word) <= 4:
                    tokens.append(word)
                else:
                    # First subword without ##, rest with ##
                    tokens.append(word[:3])
                    for i in range(3, len(word), 3):
                        subword = word[i:i+3]
                        if subword:
                            tokens.append(f"##{subword}")
        
        return tokens
    
    def generate_compatibility_report(self, batch_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive tokenizer compatibility report.
        
        Args:
            batch_results: Results from validate_batch_compatibility
            
        Returns:
            str: Formatted compatibility report
        """
        report_lines = [
            "PTIL Tokenizer Compatibility Report",
            "=" * 40,
            f"Total texts analyzed: {batch_results['total_texts']}",
            f"Overall compatibility: {'PASS' if batch_results['overall_compatible'] else 'FAIL'}",
            ""
        ]
        
        # Add per-tokenizer statistics
        report_lines.append("Tokenizer Compatibility:")
        for tokenizer_name, percentage in batch_results['compatibility_percentages'].items():
            stats = batch_results['tokenizer_stats'][tokenizer_name]
            status = "PASS" if percentage >= 95.0 else "FAIL"
            report_lines.append(
                f"  {tokenizer_name.upper()}: {status} - {percentage:.1f}% "
                f"({stats['compatible']}/{stats['total']})"
            )
        
        # Add common issues if any
        if not batch_results['overall_compatible']:
            report_lines.extend([
                "",
                "Common Issues Found:",
                "-" * 20
            ])
            
            issue_counts = {}
            for text_results in batch_results['detailed_results']:
                for result in text_results.values():
                    for issue in result.issues:
                        issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"  {issue}: {count} occurrences")
        
        return "\n".join(report_lines)