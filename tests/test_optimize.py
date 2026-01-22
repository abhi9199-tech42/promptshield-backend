import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm import analyze_prompt, OptimizationResult

def test_analyze_prompt():
    raw_text = "Please act as a helpful assistant. The meeting was conducted by the team."
    
    # Run analysis
    result = analyze_prompt(raw_text, model="gpt-4o-mini")
    
    print("--- Analysis Result ---")
    print(f"Raw Text: {result.raw_text}")
    print(f"Compressed Text: {result.compressed_text}")
    print(f"Suggestions: {result.suggestions}")
    print(f"Token Savings: {result.tokens.savings} tokens")
    
    # Check if suggestions contain expected items
    has_passive = any("passive voice" in s for s in result.suggestions)
    has_politeness = any("politeness markers" in s for s in result.suggestions)
    has_act_as = any("Act as" in s for s in result.suggestions)
    
    print(f"Detected Passive Voice: {has_passive}")
    print(f"Detected Politeness: {has_politeness}")
    print(f"Detected Act As: {has_act_as}")
    
    if has_passive and has_politeness and has_act_as:
        print("SUCCESS: All heuristics triggered correctly.")
    else:
        print("FAILURE: Some heuristics missed.")

if __name__ == "__main__":
    test_analyze_prompt()
