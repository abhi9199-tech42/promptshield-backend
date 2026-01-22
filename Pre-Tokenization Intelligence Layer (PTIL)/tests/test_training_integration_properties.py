"""
Property-based tests for PTIL Training Integration.

This module contains property-based tests that validate universal properties
of the PTIL training format generation across many generated inputs using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from ptil.encoder import PTILEncoder, TrainingConfig


class TestTrainingIntegrationProperties:
    """Property-based tests for PTIL Training Integration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = PTILEncoder()
    
    @given(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    @settings(max_examples=100, deadline=5000)
    def test_training_integration_format(self, text):
        """
        Property 20: Training Integration Format
        For any input text, the training format should provide input format as 
        [CSC_SERIALIZATION] + [ORIGINAL_TEXT].
        **Validates: Requirements 8.1**
        """
        # Test standard training format
        training_output = self.encoder.encode_for_training(text)
        
        # Verify the format contains both CSC and original text components
        assert "[CSC]" in training_output, (
            f"Training format missing [CSC] component for text: '{text}'\n"
            f"Output: '{training_output}'"
        )
        
        assert "[TEXT]" in training_output, (
            f"Training format missing [TEXT] component for text: '{text}'\n"
            f"Output: '{training_output}'"
        )
        
        # Verify original text is preserved in the output
        assert text in training_output, (
            f"Original text not preserved in training format for: '{text}'\n"
            f"Output: '{training_output}'"
        )
        
        # Verify CSC component comes before TEXT component
        csc_pos = training_output.find("[CSC]")
        text_pos = training_output.find("[TEXT]")
        assert csc_pos < text_pos, (
            f"CSC component should come before TEXT component for: '{text}'\n"
            f"Output: '{training_output}'"
        )
        
        # Test CSC-only format
        csc_config = TrainingConfig(format_type="csc_only")
        csc_only_output = self.encoder.encode_for_training(text, csc_config)
        
        assert "[CSC]" in csc_only_output, (
            f"CSC-only format missing [CSC] component for text: '{text}'\n"
            f"Output: '{csc_only_output}'"
        )
        
        assert "[TEXT]" not in csc_only_output, (
            f"CSC-only format should not contain [TEXT] component for text: '{text}'\n"
            f"Output: '{csc_only_output}'"
        )
        
        # Test mixed format
        mixed_config = TrainingConfig(format_type="mixed", csc_weight=2.0, original_weight=1.0)
        mixed_output = self.encoder.encode_for_training(text, mixed_config)
        
        # Mixed format should contain both components
        assert "[CSC]" in mixed_output and "[TEXT]" in mixed_output, (
            f"Mixed format should contain both [CSC] and [TEXT] components for text: '{text}'\n"
            f"Output: '{mixed_output}'"
        )
        
        # CSC should appear more frequently due to higher weight
        csc_count = mixed_output.count("[CSC]")
        text_count = mixed_output.count("[TEXT]")
        assert csc_count >= text_count, (
            f"Mixed format should have more CSC components due to higher weight for text: '{text}'\n"
            f"CSC count: {csc_count}, TEXT count: {text_count}\n"
            f"Output: '{mixed_output}'"
        )
        
        # Test format without brackets
        no_brackets_config = TrainingConfig(include_brackets=False)
        no_brackets_output = self.encoder.encode_for_training(text, no_brackets_config)
        
        assert "[CSC]" not in no_brackets_output and "[TEXT]" not in no_brackets_output, (
            f"Format without brackets should not contain bracket markers for text: '{text}'\n"
            f"Output: '{no_brackets_output}'"
        )
        
        # Should still contain the original text
        assert text in no_brackets_output, (
            f"Format without brackets should still contain original text: '{text}'\n"
            f"Output: '{no_brackets_output}'"
        )
    
    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        st.sampled_from(["standard", "csc_only", "mixed"]),
        st.floats(min_value=0.1, max_value=5.0),
        st.floats(min_value=0.1, max_value=5.0),
        st.sampled_from([" ", " | ", " :: "]),
        st.booleans()
    )
    @settings(max_examples=50, deadline=5000)
    def test_training_config_consistency(self, text, format_type, csc_weight, 
                                       original_weight, separator, include_brackets):
        """
        Property: Training Configuration Consistency
        For any training configuration, the output should be consistent with the 
        specified parameters and deterministic across multiple calls.
        **Validates: Requirements 8.1**
        """
        config = TrainingConfig(
            format_type=format_type,
            csc_weight=csc_weight,
            original_weight=original_weight,
            separator=separator,
            include_brackets=include_brackets
        )
        
        # Generate training output multiple times
        output1 = self.encoder.encode_for_training(text, config)
        output2 = self.encoder.encode_for_training(text, config)
        output3 = self.encoder.encode_for_training(text, config)
        
        # Should be deterministic
        assert output1 == output2 == output3, (
            f"Training format not deterministic for text: '{text}'\n"
            f"Config: {config}\n"
            f"Output 1: '{output1}'\n"
            f"Output 2: '{output2}'\n"
            f"Output 3: '{output3}'"
        )
        
        # Verify bracket inclusion/exclusion
        if include_brackets:
            if format_type != "csc_only":
                assert "[TEXT]" in output1, (
                    f"Brackets enabled but [TEXT] missing for format {format_type}\n"
                    f"Output: '{output1}'"
                )
            if format_type != "text_only":  # CSC should be present in all our formats
                assert "[CSC]" in output1, (
                    f"Brackets enabled but [CSC] missing for format {format_type}\n"
                    f"Output: '{output1}'"
                )
        else:
            assert "[CSC]" not in output1 and "[TEXT]" not in output1, (
                f"Brackets disabled but bracket markers found in output\n"
                f"Output: '{output1}'"
            )
        
        # Verify separator usage (when applicable)
        if format_type == "standard" and include_brackets:
            # Should contain the separator between CSC and TEXT components
            csc_part = output1.split(separator)[0] if separator in output1 else output1
            assert "[CSC]" in csc_part, (
                f"Separator not properly used in standard format\n"
                f"Separator: '{separator}'\n"
                f"Output: '{output1}'"
            )
        
        # Verify original text preservation (except for CSC-only format)
        if format_type != "csc_only":
            assert text in output1, (
                f"Original text not preserved with config: {config}\n"
                f"Text: '{text}'\n"
                f"Output: '{output1}'"
            )
    
    @given(st.text(min_size=1, max_size=100).filter(lambda x: x.strip() and all(ord(c) >= 32 or c in '\t\n\r' for c in x)))
    @settings(max_examples=50, deadline=5000)
    def test_training_format_structure_validity(self, text):
        """
        Property: Training Format Structure Validity
        For any input text, the training format should maintain valid structure
        that can be parsed and used in training pipelines.
        **Validates: Requirements 8.1**
        """
        training_output = self.encoder.encode_for_training(text)
        
        # Should not be empty
        assert training_output.strip(), (
            f"Training format should not be empty for text: '{text}'"
        )
        
        # Should be a valid string (no None or other types)
        assert isinstance(training_output, str), (
            f"Training format should be a string, got {type(training_output)}"
        )
        
        # Should not contain malformed bracket structures
        open_brackets = training_output.count("[")
        close_brackets = training_output.count("]")
        assert open_brackets == close_brackets, (
            f"Mismatched brackets in training format for text: '{text}'\n"
            f"Output: '{training_output}'"
        )
        
        # If CSC component exists, it should contain valid CSC format
        if "[CSC]" in training_output:
            csc_start = training_output.find("[CSC]") + 5
            # Find the end of CSC component (either [TEXT] or end of string)
            text_start = training_output.find("[TEXT]")
            if text_start != -1:
                csc_content = training_output[csc_start:text_start].strip()
            else:
                csc_content = training_output[csc_start:].strip()
            
            # CSC content should contain angle brackets (symbolic format)
            if csc_content:  # Only check if CSC content is not empty
                assert "<" in csc_content and ">" in csc_content, (
                    f"CSC component should contain symbolic format for text: '{text}'\n"
                    f"CSC content: '{csc_content}'\n"
                    f"Full output: '{training_output}'"
                )
        
        # Test that the format is suitable for tokenizer processing
        # (no special characters that would break standard tokenizers)
        problematic_chars = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05"]
        for char in problematic_chars:
            assert char not in training_output, (
                f"Training format contains problematic character for tokenizers: {repr(char)}\n"
                f"Text: '{text}'\n"
                f"Output: '{training_output}'"
            )