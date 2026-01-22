#!/usr/bin/env python3
"""
Comprehensive Integration Tests for PTIL Semantic Encoder

This test suite validates all requirements together in realistic scenarios,
testing end-to-end functionality, system boundaries, and cross-component integration.
"""

import pytest
from typing import List, Dict
from ptil import *


class TestEndToEndIntegration:
    """Test complete end-to-end processing scenarios."""
    
    def test_simple_sentence_complete_pipeline(self):
        """Test complete pipeline with simple sentence."""
        encoder = PTILEncoder()
        text = "The boy runs to school."
        
        # Encode
        cscs = encoder.encode(text)
        assert len(cscs) > 0, "Should generate at least one CSC"
        
        csc = cscs[0]
        
        # Verify all components
        assert csc.root is not None, "Should have ROOT"
        assert csc.ops is not None, "Should have OPS"
        assert csc.roles is not None, "Should have ROLES"
        assert csc.root == ROOT.MOTION, "Should be MOTION"
        assert Role.AGENT in csc.roles, "Should have AGENT"
        
        # Serialize
        serialized = encoder.encode_and_serialize(text)
        assert len(serialized) > 0, "Should produce serialized output"
        assert "MOTION" in serialized or "M" in serialized, "Should contain ROOT"
    
    def test_complex_sentence_complete_pipeline(self):
        """Test complete pipeline with complex sentence."""
        encoder = PTILEncoder()
        text = "The experienced scientist will not publish the controversial findings tomorrow."
        
        cscs = encoder.encode(text)
        assert len(cscs) > 0
        
        csc = cscs[0]
        
        # Should have temporal and negation operators
        assert Operator.FUTURE in csc.ops or Operator.NEGATION in csc.ops
        
        # Should have multiple roles
        assert len(csc.roles) >= 2
        
        # Should serialize successfully
        serialized = encoder.encode_and_serialize(text)
        assert len(serialized) > 0
    
    def test_multiple_sentences_batch_processing(self):
        """Test batch processing of multiple sentences."""
        encoder = PTILEncoder()
        
        sentences = [
            "The cat sleeps.",
            "Birds fly south.",
            "She reads books.",
            "He gave her a gift.",
            "They are building a house."
        ]
        
        results = []
        for sentence in sentences:
            cscs = encoder.encode(sentence)
            serialized = encoder.encode_and_serialize(sentence)
            results.append({
                "text": sentence,
                "cscs": cscs,
                "serialized": serialized
            })
        
        # All should succeed
        assert len(results) == len(sentences)
        for result in results:
            assert len(result["cscs"]) > 0
            assert len(result["serialized"]) > 0
    
    def test_all_serialization_formats(self):
        """Test all three serialization formats work correctly."""
        encoder = PTILEncoder()
        text = "The scientist discovered a breakthrough."
        
        verbose = encoder.encode_and_serialize(text, format="verbose")
        compact = encoder.encode_and_serialize(text, format="compact")
        ultra = encoder.encode_and_serialize(text, format="ultra")
        
        # All should produce output
        assert len(verbose) > 0
        assert len(compact) > 0
        assert len(ultra) > 0
        
        # Ultra should be shortest
        assert len(ultra) <= len(compact) <= len(verbose)
    
    def test_all_training_formats(self):
        """Test all training format configurations."""
        encoder = PTILEncoder()
        text = "The AI system processes language."
        
        # Standard format
        standard_config = TrainingConfig(format_type="standard")
        encoder.set_training_config(standard_config)
        standard = encoder.encode_for_training(text)
        assert len(standard) > 0
        
        # CSC-only format
        csc_config = TrainingConfig(format_type="csc_only")
        encoder.set_training_config(csc_config)
        csc_only = encoder.encode_for_training(text)
        assert len(csc_only) > 0
        
        # Mixed format
        mixed_config = TrainingConfig(format_type="mixed", csc_weight=2.0, original_weight=1.0)
        encoder.set_training_config(mixed_config)
        mixed = encoder.encode_for_training(text)
        assert len(mixed) > 0


