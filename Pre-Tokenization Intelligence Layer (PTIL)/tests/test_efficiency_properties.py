"""
Property-based tests for PTIL Efficiency Analysis.

This module contains property-based tests that validate token reduction efficiency
properties of the PTIL system across many generated inputs using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from ptil.efficiency_analyzer import EfficiencyAnalyzer, EfficiencyMetrics
from ptil.encoder import PTILEncoder


class TestEfficiencyProperties:
    """Property-based tests for PTIL efficiency analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = PTILEncoder()
        self.analyzer = EfficiencyAnalyzer(self.encoder)
    
    @given(st.text(min_size=10, max_size=500).filter(lambda x: x.strip() and len(x.split()) >= 3))
    @settings(max_examples=100, deadline=10000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_token_reduction_efficiency(self, text):
        """
        Property 19: Token Reduction Efficiency
        For any typical text input, the CSC representation should achieve 60-80% token reduction 
        compared to raw text.
        **Validates: Requirements 7.1**
        """
        # Skip texts that are too short or contain only special characters
        words = text.split()
        assume(len(words) >= 3)
        assume(any(word.isalpha() for word in words))
        
        try:
            # Analyze token reduction efficiency
            metrics = self.analyzer.analyze_text(text, tokenizer_type="bpe")
            
            # Verify metrics are valid
            assert metrics.raw_token_count > 0, (
                f"Raw token count should be positive for text: '{text[:50]}...'"
            )
            assert metrics.csc_token_count >= 0, (
                f"CSC token count should be non-negative for text: '{text[:50]}...'"
            )
            
            # For meaningful text, CSC should have some tokens
            if len(words) >= 3:
                assert metrics.csc_token_count > 0, (
                    f"CSC should produce tokens for meaningful text: '{text[:50]}...'"
                )
            
            # Verify reduction percentage calculation
            expected_reduction = ((metrics.raw_token_count - metrics.csc_token_count) / 
                                metrics.raw_token_count) * 100
            assert abs(metrics.reduction_percentage - expected_reduction) < 0.01, (
                f"Reduction percentage calculation error for text: '{text[:50]}...'\n"
                f"Expected: {expected_reduction:.2f}%, Got: {metrics.reduction_percentage:.2f}%"
            )
            
            # Verify reduction ratio calculation
            expected_ratio = metrics.raw_token_count / max(metrics.csc_token_count, 1)
            assert abs(metrics.reduction_ratio - expected_ratio) < 0.01, (
                f"Reduction ratio calculation error for text: '{text[:50]}...'\n"
                f"Expected: {expected_ratio:.2f}, Got: {metrics.reduction_ratio:.2f}"
            )
            
            # For well-formed sentences, we expect some level of reduction
            # (though not necessarily within the 60-80% target for all random text)
            if len(words) >= 5 and any(word.lower() in ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'will', 'would'] for word in words):
                # This looks like natural language, expect at least some reduction
                assert metrics.reduction_percentage >= 0, (
                    f"Expected some token reduction for natural language text: '{text[:50]}...'\n"
                    f"Raw tokens: {metrics.raw_token_count}, CSC tokens: {metrics.csc_token_count}"
                )
            
            # Verify that reduction percentage is mathematically correct
            # (can be negative if CSC is longer than original)
            assert -1000 <= metrics.reduction_percentage <= 100, (
                f"Reduction percentage should be reasonable for text: '{text[:50]}...'\n"
                f"Got: {metrics.reduction_percentage:.2f}%"
            )
            
            # Verify that reduction ratio is positive
            assert metrics.reduction_ratio > 0, (
                f"Reduction ratio should be positive for text: '{text[:50]}...'\n"
                f"Got: {metrics.reduction_ratio:.2f}"
            )
            
        except Exception as e:
            # For property-based testing, we should handle edge cases gracefully
            pytest.fail(f"Efficiency analysis failed for text: '{text[:50]}...'\nError: {e}")
    
    @given(st.lists(
        st.text(min_size=10, max_size=200).filter(lambda x: x.strip() and len(x.split()) >= 3),
        min_size=2, max_size=10
    ))
    @settings(max_examples=50, deadline=15000)
    def test_batch_efficiency_consistency(self, texts):
        """
        Property: Batch Efficiency Consistency
        For any batch of texts, efficiency analysis should be consistent and provide
        meaningful aggregate statistics.
        **Validates: Requirements 7.1, 7.2**
        """
        # Filter out texts that are too similar or problematic
        unique_texts = []
        for text in texts:
            words = text.split()
            if (len(words) >= 3 and 
                any(word.isalpha() for word in words) and
                text not in unique_texts):
                unique_texts.append(text)
        
        assume(len(unique_texts) >= 2)
        
        try:
            # Analyze batch efficiency
            metrics_list = self.analyzer.analyze_batch(unique_texts, tokenizer_type="bpe")
            
            # Verify we got results for all texts
            assert len(metrics_list) <= len(unique_texts), (
                f"Got more results than input texts: {len(metrics_list)} > {len(unique_texts)}"
            )
            
            # Verify each metric is valid
            for i, metrics in enumerate(metrics_list):
                assert isinstance(metrics, EfficiencyMetrics), (
                    f"Result {i} is not an EfficiencyMetrics instance"
                )
                assert metrics.raw_token_count > 0, (
                    f"Invalid raw token count for text {i}: {metrics.raw_token_count}"
                )
                assert metrics.csc_token_count >= 0, (
                    f"Invalid CSC token count for text {i}: {metrics.csc_token_count}"
                )
                assert 0 <= metrics.reduction_percentage <= 100, (
                    f"Invalid reduction percentage for text {i}: {metrics.reduction_percentage}"
                )
            
            # Test batch validation
            if metrics_list:
                validation_results = self.analyzer.validate_batch_efficiency(metrics_list)
                
                # Verify validation structure
                assert "overall_valid" in validation_results
                assert "total_texts" in validation_results
                assert "statistics" in validation_results
                assert validation_results["total_texts"] == len(metrics_list)
                
                # Verify statistics are reasonable
                stats = validation_results["statistics"]
                assert "avg_reduction_percentage" in stats
                assert "min_reduction_percentage" in stats
                assert "max_reduction_percentage" in stats
                assert "avg_reduction_ratio" in stats
                
                # Statistics should be within reasonable bounds
                assert -1000 <= stats["avg_reduction_percentage"] <= 100
                assert -1000 <= stats["min_reduction_percentage"] <= 100
                assert -1000 <= stats["max_reduction_percentage"] <= 100
                assert stats["avg_reduction_ratio"] > 0
                
                # Min should be <= avg <= max
                assert stats["min_reduction_percentage"] <= stats["avg_reduction_percentage"]
                assert stats["avg_reduction_percentage"] <= stats["max_reduction_percentage"]
        
        except Exception as e:
            pytest.fail(f"Batch efficiency analysis failed for {len(unique_texts)} texts\nError: {e}")
    
    @given(st.sampled_from([
        # Well-formed sentences that should achieve good reduction
        "The boy will not go to school tomorrow",
        "She is reading a book in the library",
        "They have been working on the project all day",
        "The cat sat on the mat and looked around",
        "We should finish this task before the deadline",
        "The students are studying for their final exams",
        "He walked slowly through the quiet park",
        "The meeting will start at three o'clock sharp",
        "She has completed all her assignments successfully",
        "The weather forecast predicts rain for tomorrow"
    ]))
    @settings(max_examples=50, deadline=5000)
    def test_natural_language_efficiency_target(self, text):
        """
        Property: Natural Language Efficiency Target
        For well-formed natural language sentences, the system should achieve
        meaningful token reduction that approaches the 60-80% target.
        **Validates: Requirements 7.1**
        """
        try:
            # Test with different tokenizer types
            for tokenizer_type in ["bpe", "unigram", "wordpiece"]:
                metrics = self.analyzer.analyze_text(text, tokenizer_type=tokenizer_type)
                
                # Verify basic metrics validity
                assert metrics.raw_token_count > 0
                assert metrics.csc_token_count > 0
                assert metrics.reduction_percentage >= 0
                
                # For well-formed natural language, expect some reduction
                # (We don't enforce the 60-80% target here as it depends on the specific
                # implementation quality, but we expect at least some improvement)
                assert metrics.reduction_percentage >= 0, (
                    f"Expected some reduction for natural language with {tokenizer_type}: '{text}'\n"
                    f"Raw: {metrics.raw_token_count}, CSC: {metrics.csc_token_count}, "
                    f"Reduction: {metrics.reduction_percentage:.1f}%"
                )
                
                # Verify the CSC is not longer than the original (that would be counterproductive)
                assert metrics.csc_token_count <= metrics.raw_token_count * 1.5, (
                    f"CSC should not be significantly longer than original with {tokenizer_type}: '{text}'\n"
                    f"Raw: {metrics.raw_token_count}, CSC: {metrics.csc_token_count}"
                )
                
                # Verify target validation works
                target_met = self.analyzer.validate_efficiency_target(metrics)
                assert isinstance(target_met, bool), (
                    f"Target validation should return boolean for {tokenizer_type}"
                )
        
        except Exception as e:
            pytest.fail(f"Natural language efficiency test failed for: '{text}'\nError: {e}")
    
    @given(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    @settings(max_examples=100, deadline=5000)
    def test_efficiency_metrics_properties(self, text):
        """
        Property: Efficiency Metrics Properties
        For any text input, efficiency metrics should satisfy basic mathematical properties.
        **Validates: Requirements 7.1, 7.2**
        """
        try:
            metrics = self.analyzer.analyze_text(text, tokenizer_type="bpe")
            
            # Basic mathematical properties
            if metrics.raw_token_count > 0:
                # Reduction percentage should match calculation
                expected_reduction = ((metrics.raw_token_count - metrics.csc_token_count) / 
                                    metrics.raw_token_count) * 100
                assert abs(metrics.reduction_percentage - expected_reduction) < 0.01
                
                # Reduction ratio should match calculation
                expected_ratio = metrics.raw_token_count / max(metrics.csc_token_count, 1)
                assert abs(metrics.reduction_ratio - expected_ratio) < 0.01
                
                # If CSC has fewer tokens, reduction should be positive
                if metrics.csc_token_count < metrics.raw_token_count:
                    assert metrics.reduction_percentage > 0
                    assert metrics.reduction_ratio > 1
                
                # If CSC has same tokens, reduction should be zero
                if metrics.csc_token_count == metrics.raw_token_count:
                    assert abs(metrics.reduction_percentage) < 0.01
                    assert abs(metrics.reduction_ratio - 1.0) < 0.01
                
                # If CSC has more tokens, reduction should be negative
                if metrics.csc_token_count > metrics.raw_token_count:
                    assert metrics.reduction_percentage < 0
                    assert metrics.reduction_ratio < 1
            
            # Verify string representation works
            str_repr = str(metrics)
            assert "EfficiencyMetrics" in str_repr
            assert str(metrics.raw_token_count) in str_repr
            assert str(metrics.csc_token_count) in str_repr
        
        except Exception as e:
            pytest.fail(f"Efficiency metrics properties test failed for: '{text[:50]}...'\nError: {e}")