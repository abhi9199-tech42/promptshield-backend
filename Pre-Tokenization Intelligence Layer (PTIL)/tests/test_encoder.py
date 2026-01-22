"""
Integration tests for PTIL Encoder.

This module contains integration tests that validate the end-to-end
functionality of the PTIL encoder with various sentence types and
error handling scenarios.
"""

import pytest
from ptil.encoder import PTILEncoder
from ptil.models import CSC, ROOT, Role, META


class TestEncoderIntegration:
    """Integration tests for PTIL Encoder end-to-end functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = PTILEncoder()
    
    def test_simple_sentence_processing(self):
        """
        Test complete text processing with simple sentence types.
        Requirements: 1.5, 5.1, 5.2
        """
        # Test simple declarative sentence
        text = "The boy runs"
        cscs = self.encoder.encode(text)
        
        assert len(cscs) > 0, "Should generate at least one CSC"
        csc = cscs[0]
        
        # Verify CSC structure completeness
        assert csc.root is not None, "CSC should have a ROOT"
        assert isinstance(csc.ops, list), "CSC should have OPS list"
        assert isinstance(csc.roles, dict), "CSC should have ROLES dict"
        # META is optional
        
        # Verify serialization works
        serialized = self.encoder.encode_and_serialize(text)
        assert serialized, "Should produce serialized output"
        assert "<ROOT=" in serialized, "Serialized output should contain ROOT"
    
    def test_complex_sentence_processing(self):
        """
        Test processing of complex sentences with multiple components.
        Requirements: 1.5, 5.1, 5.2
        """
        # Test sentence with temporal, negation, and roles
        text = "The boy will not go to school tomorrow"
        cscs = self.encoder.encode(text)
        
        assert len(cscs) > 0, "Should generate at least one CSC"
        csc = cscs[0]
        
        # Verify components are present
        assert csc.root is not None, "Should have ROOT"
        assert len(csc.ops) > 0, "Should have operators (FUTURE, NEGATION)"
        assert len(csc.roles) > 0, "Should have role bindings"
        
        # Test serialization
        serialized = self.encoder.encode_and_serialize(text)
        assert "<ROOT=" in serialized, "Should contain ROOT"
        assert "<OPS=" in serialized, "Should contain OPS"
        assert "FUTURE" in serialized or "NEGATION" in serialized, "Should contain temporal/negation operators"
    
    def test_question_sentence_processing(self):
        """
        Test processing of interrogative sentences.
        Requirements: 1.5, 5.1, 5.2
        """
        text = "Where is the cat?"
        cscs = self.encoder.encode(text)
        
        assert len(cscs) > 0, "Should generate CSC for question"
        csc = cscs[0]
        
        # Should have basic structure
        assert csc.root is not None, "Question should have ROOT"
        
        # META might contain QUESTION marker
        if csc.meta:
            # If META is detected, it might be QUESTION
            pass  # META detection is optional and may vary
        
        # Verify serialization
        serialized = self.encoder.encode_and_serialize(text)
        assert serialized, "Should serialize question"
    
    def test_command_sentence_processing(self):
        """
        Test processing of imperative sentences.
        Requirements: 1.5, 5.1, 5.2
        """
        text = "Go to the store"
        cscs = self.encoder.encode(text)
        
        assert len(cscs) > 0, "Should generate CSC for command"
        csc = cscs[0]
        
        # Should have basic structure
        assert csc.root is not None, "Command should have ROOT"
        
        # Verify serialization
        serialized = self.encoder.encode_and_serialize(text)
        assert serialized, "Should serialize command"
    
    def test_multiple_predicate_processing(self):
        """
        Test processing of sentences with multiple predicates.
        Requirements: 1.5, 5.1, 5.2
        """
        text = "The boy runs and jumps"
        cscs = self.encoder.encode(text)
        
        # Should generate CSCs (may be one or multiple depending on implementation)
        assert len(cscs) > 0, "Should generate at least one CSC"
        
        # Verify each CSC has proper structure
        for csc in cscs:
            assert csc.root is not None, "Each CSC should have ROOT"
            assert isinstance(csc.ops, list), "Each CSC should have OPS"
            assert isinstance(csc.roles, dict), "Each CSC should have ROLES"
        
        # Verify serialization
        serialized = self.encoder.encode_and_serialize(text)
        assert serialized, "Should serialize multiple predicates"
    
    def test_empty_input_handling(self):
        """
        Test error handling for empty input.
        Requirements: 1.5
        """
        # Empty string
        cscs = self.encoder.encode("")
        assert cscs == [], "Empty string should return empty list"
        
        # Whitespace only
        cscs = self.encoder.encode("   ")
        assert cscs == [], "Whitespace-only should return empty list"
        
        # Serialization of empty input
        serialized = self.encoder.encode_and_serialize("")
        assert serialized == "", "Empty input should serialize to empty string"
    
    def test_invalid_input_handling(self):
        """
        Test error handling for invalid input types.
        Requirements: 1.5
        """
        # Non-string input should raise ValueError
        with pytest.raises(ValueError):
            self.encoder.encode(123)
        
        with pytest.raises(ValueError):
            self.encoder.encode(None)
        
        with pytest.raises(ValueError):
            self.encoder.encode(['list', 'input'])
    
    def test_malformed_text_handling(self):
        """
        Test graceful handling of malformed or unusual text.
        Requirements: 1.5
        """
        # Special characters and symbols
        text = "!@#$%^&*()"
        cscs = self.encoder.encode(text)
        # Should not crash, may return empty or fallback CSC
        assert isinstance(cscs, list), "Should return list even for special characters"
        
        # Very long text
        long_text = "The boy runs " * 100
        cscs = self.encoder.encode(long_text)
        assert isinstance(cscs, list), "Should handle long text"
        
        # Mixed languages (if supported)
        mixed_text = "Hello world 你好"
        cscs = self.encoder.encode(mixed_text)
        assert isinstance(cscs, list), "Should handle mixed language text"
    
    def test_component_integration(self):
        """
        Test that all components work together properly.
        Requirements: 1.5, 5.1, 5.2
        """
        text = "The student quickly reads the book"
        cscs = self.encoder.encode(text)
        
        assert len(cscs) > 0, "Should generate CSC"
        csc = cscs[0]
        
        # Verify all components contributed
        assert csc.root is not None, "ROOT mapper should contribute"
        # OPS may be empty for simple present tense
        assert isinstance(csc.ops, list), "OPS extractor should contribute"
        assert isinstance(csc.roles, dict), "ROLES binder should contribute"
        # META is optional
        
        # Verify component status
        status = self.encoder.get_component_status()
        expected_components = [
            'linguistic_analyzer', 'root_mapper', 'ops_extractor',
            'roles_binder', 'meta_detector', 'csc_generator', 'csc_serializer'
        ]
        
        for component in expected_components:
            assert component in status, f"Component {component} should be in status"
            assert status[component] is True, f"Component {component} should be initialized"
    
    def test_error_recovery_scenarios(self):
        """
        Test error handling and recovery in various failure scenarios.
        Requirements: 1.5
        """
        # Test with text that might cause parsing issues
        problematic_texts = [
            "...",  # Only punctuation
            "123 456 789",  # Only numbers
            "a",  # Single character
            "THE THE THE",  # Repeated words
            "This is a very long sentence with many words that might cause issues in processing and should still be handled gracefully by the system",  # Very long sentence
        ]
        
        for text in problematic_texts:
            try:
                cscs = self.encoder.encode(text)
                # Should not crash and should return a list
                assert isinstance(cscs, list), f"Should return list for text: '{text}'"
                
                # Try serialization too
                serialized = self.encoder.encode_and_serialize(text)
                assert isinstance(serialized, str), f"Should return string for text: '{text}'"
                
            except Exception as e:
                pytest.fail(f"Encoder crashed on text '{text}': {e}")
    
    def test_deterministic_behavior(self):
        """
        Test that the encoder produces consistent results.
        Requirements: 1.5
        """
        test_sentences = [
            "The cat sleeps",
            "Dogs bark loudly",
            "She will arrive tomorrow",
            "They are not coming"
        ]
        
        for sentence in test_sentences:
            # Process multiple times
            results = []
            for _ in range(3):
                cscs = self.encoder.encode(sentence)
                results.append(cscs)
            
            # All results should be identical
            assert all(result == results[0] for result in results), (
                f"Non-deterministic behavior for sentence: '{sentence}'"
            )
            
            # Test serialization determinism too
            serialized_results = []
            for _ in range(3):
                serialized = self.encoder.encode_and_serialize(sentence)
                serialized_results.append(serialized)
            
            assert all(result == serialized_results[0] for result in serialized_results), (
                f"Non-deterministic serialization for sentence: '{sentence}'"
            )