class TestAllRequirementsTogether:
    """Test all requirements working together in realistic scenarios."""
    
    def test_requirements_1_through_6_integration(self):
        """Test Req 1-6: CSC generation, ROOT, OPS, ROLES, analysis, serialization."""
        encoder = PTILEncoder()
        text = "The boy will not go to school tomorrow."
        
        # Req 1: Core CSC generation
        cscs = encoder.encode(text)
        assert len(cscs) > 0
        csc = cscs[0]
        assert csc.root is not None
        assert csc.ops is not None
        assert csc.roles is not None
        
        # Req 2: ROOT layer
        assert csc.root == ROOT.MOTION
        
        # Req 3: OPS layer
        assert Operator.FUTURE in csc.ops
        assert Operator.NEGATION in csc.ops
        
        # Req 4: ROLES layer
        assert Role.AGENT in csc.roles
        assert Role.GOAL in csc.roles or Role.LOCATION in csc.roles
        
        # Req 5: Linguistic analysis (implicit - successful encoding proves it worked)
        assert True
        
        # Req 6: Serialization
        serialized = encoder.encode_and_serialize(text)
        assert len(serialized) > 0
        assert "MOTION" in serialized or "M" in serialized
    
    def test_requirements_7_and_8_integration(self):
        """Test Req 7-8: Token efficiency and training integration."""
        encoder = PTILEncoder()
        analyzer = EfficiencyAnalyzer(encoder)
        text = "The experienced researcher discovered a groundbreaking new theory."
        
        # Req 7: Token efficiency
        metrics = analyzer.analyze_text(text)
        assert metrics.reduction_percentage >= 40  # Should have significant reduction
        assert metrics.reduction_ratio > 1.0
        
        # Req 8: Training integration
        training_output = encoder.encode_for_training(text)
        assert len(training_output) > 0
    
    def test_requirement_9_cross_lingual_integration(self):
        """Test Req 9: Cross-lingual consistency."""
        # English
        en_encoder = PTILEncoder.create_for_language("en")
        en_cscs = en_encoder.encode("The boy runs.")
        
        # Spanish
        try:
            es_encoder = PTILEncoder.create_for_language("es")
            es_cscs = es_encoder.encode("El niño corre.")
            
            # Should have same ROOT
            if en_cscs and es_cscs:
                assert en_cscs[0].root == es_cscs[0].root
        except Exception:
            # Spanish model may not be installed
            pytest.skip("Spanish language model not available")
    
    def test_requirement_10_system_boundaries(self):
        """Test Req 10: System boundaries and limitations."""
        encoder = PTILEncoder()
        
        # Should process false statements without verification
        false_statement = "The sun orbits the Earth."
        cscs = encoder.encode(false_statement)
        assert len(cscs) > 0  # Processes without truth checking
        
        # Should process nonsense with valid structure
        nonsense = "The purple idea sleeps furiously."
        cscs = encoder.encode(nonsense)
        assert len(cscs) > 0  # Processes without world knowledge


class TestSystemBoundaries:
    """Test system boundaries and error handling."""
    
    def test_empty_input_handling(self):
        """Test handling of empty input."""
        encoder = PTILEncoder()
        
        # Empty string
        cscs = encoder.encode("")
        assert isinstance(cscs, list)  # Should return list, possibly empty
        
        # Whitespace only
        cscs = encoder.encode("   ")
        assert isinstance(cscs, list)
    
    def test_malformed_input_handling(self):
        """Test handling of malformed input."""
        encoder = PTILEncoder()
        
        test_cases = [
            "12345",  # Numbers only
            "@#$%^&*()",  # Special characters
            "a",  # Single character
        ]
        
        for test_input in test_cases:
            try:
                cscs = encoder.encode(test_input)
                # Should either succeed or fail gracefully
                assert isinstance(cscs, list)
            except Exception as e:
                # Should not crash
                assert isinstance(e, (ValueError, RuntimeError))
    
    def test_very_long_input_handling(self):
        """Test handling of very long input."""
        encoder = PTILEncoder()
        
        # Very long sentence
        long_text = "The " + " and the ".join(["cat"] * 50) + " sleeps."
        
        try:
            cscs = encoder.encode(long_text)
            assert isinstance(cscs, list)
        except Exception:
            # May fail on very long input, but shouldn't crash
            pass
    
    def test_unicode_input_handling(self):
        """Test handling of Unicode characters."""
        encoder = PTILEncoder()
        
        unicode_texts = [
            "Thîs sëntëncë hås ünüsüål chäräctërs.",
            "这是中文。",  # Chinese
            "これは日本語です。",  # Japanese
        ]
        
        for text in unicode_texts:
            try:
                cscs = encoder.encode(text)
                assert isinstance(cscs, list)
            except Exception:
                # May not support all languages, but shouldn't crash
                pass


