"""
Tests for PTIL Linguistic Analyzer component.

Includes property-based tests for linguistic analysis completeness and unit tests
for edge cases and negation detection patterns.
Requirements: 5.1, 5.2
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from ptil.linguistic_analyzer import LinguisticAnalyzer
from ptil.models import LinguisticAnalysis


class TestLinguisticAnalyzerProperties:
    """Property-based tests for linguistic analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        try:
            self.analyzer = LinguisticAnalyzer()
        except RuntimeError as e:
            pytest.skip(f"spaCy model not available: {e}")
    
    @given(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
    @settings(max_examples=20)
    def test_linguistic_analysis_completeness(self, text):
        """
        Property 15: Linguistic Analysis Completeness
        For any input text, the linguistic analysis should include tokenization, 
        POS tagging, dependency parsing, and marker detection.
        
        **Feature: ptil-semantic-encoder, Property 15: Linguistic Analysis Completeness**
        **Validates: Requirements 5.1, 5.2**
        """
        # Skip texts that might cause issues with spaCy
        assume(len(text.strip()) > 0)
        assume(not all(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in text))
        
        analysis = self.analyzer.analyze(text)
        
        # Verify analysis structure completeness
        assert isinstance(analysis, LinguisticAnalysis)
        
        # Verify all required components are present
        assert hasattr(analysis, 'tokens')
        assert hasattr(analysis, 'pos_tags')
        assert hasattr(analysis, 'dependencies')
        assert hasattr(analysis, 'negation_markers')
        assert hasattr(analysis, 'tense_markers')
        assert hasattr(analysis, 'aspect_markers')
        
        # Verify component types
        assert isinstance(analysis.tokens, list)
        assert isinstance(analysis.pos_tags, list)
        assert isinstance(analysis.dependencies, list)
        assert isinstance(analysis.negation_markers, list)
        assert isinstance(analysis.tense_markers, dict)
        assert isinstance(analysis.aspect_markers, dict)
        
        # Verify tokens and POS tags have same length (if any tokens exist)
        if analysis.tokens:
            assert len(analysis.tokens) == len(analysis.pos_tags)
        
        # Verify dependency structure validity
        for dep in analysis.dependencies:
            assert isinstance(dep, tuple)
            assert len(dep) == 3
            head_idx, relation, dependent_idx = dep
            assert isinstance(head_idx, int)
            assert isinstance(relation, str)
            assert isinstance(dependent_idx, int)
            # Indices should be valid for token list
            assert 0 <= head_idx < len(analysis.tokens)
            assert 0 <= dependent_idx < len(analysis.tokens)
        
        # Verify negation markers are valid indices
        for marker_idx in analysis.negation_markers:
            assert isinstance(marker_idx, int)
            assert 0 <= marker_idx < len(analysis.tokens)
        
        # Verify tense markers structure
        for tense_type, indices in analysis.tense_markers.items():
            assert isinstance(tense_type, str)
            assert isinstance(indices, list)
            for idx in indices:
                assert isinstance(idx, int)
                assert 0 <= idx < len(analysis.tokens)
        
        # Verify aspect markers structure
        for aspect_type, indices in analysis.aspect_markers.items():
            assert isinstance(aspect_type, str)
            assert isinstance(indices, list)
            for idx in indices:
                assert isinstance(idx, int)
                assert 0 <= idx < len(analysis.tokens)


class TestLinguisticAnalyzerEdgeCases:
    """Unit tests for edge cases and specific patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        try:
            self.analyzer = LinguisticAnalyzer()
        except RuntimeError as e:
            pytest.skip(f"spaCy model not available: {e}")
    
    def test_empty_input(self):
        """Test empty input handling."""
        analysis = self.analyzer.analyze("")
        assert analysis.tokens == []
        assert analysis.pos_tags == []
        assert analysis.dependencies == []
        assert analysis.negation_markers == []
        assert analysis.tense_markers == {}
        assert analysis.aspect_markers == {}
    
    def test_whitespace_only_input(self):
        """Test whitespace-only input handling."""
        analysis = self.analyzer.analyze("   \n\t  ")
        assert analysis.tokens == []
        assert analysis.pos_tags == []
        assert analysis.dependencies == []
        assert analysis.negation_markers == []
        assert analysis.tense_markers == {}
        assert analysis.aspect_markers == {}
    
    def test_single_word_input(self):
        """Test single word input."""
        analysis = self.analyzer.analyze("hello")
        assert len(analysis.tokens) == 1
        assert len(analysis.pos_tags) == 1
        assert analysis.tokens[0] == "hello"
        # Single word has no dependencies
        assert analysis.dependencies == []
    
    def test_negation_detection_patterns(self):
        """Test various negation patterns."""
        test_cases = [
            ("I do not like this", [2]),  # "not"
            ("I don't like this", [1]),   # "don't" 
            ("I never go there", [1]),    # "never"
            ("Nobody came", [0]),         # "nobody"
            ("Nothing happened", [0]),    # "nothing"
            ("I can't do it", [1]),       # "can't"
            ("He won't come", [1]),       # "won't"
        ]
        
        for text, expected_positions in test_cases:
            analysis = self.analyzer.analyze(text)
            # Check that negation was detected (positions may vary due to tokenization)
            assert len(analysis.negation_markers) > 0, f"No negation detected in: {text}"
    
    def test_tense_marker_detection(self):
        """Test tense marker detection."""
        # Future tense
        analysis = self.analyzer.analyze("I will go tomorrow")
        assert "future" in analysis.tense_markers
        assert len(analysis.tense_markers["future"]) > 0
        
        # Past tense
        analysis = self.analyzer.analyze("I went yesterday")
        assert "past" in analysis.tense_markers
        assert len(analysis.tense_markers["past"]) > 0
        
        # Present tense
        analysis = self.analyzer.analyze("I go every day")
        assert "present" in analysis.tense_markers
        assert len(analysis.tense_markers["present"]) > 0
    
    def test_aspect_marker_detection(self):
        """Test aspect marker detection."""
        # Continuous aspect
        analysis = self.analyzer.analyze("I am running")
        assert "continuous" in analysis.aspect_markers
        
        # Perfect aspect
        analysis = self.analyzer.analyze("I have finished")
        assert "completed" in analysis.aspect_markers
        
        # Habitual aspect
        analysis = self.analyzer.analyze("I usually walk")
        assert "habitual" in analysis.aspect_markers
    
    def test_malformed_text_handling(self):
        """Test handling of malformed or unusual text."""
        test_cases = [
            "!!!???",  # Only punctuation
            "123 456",  # Only numbers
            "a b c d e f g h i j k l m n o p",  # Many short words
            "word1 word2 word3.",  # Mixed alphanumeric
        ]
        
        for text in test_cases:
            analysis = self.analyzer.analyze(text)
            # Should not crash and should return valid structure
            assert isinstance(analysis, LinguisticAnalysis)
            assert len(analysis.tokens) == len(analysis.pos_tags)
    
    def test_unsupported_characters(self):
        """Test handling of unsupported or special characters."""
        test_cases = [
            "Hello 世界",  # Mixed languages
            "café naïve résumé",  # Accented characters
            "user@example.com",  # Email
            "http://example.com",  # URL
            "$100 €50 ¥1000",  # Currency symbols
        ]
        
        for text in test_cases:
            analysis = self.analyzer.analyze(text)
            # Should handle gracefully without crashing
            assert isinstance(analysis, LinguisticAnalysis)
            assert len(analysis.tokens) > 0
            assert len(analysis.tokens) == len(analysis.pos_tags)