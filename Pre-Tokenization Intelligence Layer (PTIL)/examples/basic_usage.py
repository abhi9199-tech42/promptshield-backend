#!/usr/bin/env python3
"""
Basic Usage Example for PTIL Semantic Encoder

This script demonstrates the fundamental usage of the PTIL system for converting
natural language text into Compressed Semantic Code (CSC) representations.
"""

import sys
import os

# Add the parent directory to the path to import ptil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ptil import PTILEncoder, TrainingConfig


def main():
    """Demonstrate basic PTIL encoder usage."""
    print("=== PTIL Semantic Encoder - Basic Usage Example ===\n")
    
    # Initialize the encoder
    print("1. Initializing PTIL Encoder...")
    try:
        encoder = PTILEncoder()
        print("   ✓ Encoder initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize encoder: {e}")
        return
    
    # Example sentences to process
    examples = [
        "The boy runs to school.",
        "She will not go home tomorrow.",
        "Did you see the movie?",
        "Please close the door.",
        "I think it might rain today."
    ]
    
    print("\n2. Processing example sentences...")
    print("-" * 50)
    
    for i, text in enumerate(examples, 1):
        print(f"\nExample {i}: '{text}'")
        
        try:
            # Basic encoding
            cscs = encoder.encode(text)
            print(f"   Generated {len(cscs)} CSC(s):")
            
            for j, csc in enumerate(cscs):
                print(f"     CSC {j+1}:")
                print(f"       ROOT: {csc.root.value}")
                print(f"       OPS: {[op.value for op in csc.ops]}")
                print(f"       ROLES: {[(role.value, entity.text) for role, entity in csc.roles.items()]}")
                print(f"       META: {csc.meta.value if csc.meta else None}")
            
            # Serialized output
            serialized = encoder.encode_and_serialize(text)
            print(f"   Serialized: {serialized}")
            
        except Exception as e:
            print(f"   ✗ Error processing: {e}")
    
    print("\n3. Different serialization formats...")
    print("-" * 50)
    
    test_text = "The boy will not go to school tomorrow."
    print(f"\nTest sentence: '{test_text}'")
    
    formats = ["verbose", "compact", "ultra"]
    for fmt in formats:
        try:
            serialized = encoder.encode_and_serialize(test_text, format=fmt)
            print(f"   {fmt.capitalize()}: {serialized}")
        except Exception as e:
            print(f"   ✗ {fmt.capitalize()} format error: {e}")
    
    print("\n4. Training format output...")
    print("-" * 50)
    
    try:
        # Standard training format
        training_output = encoder.encode_for_training(test_text)
        print(f"   Standard: {training_output}")
        
        # CSC-only format
        csc_config = TrainingConfig(format_type="csc_only")
        encoder.set_training_config(csc_config)
        csc_only = encoder.encode_for_training(test_text)
        print(f"   CSC-only: {csc_only}")
        
        # Mixed format
        mixed_config = TrainingConfig(format_type="mixed", csc_weight=2.0, original_weight=1.0)
        encoder.set_training_config(mixed_config)
        mixed_output = encoder.encode_for_training(test_text)
        print(f"   Mixed: {mixed_output}")
        
    except Exception as e:
        print(f"   ✗ Training format error: {e}")
    
    print("\n5. Component status check...")
    print("-" * 50)
    
    try:
        status = encoder.get_component_status()
        print("   Component Status:")
        for component, is_active in status.items():
            status_symbol = "✓" if is_active else "✗"
            print(f"     {status_symbol} {component}")
    except Exception as e:
        print(f"   ✗ Status check error: {e}")
    
    print("\n=== Basic Usage Example Complete ===")


if __name__ == "__main__":
    main()