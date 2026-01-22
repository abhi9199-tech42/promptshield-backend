
import unittest
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ptil import PTILEncoder

class TestPTILCSE(unittest.TestCase):
    def setUp(self):
        self.encoder = PTILEncoder()

    def test_cse_simple_repetition(self):
        # "hello world hello world" -> "hello world"
        # "hello world" is a bigram.
        text = "hello world hello world"
        # CSE runs on words.
        # "hello world hello world" -> "hello world"
        result = self.encoder.apply_cse(text).strip()
        self.assertEqual(result, "hello world")

    def test_cse_trigram_repetition(self):
        # "one two three one two three" -> "one two three"
        text = "one two three one two three"
        result = self.encoder.apply_cse(text).strip()
        self.assertEqual(result, "one two three")

    def test_pipeline_integration(self):
        # "Create a python script. The python script should be fast."
        # Normalization: "mk py script. the py script should be fast."
        # CSE: "py script" repeats.
        # "mk py script. the should be fast." (py script removed)
        # Stopwords: "mk py script. fast."
        
        text = "Create a python script. The python script should be fast."
        compressed, confidence = self.encoder.encode_and_serialize(text)
        print(f"Original: {text}")
        print(f"Compressed: {compressed}")
        
        # Expect "mk py script" at start
        self.assertTrue(compressed.startswith("mk py script"))
        # Expect second "py script" to be gone
        # "mk py script. fast."
        self.assertNotIn("py script py script", compressed)
        
    def test_cse_with_stopwords(self):
        # "I want to go to the store. I want to go to the park."
        # "I want to" repeats.
        text = "I want to go to the store. I want to go to the park."
        # Normalized: "I want to go to the store. I want to go to the park." (assuming no normalization for these)
        # CSE: "I want to" removed second time.
        # "I want to go to the store. go to the park."
        # Stopwords removes "I", "want", "to", "the"...
        # Remaining: "store. park."
        
        compressed, confidence = self.encoder.encode_and_serialize(text)
        print(f"Original: {text}")
        print(f"Compressed: {compressed}")
        
        self.assertIn("store", compressed)
        self.assertIn("park", compressed)

if __name__ == '__main__':
    unittest.main()
