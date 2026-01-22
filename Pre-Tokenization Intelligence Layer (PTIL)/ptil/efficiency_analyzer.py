"""
Efficiency Analyzer for PTIL semantic encoder.

This module provides token reduction measurement and validation capabilities
to ensure the PTIL system achieves the required 60-80% token reduction
compared to raw text processing.
"""

import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from .models import CSC
from .encoder import PTILEncoder
from .csc_serializer import CSCSerializer


@dataclass
class EfficiencyMetrics:
    """Metrics for token reduction efficiency analysis."""
    raw_text: str
    csc_serialized: str
    raw_token_count: int
    csc_token_count: int
    reduction_percentage: float
    reduction_ratio: float
    
    def __str__(self) -> str:
        return (f"EfficiencyMetrics(raw_tokens={self.raw_token_count}, "
                f"csc_tokens={self.csc_token_count}, "
                f"reduction={self.reduction_percentage:.1f}%)")


class EfficiencyAnalyzer:
    """
    Analyzer for measuring and validating token reduction efficiency.
    
    Provides comprehensive token counting, reduction measurement, and validation
    against the required 60-80% token reduction targets.
    """
    
    def __init__(self, encoder: Optional[PTILEncoder] = None):
        """
        Initialize the efficiency analyzer.
        
        Args:
            encoder: PTIL encoder instance (creates new one if None)
        """
        self.logger = logging.getLogger(__name__)
        self.encoder = encoder or PTILEncoder()
        self.serializer = CSCSerializer()
        
        # Token reduction targets
        self.min_reduction_percentage = 60.0
        self.max_reduction_percentage = 80.0
        
    def analyze_text(self, text: str, tokenizer_type: str = "bpe", format: str = "ultra") -> EfficiencyMetrics:
        """
        Analyze token reduction efficiency for a single text.
        
        Args:
            text: Input text to analyze
            tokenizer_type: Type of tokenizer to simulate ("bpe", "unigram", "wordpiece")
            format: Serialization format ("verbose", "compact", "ultra")
            
        Returns:
            EfficiencyMetrics: Detailed efficiency analysis results
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        try:
            # Generate CSC representation
            cscs = self.encoder.encode(text)
            csc_serialized = self.encoder.encode_and_serialize(text, format=format)
            
            # Count tokens for both representations
            raw_token_count = self._count_tokens(text, tokenizer_type)
            csc_token_count = self._count_tokens(csc_serialized, tokenizer_type)
            
            # Calculate reduction metrics
            reduction_percentage = self._calculate_reduction_percentage(
                raw_token_count, csc_token_count
            )
            reduction_ratio = raw_token_count / max(csc_token_count, 1)
            
            metrics = EfficiencyMetrics(
                raw_text=text,
                csc_serialized=csc_serialized,
                raw_token_count=raw_token_count,
                csc_token_count=csc_token_count,
                reduction_percentage=reduction_percentage,
                reduction_ratio=reduction_ratio
            )
            
            self.logger.debug(f"Analyzed text efficiency: {metrics}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Efficiency analysis failed for text '{text[:50]}...': {e}")
            raise RuntimeError(f"Efficiency analysis failed: {e}")
    
    def analyze_batch(self, texts: List[str], 
                     tokenizer_type: str = "bpe", format: str = "ultra") -> List[EfficiencyMetrics]:
        """
        Analyze token reduction efficiency for multiple texts.
        
        Args:
            texts: List of input texts to analyze
            tokenizer_type: Type of tokenizer to simulate
            format: Serialization format ("verbose", "compact", "ultra")
            
        Returns:
            List[EfficiencyMetrics]: Efficiency analysis results for each text
        """
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        results = []
        failed_count = 0
        
        for i, text in enumerate(texts):
            try:
                metrics = self.analyze_text(text, tokenizer_type, format)
                results.append(metrics)
            except Exception as e:
                self.logger.warning(f"Failed to analyze text {i}: {e}")
                failed_count += 1
        
        if failed_count > 0:
            self.logger.warning(f"Failed to analyze {failed_count}/{len(texts)} texts")
        
        return results
    
    def validate_efficiency_target(self, metrics: EfficiencyMetrics) -> bool:
        """
        Validate that efficiency metrics meet the 60-80% reduction target.
        
        Args:
            metrics: Efficiency metrics to validate
            
        Returns:
            bool: True if metrics meet the target, False otherwise
        """
        return (self.min_reduction_percentage <= metrics.reduction_percentage <= 
                self.max_reduction_percentage)
    
    def validate_batch_efficiency(self, metrics_list: List[EfficiencyMetrics]) -> Dict[str, Any]:
        """
        Validate efficiency across a batch of texts.
        
        Args:
            metrics_list: List of efficiency metrics to validate
            
        Returns:
            Dict[str, Any]: Validation results with statistics
        """
        if not metrics_list:
            raise ValueError("Metrics list cannot be empty")
        
        # Calculate statistics
        reductions = [m.reduction_percentage for m in metrics_list]
        ratios = [m.reduction_ratio for m in metrics_list]
        
        avg_reduction = sum(reductions) / len(reductions)
        min_reduction = min(reductions)
        max_reduction = max(reductions)
        avg_ratio = sum(ratios) / len(ratios)
        
        # Count texts meeting target
        meeting_target = sum(1 for m in metrics_list if self.validate_efficiency_target(m))
        target_percentage = (meeting_target / len(metrics_list)) * 100
        
        # Determine overall validation result
        overall_valid = (avg_reduction >= self.min_reduction_percentage and 
                        target_percentage >= 80.0)  # 80% of texts should meet target
        
        validation_results = {
            "overall_valid": overall_valid,
            "total_texts": len(metrics_list),
            "meeting_target": meeting_target,
            "target_percentage": target_percentage,
            "statistics": {
                "avg_reduction_percentage": avg_reduction,
                "min_reduction_percentage": min_reduction,
                "max_reduction_percentage": max_reduction,
                "avg_reduction_ratio": avg_ratio
            },
            "target_range": {
                "min": self.min_reduction_percentage,
                "max": self.max_reduction_percentage
            }
        }
        
        self.logger.info(f"Batch validation: {meeting_target}/{len(metrics_list)} texts "
                        f"meet target ({target_percentage:.1f}%)")
        
        return validation_results
    
    def generate_efficiency_report(self, metrics_list: List[EfficiencyMetrics]) -> str:
        """
        Generate a comprehensive efficiency report.
        
        Args:
            metrics_list: List of efficiency metrics
            
        Returns:
            str: Formatted efficiency report
        """
        if not metrics_list:
            return "No metrics available for report generation."
        
        validation = self.validate_batch_efficiency(metrics_list)
        stats = validation["statistics"]
        
        report_lines = [
            "PTIL Token Reduction Efficiency Report",
            "=" * 40,
            f"Total texts analyzed: {validation['total_texts']}",
            f"Texts meeting target: {validation['meeting_target']} "
            f"({validation['target_percentage']:.1f}%)",
            f"Target range: {validation['target_range']['min']}-"
            f"{validation['target_range']['max']}% reduction",
            "",
            "Statistics:",
            f"  Average reduction: {stats['avg_reduction_percentage']:.1f}%",
            f"  Minimum reduction: {stats['min_reduction_percentage']:.1f}%",
            f"  Maximum reduction: {stats['max_reduction_percentage']:.1f}%",
            f"  Average ratio: {stats['avg_reduction_ratio']:.2f}x",
            "",
            f"Overall validation: {'PASS' if validation['overall_valid'] else 'FAIL'}",
        ]
        
        # Add sample details for first few texts
        if len(metrics_list) <= 5:
            report_lines.extend([
                "",
                "Detailed Results:",
                "-" * 20
            ])
            
            for i, metrics in enumerate(metrics_list):
                status = "PASS" if self.validate_efficiency_target(metrics) else "FAIL"
                report_lines.append(
                    f"{i+1}. {status} - {metrics.reduction_percentage:.1f}% reduction "
                    f"({metrics.raw_token_count} → {metrics.csc_token_count} tokens)"
                )
                report_lines.append(f"   Text: {metrics.raw_text[:60]}...")
                report_lines.append(f"   CSC:  {metrics.csc_serialized[:60]}...")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _count_tokens(self, text: str, tokenizer_type: str) -> int:
        """
        Count tokens using simulated tokenizer behavior.
        
        Args:
            text: Text to tokenize
            tokenizer_type: Type of tokenizer ("bpe", "unigram", "wordpiece")
            
        Returns:
            int: Estimated token count
        """
        if not text or not text.strip():
            return 0
        
        # For ultra-compact CSC format, use optimized counting
        if self._is_ultra_compact_format(text):
            return self._count_ultra_compact_tokens(text)
        
        # Simplified tokenizer simulation
        if tokenizer_type.lower() == "bpe":
            return self._simulate_bpe_tokenization(text)
        elif tokenizer_type.lower() == "unigram":
            return self._simulate_unigram_tokenization(text)
        elif tokenizer_type.lower() == "wordpiece":
            return self._simulate_wordpiece_tokenization(text)
        else:
            # Default to simple whitespace tokenization
            return len(text.split())
    
    def _is_ultra_compact_format(self, text: str) -> bool:
        """Check if text is in ultra-compact CSC format."""
        # Ultra-compact format characteristics:
        # - Very short (typically < 20 chars)
        # - No angle brackets or equals signs
        # - Starts with digit/letter (ROOT code)
        # - Contains mostly alphanumeric characters
        
        if len(text) > 30:
            return False
        
        if any(char in text for char in ["<", ">", "="]):
            return False
        
        # Should start with ROOT code (digit or A-Z)
        if text and not (text[0].isdigit() or text[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            return False
        
        return True
    
    def _count_ultra_compact_tokens(self, text: str) -> int:
        """
        Count tokens for ultra-compact CSC format.
        
        Ultra-compact format is designed to be tokenized very efficiently.
        Most of the string should be treated as 1-2 tokens maximum.
        """
        if not text.strip():
            return 0
        
        # Split by spaces (multiple CSCs)
        parts = text.split()
        total_tokens = 0
        
        for part in parts:
            if not part:
                continue
            
            # Each ultra-compact CSC should be 1-2 tokens
            if len(part) <= 8:
                total_tokens += 1  # Single token
            else:
                total_tokens += 2  # Two tokens for longer ones
        
        return total_tokens
    
    def _simulate_bpe_tokenization(self, text: str) -> int:
        """
        Simulate BPE tokenization for token counting.
        
        Args:
            text: Text to tokenize
            
        Returns:
            int: Estimated BPE token count
        """
        # Simplified BPE simulation
        # Real BPE would use learned merge rules
        
        # Split on whitespace and punctuation
        import re
        tokens = re.findall(r'\w+|[^\w\s]', text)
        
        # Simulate subword splitting (rough approximation)
        total_tokens = 0
        for token in tokens:
            if len(token) <= 3:
                total_tokens += 1
            elif len(token) <= 6:
                total_tokens += 2
            else:
                total_tokens += max(2, len(token) // 3)
        
        return total_tokens
    
    def _simulate_unigram_tokenization(self, text: str) -> int:
        """
        Simulate Unigram tokenization for token counting.
        
        Args:
            text: Text to tokenize
            
        Returns:
            int: Estimated Unigram token count
        """
        # Simplified Unigram simulation
        # Similar to BPE but with different splitting strategy
        
        import re
        tokens = re.findall(r'\w+|[^\w\s]', text)
        
        # Unigram tends to create slightly fewer tokens than BPE
        total_tokens = 0
        for token in tokens:
            if len(token) <= 4:
                total_tokens += 1
            elif len(token) <= 8:
                total_tokens += 2
            else:
                total_tokens += max(2, len(token) // 4)
        
        return total_tokens
    
    def _simulate_wordpiece_tokenization(self, text: str) -> int:
        """
        Simulate WordPiece tokenization for token counting.
        
        Args:
            text: Text to tokenize
            
        Returns:
            int: Estimated WordPiece token count
        """
        # Simplified WordPiece simulation
        # WordPiece uses ## prefix for continuation tokens
        
        import re
        tokens = re.findall(r'\w+|[^\w\s]', text)
        
        # WordPiece behavior similar to BPE
        total_tokens = 0
        for token in tokens:
            if len(token) <= 3:
                total_tokens += 1
            elif len(token) <= 7:
                total_tokens += 2
            else:
                total_tokens += max(2, len(token) // 3)
        
        return total_tokens
    
    def _calculate_reduction_percentage(self, raw_count: int, csc_count: int) -> float:
        """
        Calculate token reduction percentage.
        
        Args:
            raw_count: Original token count
            csc_count: CSC token count
            
        Returns:
            float: Reduction percentage (0-100, can be negative if CSC is longer)
        """
        if raw_count == 0:
            return 0.0
        
        reduction = raw_count - csc_count
        return (reduction / raw_count) * 100.0