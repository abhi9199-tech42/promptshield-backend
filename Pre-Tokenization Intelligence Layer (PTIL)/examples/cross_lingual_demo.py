#!/usr/bin/env python3
"""
Cross-Lingual Consistency Demo for PTIL Semantic Encoder

This script demonstrates PTIL's ability to generate consistent semantic
representations across different languages for equivalent meanings.
"""

import sys
import os

# Add the parent directory to the path to import ptil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ptil import PTILEncoder, CrossLingualValidator


def main():
    """Demonstrate cross-lingual consistency in PTIL encoding."""
    print("=== PTIL Cross-Lingual Consistency Demo ===\n")
    
    # Test sentences in different languages with equivalent meanings
    test_cases = [
        {
            "concept": "Simple motion",
            "sentences": {
                "en": "The boy runs.",
                "es": "El niño corre.",
                "fr": "Le garçon court."
            }
        },
        {
            "concept": "Future negation",
            "sentences": {
                "en": "She will not go home.",
                "es": "Ella no irá a casa.",
                "fr": "Elle n'ira pas à la maison."
            }
        },
        {
            "concept": "Question",
            "sentences": {
                "en": "Do you see the cat?",
                "es": "¿Ves el gato?",
                "fr": "Vois-tu le chat?"
            }
        },
        {
            "concept": "Past action",
            "sentences": {
                "en": "He ate the apple.",
                "es": "Él comió la manzana.",
                "fr": "Il a mangé la pomme."
            }
        }
    ]
    
    print("1. Initializing encoders for different languages...")
    encoders = {}
    supported_languages = ["en", "es", "fr"]
    
    for lang in supported_languages:
        try:
            encoder = PTILEncoder.create_for_language(lang)
            encoders[lang] = encoder
            print(f"   ✓ {lang.upper()} encoder initialized")
        except Exception as e:
            print(f"   ✗ Failed to initialize {lang.upper()} encoder: {e}")
            # Use fallback encoder
            try:
                encoders[lang] = PTILEncoder()
                print(f"   ⚠ Using fallback encoder for {lang.upper()}")
            except Exception as fallback_error:
                print(f"   ✗ Fallback encoder failed for {lang.upper()}: {fallback_error}")
                continue
    
    print(f"\n2. Processing cross-lingual test cases...")
    print("=" * 60)
    
    # Initialize cross-lingual validator
    try:
        validator = CrossLingualValidator()
        print("   ✓ Cross-lingual validator initialized")
    except Exception as e:
        print(f"   ✗ Validator initialization failed: {e}")
        validator = None
    
    for case_num, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {case_num}: {test_case['concept']}")
        print("-" * 40)
        
        # Store results for comparison
        results = {}
        
        # Process each language
        for lang, sentence in test_case["sentences"].items():
            if lang not in encoders:
                print(f"   {lang.upper()}: Encoder not available")
                continue
                
            print(f"\n   {lang.upper()}: '{sentence}'")
            
            try:
                # Encode the sentence
                cscs = encoders[lang].encode(sentence)
                
                if cscs:
                    csc = cscs[0]  # Take first CSC
                    results[lang] = csc
                    
                    print(f"     ROOT: {csc.root.value}")
                    print(f"     OPS: {[op.value for op in csc.ops]}")
                    print(f"     ROLES: {[(role.value, entity.text) for role, entity in csc.roles.items()]}")
                    print(f"     META: {csc.meta.value if csc.meta else None}")
                    
                    # Serialized form
                    serialized = encoders[lang].encode_and_serialize(sentence)
                    print(f"     Serialized: {serialized}")
                else:
                    print("     ✗ No CSC generated")
                    
            except Exception as e:
                print(f"     ✗ Error: {e}")
        
        # Compare consistency across languages
        if len(results) >= 2 and validator:
            print(f"\n   Cross-lingual consistency check:")
            
            languages = list(results.keys())
            for i in range(len(languages)):
                for j in range(i + 1, len(languages)):
                    lang1, lang2 = languages[i], languages[j]
                    
                    try:
                        is_consistent = validator.validate_consistency(
                            results[lang1], results[lang2], lang1, lang2
                        )
                        
                        consistency_symbol = "✓" if is_consistent else "✗"
                        print(f"     {consistency_symbol} {lang1.upper()} ↔ {lang2.upper()}: {'Consistent' if is_consistent else 'Inconsistent'}")
                        
                    except Exception as e:
                        print(f"     ⚠ {lang1.upper()} ↔ {lang2.upper()}: Validation error: {e}")
        
        elif len(results) < 2:
            print(f"   ⚠ Insufficient results for consistency check")
    
    print("\n3. Language-independent ROOT usage analysis...")
    print("=" * 60)
    
    # Analyze ROOT distribution across languages
    root_usage = {}
    
    for case_num, test_case in enumerate(test_cases, 1):
        concept = test_case['concept']
        roots_for_concept = set()
        
        for lang, sentence in test_case["sentences"].items():
            if lang not in encoders:
                continue
                
            try:
                cscs = encoders[lang].encode(sentence)
                if cscs:
                    roots_for_concept.add(cscs[0].root.value)
            except Exception:
                continue
        
        root_usage[concept] = roots_for_concept
        
        if len(roots_for_concept) == 1:
            print(f"   ✓ {concept}: Consistent ROOT ({list(roots_for_concept)[0]})")
        elif len(roots_for_concept) > 1:
            print(f"   ✗ {concept}: Inconsistent ROOTs ({', '.join(roots_for_concept)})")
        else:
            print(f"   ⚠ {concept}: No ROOTs extracted")
    
    print("\n4. Summary...")
    print("=" * 60)
    
    total_concepts = len(test_cases)
    consistent_concepts = sum(1 for roots in root_usage.values() if len(roots) == 1)
    
    print(f"   Total concepts tested: {total_concepts}")
    print(f"   Consistent concepts: {consistent_concepts}")
    print(f"   Consistency rate: {consistent_concepts/total_concepts*100:.1f}%")
    
    if consistent_concepts == total_concepts:
        print("   ✓ Perfect cross-lingual consistency achieved!")
    elif consistent_concepts >= total_concepts * 0.8:
        print("   ⚠ Good cross-lingual consistency (some minor variations)")
    else:
        print("   ✗ Cross-lingual consistency needs improvement")
    
    print("\n=== Cross-Lingual Demo Complete ===")


if __name__ == "__main__":
    main()