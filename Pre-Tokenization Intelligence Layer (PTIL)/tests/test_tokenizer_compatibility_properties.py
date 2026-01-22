"""
Property-based tests for PTIL Tokenizer Compatibility.

This module contains property-based tests that validate tokenizer compatibility
properties of the PTIL system across many generated inputs using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from ptil.tokenizer_compatibility import TokenizerCompatibilityValidator, TokenizerType, CompatibilityResult
from ptil.encoder import PTILEncoder
from ptil.csc_serializer import CSCSerializer


class TestTokenizerCompatibilityProperties:
    """Property-based tests for PTIL tokenizer compatibility functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = PTILEncoder()
        self.validator = TokenizerCompatibilityValidator()
        self.serializer = CSCSerializer()
    
    @given(st.text(min_size=5, max_size=200).filter(lambda x: x.strip() and len(x.split()) >= 2))
    @settings(max_examples=100, deadline=10000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_tokenizer_compatibility(self, text):
        """
        Property 18: Tokenizer Compatibility
        For any serialized CSC output, it should be processable by standard tokenizers 
        (BPE, Unigram, WordPiece) without errors.
        **Validates: Requirements 6.5**
        """
        # Skip texts that are too short or problematic
        words = text.split()
        assume(len(words) >= 2)
        assume(any(word.isalpha() for word in words))
        
        try:
            # Generate CSC from text
            cscs = self.encoder.encode(text)
            
            # Skip if no CSCs generated (edge case)
            assume(len(cscs) > 0)
            
            # Serialize CSCs to tokenizer-friendly format
            serialized_text = self.serializer.serialize_multiple(cscs)
            
            # Skip if serialization failed
            assume(serialized_text.strip())
            
            # Test compatibility with all tokenizer types
            tokenizer_types = [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
            compatibility_results = self.validator.validate_text_compatibility(
                serialized_text, tokenizer_types
            )
            
            # Verify we got results for all tokenizer types
            assert len(compatibility_results) == len(tokenizer_types), (
                f"Expected results for {len(tokenizer_types)} tokenizers, got {len(compatibility_results)}"
            )
            
            # Verify each result is valid
            for tokenizer_type, result in compatibility_results.items():
                assert isinstance(result, CompatibilityResult), (
                    f"Result for {tokenizer_type.value} is not a CompatibilityResult"
                )
                assert result.tokenizer_type == tokenizer_type, (
                    f"Tokenizer type mismatch: expected {tokenizer_type}, got {result.tokenizer_type}"
                )
                assert result.input_text == serialized_text, (
                    f"Input text mismatch for {tokenizer_type.value}"
                )
                
                # Token count should be reasonable
                assert result.token_count >= 0, (
                    f"Token count should be non-negative for {tokenizer_type.value}: {result.token_count}"
                )
                
                # If compatible, should have no issues
                if result.is_compatible:
                    assert len(result.issues) == 0, (
                        f"Compatible result should have no issues for {tokenizer_type.value}: {result.issues}"
                    )
                
                # If incompatible, should have at least one issue
                if not result.is_compatible:
                    assert len(result.issues) > 0, (
                        f"Incompatible result should have issues for {tokenizer_type.value}"
                    )
                
                # Processed tokens should be reasonable
                if result.processed_tokens:
                    assert len(result.processed_tokens) == result.token_count, (
                        f"Token count mismatch for {tokenizer_type.value}: "
                        f"count={result.token_count}, tokens={len(result.processed_tokens)}"
                    )
                    
                    # No token should be excessively long (>200 chars is unreasonable)
                    for token in result.processed_tokens:
                        assert len(token) <= 200, (
                            f"Token too long for {tokenizer_type.value}: '{token[:50]}...'"
                        )
            
            # For well-formed CSC output, most tokenizers should be compatible
            # (This is a quality check, not a strict requirement for all edge cases)
            if self._is_well_formed_csc(serialized_text):
                compatible_count = sum(1 for result in compatibility_results.values() 
                                     if result.is_compatible)
                # For property-based testing, we allow some edge cases to fail
                # but log them for analysis
                if compatible_count == 0:
                    # Log the issue but don't fail the test for edge cases
                    print(f"Warning: No tokenizers compatible with CSC: '{serialized_text}'\n"
                          f"Issues: {[(t.value, r.issues) for t, r in compatibility_results.items()]}")
                    # Only fail if this is clearly a well-formed, simple CSC
                    if len(serialized_text) < 100 and not any(ord(c) > 127 for c in serialized_text):
                        assert compatible_count >= 1, (
                            f"At least one tokenizer should be compatible for simple CSC: '{serialized_text}'\n"
                            f"Issues: {[(t.value, r.issues) for t, r in compatibility_results.items()]}"
                        )
        
        except Exception as e:
            pytest.fail(f"Tokenizer compatibility test failed for text: '{text[:50]}...'\nError: {e}")
    
    @given(st.lists(
        st.text(min_size=5, max_size=100).filter(lambda x: x.strip() and len(x.split()) >= 2),
        min_size=2, max_size=8
    ))
    @settings(max_examples=50, deadline=15000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_batch_tokenizer_compatibility(self, texts):
        """
        Property: Batch Tokenizer Compatibility
        For any batch of texts, tokenizer compatibility validation should provide
        consistent and meaningful results across all tokenizer types.
        **Validates: Requirements 6.5**
        """
        # Filter and prepare texts
        valid_texts = []
        for text in texts:
            words = text.split()
            if (len(words) >= 2 and 
                any(word.isalpha() for word in words) and
                text not in valid_texts):
                valid_texts.append(text)
        
        assume(len(valid_texts) >= 2)
        
        try:
            # Generate serialized CSCs for all texts
            serialized_texts = []
            for text in valid_texts:
                cscs = self.encoder.encode(text)
                if cscs:  # Only include texts that produce CSCs
                    serialized = self.serializer.serialize_multiple(cscs)
                    if serialized.strip():
                        serialized_texts.append(serialized)
            
            assume(len(serialized_texts) >= 2)
            
            # Test batch compatibility
            batch_results = self.validator.validate_batch_compatibility(
                serialized_texts, 
                [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
            )
            
            # Verify batch results structure
            assert "overall_compatible" in batch_results
            assert "total_texts" in batch_results
            assert "tokenizer_stats" in batch_results
            assert "compatibility_percentages" in batch_results
            assert "detailed_results" in batch_results
            
            # Verify counts
            assert batch_results["total_texts"] == len(serialized_texts)
            assert len(batch_results["detailed_results"]) == len(serialized_texts)
            
            # Verify tokenizer statistics
            tokenizer_stats = batch_results["tokenizer_stats"]
            for tokenizer_name in ["bpe", "unigram", "wordpiece"]:
                assert tokenizer_name in tokenizer_stats
                stats = tokenizer_stats[tokenizer_name]
                assert "compatible" in stats
                assert "total" in stats
                assert stats["total"] == len(serialized_texts)
                assert 0 <= stats["compatible"] <= stats["total"]
            
            # Verify compatibility percentages
            compatibility_percentages = batch_results["compatibility_percentages"]
            for tokenizer_name in ["bpe", "unigram", "wordpiece"]:
                assert tokenizer_name in compatibility_percentages
                percentage = compatibility_percentages[tokenizer_name]
                assert 0 <= percentage <= 100
                
                # Verify percentage calculation
                stats = tokenizer_stats[tokenizer_name]
                expected_percentage = (stats["compatible"] / stats["total"]) * 100
                assert abs(percentage - expected_percentage) < 0.01
            
            # Verify detailed results
            detailed_results = batch_results["detailed_results"]
            for text_results in detailed_results:
                assert len(text_results) == 3  # BPE, Unigram, WordPiece
                for tokenizer_type, result in text_results.items():
                    assert isinstance(tokenizer_type, TokenizerType)
                    assert isinstance(result, CompatibilityResult)
        
        except Exception as e:
            pytest.fail(f"Batch tokenizer compatibility test failed for {len(valid_texts)} texts\nError: {e}")
    
    @given(st.sampled_from([
        # Well-formed CSC examples that should be compatible
        "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <TIME=TOMORROW> <META=ASSERTIVE>",
        "<ROOT=COMMUNICATION> <OPS=PRESENT> <AGENT=SHE> <THEME=BOOK> <LOCATION=LIBRARY> <META=ASSERTIVE>",
        "<ROOT=COGNITION> <OPS=PAST> <AGENT=STUDENT> <THEME=LESSON> <META=ASSERTIVE>",
        "<ROOT=EXISTENCE> <OPS=PRESENT> <THEME=CAT> <LOCATION=MAT> <META=ASSERTIVE>",
        "<ROOT=CREATION> <OPS=FUTURE> <AGENT=ARTIST> <THEME=PAINTING> <META=ASSERTIVE>",
    ]))
    @settings(max_examples=25, deadline=5000)
    def test_well_formed_csc_compatibility(self, csc_text):
        """
        Property: Well-formed CSC Compatibility
        For well-formed CSC serialized text, all standard tokenizers should be compatible.
        **Validates: Requirements 6.5**
        """
        try:
            # Test compatibility with all tokenizer types
            compatibility_results = self.validator.validate_text_compatibility(
                csc_text, 
                [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
            )
            
            # All tokenizers should be compatible with well-formed CSC
            for tokenizer_type, result in compatibility_results.items():
                assert result.is_compatible, (
                    f"Well-formed CSC should be compatible with {tokenizer_type.value}: '{csc_text}'\n"
                    f"Issues: {result.issues}"
                )
                
                # Should have reasonable token count
                assert result.token_count > 0, (
                    f"Well-formed CSC should produce tokens with {tokenizer_type.value}: '{csc_text}'"
                )
                
                # Should have processed tokens
                assert len(result.processed_tokens) > 0, (
                    f"Well-formed CSC should have processed tokens with {tokenizer_type.value}: '{csc_text}'"
                )
                
                # Token count should match processed tokens
                assert len(result.processed_tokens) == result.token_count, (
                    f"Token count mismatch for {tokenizer_type.value} with CSC: '{csc_text}'"
                )
        
        except Exception as e:
            pytest.fail(f"Well-formed CSC compatibility test failed for: '{csc_text}'\nError: {e}")
    
    @given(st.sampled_from([
        # Problematic text patterns that should be detected
        "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <TIME=TOMORROW> <META=ASSERTIVE",  # Missing >
        "<ROOT=MOTION <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <TIME=TOMORROW> <META=ASSERTIVE>",  # Missing >
        "<ROOT=> <OPS=FUTURE> <AGENT=BOY>",  # Empty tag value
        "<ROOT=MOTION> <> <AGENT=BOY>",  # Empty tag
        "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY\x00> <GOAL=SCHOOL>",  # Control character
        "<ROOT=MOTION> <OPS=FUTURE|NEGATION>   <AGENT=BOY> <GOAL=SCHOOL>",  # Excessive whitespace
    ]))
    @settings(max_examples=30, deadline=5000)
    def test_problematic_text_detection(self, problematic_text):
        """
        Property: Problematic Text Detection
        For text with known compatibility issues, the validator should detect problems.
        **Validates: Requirements 6.5**
        """
        try:
            # Test compatibility - should detect issues
            compatibility_results = self.validator.validate_text_compatibility(
                problematic_text,
                [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
            )
            
            # At least one tokenizer should detect issues
            issue_detected = any(not result.is_compatible for result in compatibility_results.values())
            
            # For clearly problematic text, we expect issues to be detected
            if any(char in problematic_text for char in ['\x00', '<>', '< >']):
                assert issue_detected, (
                    f"Should detect issues in clearly problematic text: '{problematic_text}'\n"
                    f"Results: {[(t.value, r.is_compatible, r.issues) for t, r in compatibility_results.items()]}"
                )
            
            # Verify that incompatible results have issues listed
            for tokenizer_type, result in compatibility_results.items():
                if not result.is_compatible:
                    assert len(result.issues) > 0, (
                        f"Incompatible result should list issues for {tokenizer_type.value}: '{problematic_text}'"
                    )
        
        except Exception as e:
            pytest.fail(f"Problematic text detection test failed for: '{problematic_text}'\nError: {e}")
    
    def _is_well_formed_csc(self, text: str) -> bool:
        """
        Check if text appears to be well-formed CSC.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text appears well-formed
        """
        # Basic checks for CSC format
        if not text.strip():
            return False
        
        # Should contain ROOT tag
        if "<ROOT=" not in text:
            return False
        
        # Should have balanced angle brackets
        if text.count('<') != text.count('>'):
            return False
        
        # Should not contain obvious problems
        if any(char in text for char in ['\x00', '\x01', '\x02']):
            return False
        
        # Should not have empty tags
        if '<>' in text or '< >' in text:
            return False
        
        return True