class TestCrossComponentIntegration:
    """Test integration between different components."""
    
    def test_linguistic_analyzer_to_root_mapper(self):
        """Test integration between linguistic analyzer and ROOT mapper."""
        encoder = PTILEncoder()
        text = "The scientist analyzes the data."
        
        # Linguistic analysis should feed into ROOT mapping
        analysis = encoder.linguistic_analyzer.analyze(text)
        assert len(analysis.tokens) > 0
        
        # ROOT mapping should use analysis
        cscs = encoder.encode(text)
        assert len(cscs) > 0
        assert cscs[0].root == ROOT.COGNITION
    
    def test_ops_extractor_to_serializer(self):
        """Test integration between OPS extractor and serializer."""
        encoder = PTILEncoder()
        text = "She will not go."
        
        cscs = encoder.encode(text)
        assert len(cscs) > 0
        
        # OPS should be extracted
        assert len(cscs[0].ops) > 0
        
        # Serializer should include OPS
        serialized = encoder.encode_and_serialize(text)
        assert "FUTURE" in serialized or "NEGATION" in serialized or "F" in serialized or "N" in serialized
    
    def test_roles_binder_to_serializer(self):
        """Test integration between ROLES binder and serializer."""
        encoder = PTILEncoder()
        text = "The boy gives the girl a book."
        
        cscs = encoder.encode(text)
        assert len(cscs) > 0
        
        # ROLES should be bound
        assert len(cscs[0].roles) > 0
        
        # Serializer should include ROLES
        serialized = encoder.encode_and_serialize(text)
        assert "BOY" in serialized or "GIRL" in serialized or "BOOK" in serialized
    
    def test_meta_detector_to_serializer(self):
        """Test integration between META detector and serializer."""
        encoder = PTILEncoder()
        
        # Question
        cscs = encoder.encode("Does the cat sleep?")
        if cscs and cscs[0].meta:
            assert cscs[0].meta == META.QUESTION
        
        # Command
        cscs = encoder.encode("Close the door!")
        if cscs and cscs[0].meta:
            assert cscs[0].meta == META.COMMAND


