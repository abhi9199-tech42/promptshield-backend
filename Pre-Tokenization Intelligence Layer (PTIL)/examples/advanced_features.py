#!/usr/bin/env python3
"""
Advanced Features Demo for PTIL Semantic Encoder

This script demonstrates advanced PTIL features including:
- Custom training configurations
- Different serialization formats
- Error handling and recovery
- Component introspection
- Batch processing
"""

import sys
import os
import json
from typing import List, Dict, Any

# Add the parent directory to the path to import ptil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ptil import (
    PTILEncoder, TrainingConfig, ROOT, Operator, Role, META,
    CSC, Entity, EfficiencyAnalyzer, TokenizerCompatibilityValidator,
    TokenizerType
)


def demonstrate_training_configurations():
    """Demonstrate different training configuration options."""
    print("=== Training Configuration Demo ===\n")
    
    encoder = PTILEncoder()
    test_text = "The scientist discovered a new species in the rainforest."
    
    print(f"Test sentence: '{test_text}'\n")
    
    # Standard configuration
    print("1. Standard Training Format:")
    standard_config = TrainingConfig(
        format_type="standard",
        include_brackets=True,
        separator=" "
    )
    encoder.set_training_config(standard_config)
    standard_output = encoder.encode_for_training(test_text)
    print(f"   Output: {standard_output}\n")
    
    # CSC-only configuration
    print("2. CSC-Only Format:")
    csc_config = TrainingConfig(
        format_type="csc_only",
        include_brackets=True
    )
    encoder.set_training_config(csc_config)
    csc_output = encoder.encode_for_training(test_text)
    print(f"   Output: {csc_output}\n")
    
    # Mixed format with weights
    print("3. Mixed Format with Weights:")
    mixed_config = TrainingConfig(
        format_type="mixed",
        csc_weight=2.0,
        original_weight=1.0,
        include_brackets=True,
        separator=" | "
    )
    encoder.set_training_config(mixed_config)
    mixed_output = encoder.encode_for_training(test_text)
    print(f"   Output: {mixed_output}\n")
    
    # No brackets format
    print("4. No Brackets Format:")
    no_brackets_config = TrainingConfig(
        format_type="standard",
        include_brackets=False,
        separator=" "
    )
    encoder.set_training_config(no_brackets_config)
    no_brackets_output = encoder.encode_for_training(test_text)
    print(f"   Output: {no_brackets_output}\n")


def demonstrate_serialization_formats():
    """Demonstrate different CSC serialization formats."""
    print("=== Serialization Formats Demo ===\n")
    
    encoder = PTILEncoder()
    test_sentences = [
        "The boy runs quickly to school.",
        "She will not go home tomorrow.",
        "Did you finish your homework?",
        "Please be quiet in the library."
    ]
    
    formats = ["verbose", "compact", "ultra"]
    
    for sentence in test_sentences:
        print(f"Sentence: '{sentence}'")
        
        for fmt in formats:
            try:
                serialized = encoder.encode_and_serialize(sentence, format=fmt)
                print(f"   {fmt.capitalize()}: {serialized}")
            except Exception as e:
                print(f"   {fmt.capitalize()}: Error - {e}")
        
        print()


def demonstrate_error_handling():
    """Demonstrate error handling and recovery mechanisms."""
    print("=== Error Handling Demo ===\n")
    
    encoder = PTILEncoder()
    
    # Test cases with various error conditions
    error_test_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("12345", "Numbers only"),
        ("@#$%^&*()", "Special characters only"),
        ("This is a very long sentence that contains many words and might test the limits of the processing pipeline with complex grammatical structures and unusual patterns.", "Very long sentence"),
        ("Thîs sëntëncë hås ünüsüål chäräctërs.", "Unicode characters"),
        ("This sentence has\nnewlines\tand\ttabs.", "Control characters")
    ]
    
    print("Testing error handling with problematic inputs:\n")
    
    for test_input, description in error_test_cases:
        print(f"Test: {description}")
        print(f"Input: '{repr(test_input)}'")
        
        try:
            cscs = encoder.encode(test_input)
            if cscs:
                print(f"   ✓ Generated {len(cscs)} CSC(s)")
                for i, csc in enumerate(cscs):
                    print(f"     CSC {i+1}: ROOT={csc.root.value}, OPS={len(csc.ops)}, ROLES={len(csc.roles)}")
            else:
                print("   ⚠ No CSCs generated (graceful handling)")
            
            # Try serialization
            serialized = encoder.encode_and_serialize(test_input)
            if serialized:
                print(f"   ✓ Serialized: {serialized[:50]}{'...' if len(serialized) > 50 else ''}")
            else:
                print("   ⚠ Empty serialization (graceful handling)")
                
        except Exception as e:
            print(f"   ✗ Exception: {e}")
        
        print()


