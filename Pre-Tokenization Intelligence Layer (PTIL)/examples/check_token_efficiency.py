
import sys
import os
import statistics

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ptil import PTILEncoder, TokenizerCompatibilityValidator, TokenizerType

def check_token_efficiency():
    encoder = PTILEncoder()
    validator = TokenizerCompatibilityValidator()
    
    # Categorized test set
    test_cases = [
        {"text": "The quick brown fox jumps over the lazy dog.", "class": "Declarative (long)"},
        {"text": "I will not be going to the party tomorrow because I am tired.", "class": "Conversational"},
        {"text": "Scientific research demonstrates that semantic encoding significantly reduces data redundancy.", "class": "Scientific"},
        {"text": "The expansion of the universe is accelerating due to dark energy.", "class": "Scientific"},
        {"text": "Go!", "class": "Command"},
        {"text": "Did you see the beautiful sunset yesterday evening?", "class": "Conversational"},
        {"text": "If it rains, we will stay inside and watch a movie.", "class": "Declarative (long)"}
    ]
    
    print(f"{'TEXT CLASS':<20} | {'RAW':<4} | {'VERB':<4} | {'COMP':<4} | {'V-RED':<7} | {'C-RED':<7} | {'STATUS'}")
    print("-" * 80)
    
    class_results = {}
    
    for case in test_cases:
        text = case["text"]
        cls = case["class"]
        
        raw_tokens = validator._simulate_tokenization(text, TokenizerType.BPE)
        raw_count = len(raw_tokens)
        
        cscs = encoder.encode(text)
        
        # Test Verbose
        ser_verbose = encoder.csc_serializer.serialize_multiple(cscs)
        tok_verbose = validator._simulate_tokenization(ser_verbose, TokenizerType.BPE)
        cnt_verbose = len(tok_verbose)
        
        # Test Compact
        ser_compact = encoder.compact_serializer.serialize_multiple(cscs)
        tok_compact = validator._simulate_tokenization(ser_compact, TokenizerType.BPE)
        cnt_compact = len(tok_compact)
        
        red_v = (1 - (cnt_verbose / raw_count)) * 100 if raw_count > 0 else 0
        red_c = (1 - (cnt_compact / raw_count)) * 100 if raw_count > 0 else 0
        
        status = "INCLUDED" if raw_count >= 5 else "EXCLUDED (Overhead)"
        
        if status == "INCLUDED":
            if cls not in class_results:
                class_results[cls] = []
            class_results[cls].append(red_c)
        
        print(f"{cls:<20} | {raw_count:<4} | {cnt_verbose:<4} | {cnt_compact:<4} | {red_v:<6.1f}% | {red_c:<6.1f}% | {status}")

    print("-" * 80)
    print("OBSERVED EFFICIENCY (Compact Format):")
    for cls, reds in class_results.items():
        avg = statistics.mean(reds)
        print(f" • {cls:<18}: {avg:.1f}%")
    
    print("\nNote: Short utterances excluded due to encoding overhead dominance.")
    print("PTIL is optimized for semantic-dense text; overhead is expected for n < 5 tokens.")



if __name__ == "__main__":
    check_token_efficiency()
