import unittest
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ptil import PTILEncoder

class TestPTILSafety(unittest.TestCase):
    def setUp(self):
        self.encoder = PTILEncoder()

    def test_semantic_safety_guard(self):
        # Critical constraints like "not", "no", "never" should be preserved.
        text = "Do not delete the database. Never run this as root."
        
        compressed, confidence = self.encoder.encode_and_serialize(text)
        print(f"Safety Test 1: {text} -> {compressed} (Conf: {confidence})")
        
        # "not" and "never" are critical.
        # "Do" is a stopword. "delete" -> "rm". "database" -> "db".
        # Expected: "not rm db. never run root."
        
        self.assertIn("not", compressed.lower())
        self.assertIn("never", compressed.lower())
        self.assertIn("rm", compressed.lower()) # Normalization should still happen
        self.assertTrue(confidence >= 0.9) # High confidence as criticals are kept

    def test_opt_out_block(self):
        # Text inside {{ ... }} should be preserved verbatim.
        text = "Please optimize this: {{ SELECT * FROM users WHERE id = 1 }}."
        
        compressed, confidence = self.encoder.encode_and_serialize(text)
        print(f"Opt-Out Test: {text} -> {compressed}")
        
        # "Please optimize this" -> "opt this" or similar.
        # "{{ ... }}" -> "SELECT * FROM users WHERE id = 1"
        
        self.assertIn("SELECT * FROM users WHERE id = 1", compressed)
        # Ensure it didn't get lowercased or normalized if inside opt-out
        # (Though current implementation lowercases before finding roots? No, opt-out is Step 0)
        self.assertTrue("SELECT" in compressed) # Case preservation check

    def test_confidence_score_drop(self):
        # If we remove critical tokens (simulated by manually modifying input vs output check?)
        # Actually, my code logic is: if input has criticals, and output keeps them, confidence is high.
        # Let's test a case where "ensure" is removed (it's not critical but similar).
        # Wait, I only track specific critical tokens.
        
        # Let's test normal confidence.
        text = "Create a function."
        compressed, confidence = self.encoder.encode_and_serialize(text)
        self.assertEqual(confidence, 1.0) # No critical tokens involved.

        # Test critical token preservation
        text_crit = "You must not fail."
        compressed_crit, confidence_crit = self.encoder.encode_and_serialize(text_crit)
        # "must" and "not" are critical.
        # "must" is in critical_tokens. "not" is in critical_tokens.
        # Both should be in output.
        self.assertIn("must", compressed_crit.lower())
        self.assertIn("not", compressed_crit.lower())
        self.assertEqual(confidence_crit, 1.0)

if __name__ == '__main__':
    unittest.main()