def demonstrate_component_introspection():
    """Demonstrate component introspection and status checking."""
    print("=== Component Introspection Demo ===\n")
    
    encoder = PTILEncoder()
    
    # Check component status
    print("1. Component Status Check:")
    status = encoder.get_component_status()
    for component, is_active in status.items():
        status_symbol = "✓" if is_active else "✗"
        print(f"   {status_symbol} {component}")
    
    print()
    
    # Demonstrate individual component access
    print("2. Individual Component Access:")
    
    test_text = "The researcher analyzed the complex data."
    
    try:
        # Linguistic analysis
        analysis = encoder.linguistic_analyzer.analyze(test_text)
        print(f"   Linguistic Analysis:")
        print(f"     Tokens: {analysis.tokens}")
        print(f"     POS Tags: {analysis.pos_tags}")
        print(f"     Dependencies: {len(analysis.dependencies)} relations")
        print(f"     Negation markers: {analysis.negation_markers}")
        print(f"     Tense markers: {analysis.tense_markers}")
        print(f"     Aspect markers: {analysis.aspect_markers}")
        
        # ROOT mapping
        if analysis.tokens:
            main_predicate = "analyzed"  # Known predicate in sentence
            root = encoder.root_mapper.map_predicate(main_predicate, "VERB", {})
            print(f"   ROOT Mapping: '{main_predicate}' → {root.value}")
        
        # Operator extraction
        ops = encoder.ops_extractor.extract_operators(analysis)
        print(f"   Operators: {[op.value for op in ops]}")
        
        # Role binding
        roles = encoder.roles_binder.bind_roles(analysis, ROOT.COGNITION)
        print(f"   Roles: {[(role.value, entity.text) for role, entity in roles.items()]}")
        
        # META detection
        meta = encoder.meta_detector.detect_meta(analysis)
        print(f"   META: {meta.value if meta else None}")
        
    except Exception as e:
        print(f"   ✗ Component introspection failed: {e}")
    
    print()


def demonstrate_batch_processing():
    """Demonstrate batch processing capabilities."""
    print("=== Batch Processing Demo ===\n")
    
    encoder = PTILEncoder()
    
    # Sample batch of sentences
    batch_sentences = [
        "The cat sleeps on the mat.",
        "Birds fly south for winter.",
        "She reads books every evening.",
        "The train arrives at noon.",
        "Children play in the park.",
        "Scientists study the stars.",
        "The chef cooks delicious meals.",
        "Students learn new concepts.",
        "The artist paints beautiful landscapes.",
        "Engineers design innovative solutions."
    ]
    
    print(f"Processing batch of {len(batch_sentences)} sentences:\n")
    
    # Process batch
    batch_results = []
    successful_processes = 0
    total_cscs = 0
    
    for i, sentence in enumerate(batch_sentences, 1):
        print(f"{i:2d}. '{sentence}'")
        
        try:
            cscs = encoder.encode(sentence)
            serialized = encoder.encode_and_serialize(sentence, format="compact")
            
            result = {
                "sentence": sentence,
                "cscs": cscs,
                "serialized": serialized,
                "success": True
            }
            
            successful_processes += 1
            total_cscs += len(cscs)
            
            print(f"    ✓ {len(cscs)} CSC(s): {serialized}")
            
        except Exception as e:
            result = {
                "sentence": sentence,
                "cscs": [],
                "serialized": "",
                "success": False,
                "error": str(e)
            }
            
            print(f"    ✗ Error: {e}")
        
        batch_results.append(result)
    
    # Batch statistics
    print(f"\nBatch Processing Summary:")
    print(f"   Total sentences: {len(batch_sentences)}")
    print(f"   Successful: {successful_processes}")
    print(f"   Failed: {len(batch_sentences) - successful_processes}")
    print(f"   Success rate: {successful_processes/len(batch_sentences)*100:.1f}%")
    print(f"   Total CSCs generated: {total_cscs}")
    print(f"   Average CSCs per sentence: {total_cscs/successful_processes:.1f}" if successful_processes > 0 else "   Average CSCs per sentence: N/A")