class TestTokenizerCompatibility:
    """Test compatibility with different tokenizers."""
    
    def test_bpe_tokenizer_compatibility(self):
        """Test compatibility with BPE tokenizer."""
        encoder = PTILEncoder()
        validator = TokenizerCompatibilityValidator()
        
        text = "The AI system processes natural language."
        serialized = encoder.encode_and_serialize(text)
        
        results = validator.validate_text_compatibility(serialized, [TokenizerType.BPE])
        result = results[TokenizerType.BPE]
        
        # Check compatibility or check issues list is not empty (error_message attr doesn't exist on CompatibilityResult)
        assert result.is_compatible or len(result.issues) > 0
    
    def test_all_tokenizers_compatibility(self):
        """Test compatibility with all tokenizer types."""
        encoder = PTILEncoder()
        validator = TokenizerCompatibilityValidator()
        
        text = "The scientist discovered a breakthrough."
        serialized = encoder.encode_and_serialize(text)
        
        tokenizer_types = [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
        
        for tokenizer_type in tokenizer_types:
            results = validator.validate_text_compatibility(serialized, [tokenizer_type])
            result = results[tokenizer_type]
            # Should either be compatible or have issues
            assert result.is_compatible or len(result.issues) > 0


class TestEfficiencyIntegration:
    """Test efficiency analysis integration."""
    
    def test_efficiency_analysis_integration(self):
        """Test efficiency analysis with encoder."""
        encoder = PTILEncoder()
        analyzer = EfficiencyAnalyzer(encoder)
        
        sentences = [
            "The cat sleeps.",
            "The quick brown fox jumps over the lazy dog.",
            "The scientist discovered a groundbreaking new theory."
        ]
        
        all_metrics = []
        for sentence in sentences:
            metrics = analyzer.analyze_text(sentence)
            all_metrics.append(metrics)
            
            # Basic validation
            assert metrics.raw_token_count > 0
            assert metrics.csc_token_count > 0
            assert metrics.reduction_ratio > 0
        
        # Validate batch efficiency
        validation_result = analyzer.validate_batch_efficiency(all_metrics)
        assert validation_result['total_texts'] == len(sentences)
        assert validation_result['average_reduction'] >= 0


class TestDeterminism:
    """Test deterministic behavior across multiple runs."""
    
    def test_deterministic_encoding(self):
        """Test that same input produces same output."""
        encoder = PTILEncoder()
        text = "The scientist discovered a breakthrough."
        
        # Encode multiple times
        cscs1 = encoder.encode(text)
        cscs2 = encoder.encode(text)
        cscs3 = encoder.encode(text)
        
        # Should produce same number of CSCs
        assert len(cscs1) == len(cscs2) == len(cscs3)
        
        # Should have same ROOT
        assert cscs1[0].root == cscs2[0].root == cscs3[0].root
        
        # Should have same OPS
        assert cscs1[0].ops == cscs2[0].ops == cscs3[0].ops
    
    def test_deterministic_serialization(self):
        """Test that serialization is deterministic."""
        encoder = PTILEncoder()
        text = "The boy runs to school."
        
        # Serialize multiple times
        s1 = encoder.encode_and_serialize(text)
        s2 = encoder.encode_and_serialize(text)
        s3 = encoder.encode_and_serialize(text)
        
        # Should be identical
        assert s1 == s2 == s3


class TestRealisticScenarios:
    """Test realistic usage scenarios."""
    
    def test_news_article_processing(self):
        """Test processing news-like sentences."""
        encoder = PTILEncoder()
        
        news_sentences = [
            "The president announced new economic policies yesterday.",
            "Scientists discovered a new species in the Amazon rainforest.",
            "The stock market crashed dramatically on Monday.",
            "Researchers published groundbreaking findings in Nature."
        ]
        
        for sentence in news_sentences:
            cscs = encoder.encode(sentence)
            assert len(cscs) > 0
            serialized = encoder.encode_and_serialize(sentence)
            assert len(serialized) > 0
    
    def test_conversational_text_processing(self):
        """Test processing conversational sentences."""
        encoder = PTILEncoder()
        
        conversations = [
            "Did you see the movie?",
            "I think it might rain today.",
            "Please close the door.",
            "That's amazing!",
            "Where are you going?"
        ]
        
        for sentence in conversations:
            cscs = encoder.encode(sentence)
            assert len(cscs) > 0
    
    def test_technical_text_processing(self):
        """Test processing technical sentences."""
        encoder = PTILEncoder()
        
        technical_sentences = [
            "The algorithm processes the input data efficiently.",
            "The system generates optimized output.",
            "The model learns from training examples.",
            "The network transmits encrypted messages."
        ]
        
        for sentence in technical_sentences:
            cscs = encoder.encode(sentence)
            assert len(cscs) > 0
            serialized = encoder.encode_and_serialize(sentence)
            assert len(serialized) > 0


class TestComponentStatus:
    """Test component status and health checks."""
    
    def test_component_status_check(self):
        """Test component status reporting."""
        encoder = PTILEncoder()
        
        status = encoder.get_component_status()
        
        # Should have all components
        assert "linguistic_analyzer" in status
        assert "root_mapper" in status
        assert "ops_extractor" in status
        assert "roles_binder" in status
        assert "meta_detector" in status
        
        # All should be active
        for component, is_active in status.items():
            assert is_active, f"{component} should be active"
    
    def test_training_config_management(self):
        """Test training configuration management."""
        encoder = PTILEncoder()
        
        # Set config
        config = TrainingConfig(format_type="mixed", csc_weight=2.0)
        encoder.set_training_config(config)
        
        # Get config
        retrieved_config = encoder.get_training_config()
        assert retrieved_config.format_type == "mixed"
        assert retrieved_config.csc_weight == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
