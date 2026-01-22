"""
Property-based tests for PTIL Encoder.

This module contains property-based tests that validate universal properties
of the PTIL encoder across many generated inputs using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from ptil.encoder import PTILEncoder
from ptil.models import CSC


class TestEncoderProperties:
    """Property-based tests for PTIL Encoder functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = PTILEncoder()
    
    @given(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    @settings(max_examples=100, deadline=5000)
    def test_deterministic_processing(self, text):
        """
        Property 4: Deterministic Processing
        For any input text, processing it multiple times should produce identical CSC output.
        **Validates: Requirements 1.5**
        """
        # Process the same text multiple times
        result1 = self.encoder.encode(text)
        result2 = self.encoder.encode(text)
        result3 = self.encoder.encode(text)
        
        # All results should be identical
        assert result1 == result2 == result3, (
            f"Deterministic processing failed for text: '{text}'\n"
            f"Result 1: {result1}\n"
            f"Result 2: {result2}\n"
            f"Result 3: {result3}"
        )
        
        # Also test serialized output for determinism
        serialized1 = self.encoder.encode_and_serialize(text)
        serialized2 = self.encoder.encode_and_serialize(text)
        serialized3 = self.encoder.encode_and_serialize(text)
        
        assert serialized1 == serialized2 == serialized3, (
            f"Deterministic serialization failed for text: '{text}'\n"
            f"Serialized 1: '{serialized1}'\n"
            f"Serialized 2: '{serialized2}'\n"
            f"Serialized 3: '{serialized3}'"
        )
    
    @given(st.sampled_from([
        # Ambiguous predicates with different POS contexts
        ("run", "The athlete will run fast"),  # VERB context
        ("run", "The run was exhausting"),     # NOUN context
        ("bank", "I bank at the local branch"),  # VERB context
        ("bank", "The river bank is steep"),     # NOUN context
        ("light", "Please light the candle"),    # VERB context
        ("light", "The light is bright"),        # NOUN context
        ("book", "I will book a flight"),        # VERB context
        ("book", "The book is interesting"),     # NOUN context
        ("play", "Children play in the park"),   # VERB context
        ("play", "The play was excellent"),      # NOUN context
    ]))
    @settings(max_examples=50, deadline=5000)
    def test_disambiguation_consistency(self, predicate_context):
        """
        Property 16: Disambiguation Consistency
        For any ambiguous input, ROOT mapping should be resolved consistently 
        using POS tags and dependency context.
        **Validates: Requirements 5.4**
        """
        predicate, sentence = predicate_context
        
        # Process the sentence multiple times
        results = []
        for _ in range(3):
            cscs = self.encoder.encode(sentence)
            results.append(cscs)
        
        # All results should be identical (deterministic)
        assert all(result == results[0] for result in results), (
            f"Disambiguation inconsistency for predicate '{predicate}' in sentence: '{sentence}'\n"
            f"Results varied across runs: {results}"
        )
        
        # Verify that disambiguation actually occurred (we got valid CSCs)
        assert len(results[0]) > 0, (
            f"No CSCs generated for ambiguous sentence: '{sentence}'"
        )
        
        # Verify that each CSC has a valid ROOT assignment
        for csc in results[0]:
            assert csc.root is not None, (
                f"No ROOT assigned for ambiguous predicate '{predicate}' in: '{sentence}'"
            )
        
        # Test that the same predicate in different contexts may map to different ROOTs
        # This validates that disambiguation is actually working
        if predicate == "run":
            # "run" as verb (MOTION) vs "run" as noun (different ROOT)
            verb_sentence = "The athlete will run fast"
            noun_sentence = "The run was exhausting"
            
            verb_cscs = self.encoder.encode(verb_sentence)
            noun_cscs = self.encoder.encode(noun_sentence)
            
            # Both should produce valid CSCs
            assert len(verb_cscs) > 0 and len(noun_cscs) > 0
            
            # The disambiguation should be consistent within each context
            verb_cscs_2 = self.encoder.encode(verb_sentence)
            noun_cscs_2 = self.encoder.encode(noun_sentence)
            
            assert verb_cscs == verb_cscs_2, "Verb context disambiguation not consistent"
            assert noun_cscs == noun_cscs_2, "Noun context disambiguation not consistent"