def demonstrate_efficiency_analysis():
    """Demonstrate efficiency analysis capabilities."""
    print("=== Efficiency Analysis Demo ===\n")
    
    encoder = PTILEncoder()
    efficiency_analyzer = EfficiencyAnalyzer()
    
    test_sentences = [
        "Hello world.",
        "The quick brown fox jumps over the lazy dog.",
        "In the beginning was the Word, and the Word was with God, and the Word was God.",
        "To be or not to be, that is the question.",
        "The mitochondria is the powerhouse of the cell."
    ]
    
    print("Analyzing token efficiency for various sentences:\n")
    
    all_metrics = []
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"{i}. '{sentence}'")
        
        try:
            metrics = efficiency_analyzer.analyze_efficiency(sentence, encoder)
            all_metrics.append(metrics)
            
            print(f"   Original tokens: {metrics.original_tokens}")
            print(f"   CSC tokens: {metrics.csc_tokens}")
            print(f"   Reduction: {metrics.reduction_percentage:.1f}%")
            print(f"   Compression ratio: {metrics.compression_ratio:.2f}x")
            print(f"   Efficiency score: {metrics.efficiency_score:.2f}")
            
        except Exception as e:
            print(f"   ✗ Analysis failed: {e}")
        
        print()
    
    # Aggregate analysis
    if all_metrics:
        print("Aggregate Efficiency Metrics:")
        try:
            aggregate = efficiency_analyzer.calculate_aggregate_metrics(all_metrics)
            print(f"   Average original tokens: {aggregate.original_tokens:.1f}")
            print(f"   Average CSC tokens: {aggregate.csc_tokens:.1f}")
            print(f"   Average reduction: {aggregate.reduction_percentage:.1f}%")
            print(f"   Average compression ratio: {aggregate.compression_ratio:.2f}x")
            print(f"   Average efficiency score: {aggregate.efficiency_score:.2f}")
        except Exception as e:
            print(f"   ✗ Aggregate calculation failed: {e}")


def demonstrate_tokenizer_compatibility():
    """Demonstrate tokenizer compatibility testing."""
    print("=== Tokenizer Compatibility Demo ===\n")
    
    encoder = PTILEncoder()
    validator = TokenizerCompatibilityValidator()
    
    test_sentence = "The advanced AI system processes natural language efficiently."
    print(f"Test sentence: '{test_sentence}'\n")
    
    # Test different serialization formats with different tokenizers
    formats = ["verbose", "compact", "ultra"]
    tokenizers = [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
    
    for fmt in formats:
        print(f"{fmt.capitalize()} format:")
        
        try:
            serialized = encoder.encode_and_serialize(test_sentence, format=fmt)
            print(f"   Serialized: {serialized}")
            
            for tokenizer in tokenizers:
                try:
                    result = validator.validate_compatibility(serialized, tokenizer)
                    
                    if result.is_compatible:
                        print(f"   ✓ {tokenizer.value}: Compatible ({result.token_count} tokens)")
                    else:
                        print(f"   ✗ {tokenizer.value}: {result.error_message}")
                        
                except Exception as e:
                    print(f"   ✗ {tokenizer.value}: Validation error - {e}")
            
        except Exception as e:
            print(f"   ✗ Serialization failed: {e}")
        
        print()


def main():
    """Run all advanced feature demonstrations."""
    print("=== PTIL Advanced Features Demo ===\n")
    
    try:
        demonstrate_training_configurations()
        print("\n" + "="*60 + "\n")
        
        demonstrate_serialization_formats()
        print("\n" + "="*60 + "\n")
        
        demonstrate_error_handling()
        print("\n" + "="*60 + "\n")
        
        demonstrate_component_introspection()
        print("\n" + "="*60 + "\n")
        
        demonstrate_batch_processing()
        print("\n" + "="*60 + "\n")
        
        demonstrate_efficiency_analysis()
        print("\n" + "="*60 + "\n")
        
        demonstrate_tokenizer_compatibility()
        
        print("\n=== Advanced Features Demo Complete ===")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()