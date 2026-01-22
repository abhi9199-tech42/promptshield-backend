"""
Unit tests for PTIL META detector component.

Tests specific examples and edge cases for META detection functionality.
"""

import pytest
from ptil.models import META, LinguisticAnalysis
from ptil.meta_detector import METADetector


class TestMETADetector:
    """Unit tests for META detector specific examples and edge cases."""
    
    def setup_method(self):
        """Set up META detector for each test."""
        self.detector = METADetector()
    
    def test_empty_analysis(self):
        """Test that empty analysis returns None."""
        analysis = LinguisticAnalysis(
            tokens=[],
            pos_tags=[],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta is None
    
    def test_assertive_sentence_detection(self):
        """Test detection of assertive/declarative sentences."""
        analysis = LinguisticAnalysis(
            tokens=["The", "boy", "runs"],
            pos_tags=["DET", "NOUN", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.ASSERTIVE
    
    def test_question_with_question_mark(self):
        """Test detection of questions with question mark."""
        analysis = LinguisticAnalysis(
            tokens=["Where", "is", "he", "?"],
            pos_tags=["ADV", "AUX", "PRON", "PUNCT"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.QUESTION
    
    def test_wh_question_detection(self):
        """Test detection of WH-questions."""
        wh_words = ["what", "who", "when", "where", "why", "how", "which", "whose"]
        
        for wh_word in wh_words:
            analysis = LinguisticAnalysis(
                tokens=[wh_word.capitalize(), "is", "that"],
                pos_tags=["PRON", "AUX", "PRON"],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
            
            meta = self.detector.detect_meta(analysis)
            assert meta == META.QUESTION, f"Failed to detect question for WH-word: {wh_word}"
    
    def test_yes_no_question_detection(self):
        """Test detection of yes/no questions with auxiliary verbs."""
        aux_verbs = ["is", "are", "was", "were", "do", "does", "did", "can", "could", "will", "would", "should"]
        
        for aux in aux_verbs:
            analysis = LinguisticAnalysis(
                tokens=[aux.capitalize(), "you", "coming"],
                pos_tags=["AUX", "PRON", "VERB"],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
            
            meta = self.detector.detect_meta(analysis)
            assert meta == META.QUESTION, f"Failed to detect question for auxiliary: {aux}"
    
    def test_tag_question_detection(self):
        """Test detection of tag questions."""
        analysis = LinguisticAnalysis(
            tokens=["You", "are", "coming", ",", "aren't", "you"],
            pos_tags=["PRON", "AUX", "VERB", "PUNCT", "AUX", "PRON"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.QUESTION
    
    def test_imperative_command_detection(self):
        """Test detection of imperative commands."""
        command_words = ["go", "come", "stop", "start", "make", "take", "give", "put"]
        
        for command in command_words:
            analysis = LinguisticAnalysis(
                tokens=[command.capitalize(), "there"],
                pos_tags=["VERB", "ADV"],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
            
            meta = self.detector.detect_meta(analysis)
            assert meta == META.COMMAND, f"Failed to detect command for verb: {command}"
    
    def test_please_command_detection(self):
        """Test detection of commands with 'please'."""
        analysis = LinguisticAnalysis(
            tokens=["Please", "sit", "down"],
            pos_tags=["INTJ", "VERB", "PART"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.COMMAND
    
    def test_lets_command_detection(self):
        """Test detection of 'let's' commands."""
        analysis = LinguisticAnalysis(
            tokens=["Let", "'s", "go"],
            pos_tags=["VERB", "PART", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.COMMAND
    
    def test_uncertain_marker_detection(self):
        """Test detection of uncertainty markers."""
        uncertainty_words = ["maybe", "perhaps", "possibly", "probably", "might", "could", "think", "believe"]
        
        for word in uncertainty_words:
            analysis = LinguisticAnalysis(
                tokens=["I", word, "he", "will", "come"],
                pos_tags=["PRON", "ADV", "PRON", "AUX", "VERB"],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
            
            meta = self.detector.detect_meta(analysis)
            assert meta == META.UNCERTAIN, f"Failed to detect uncertainty for word: {word}"
    
    def test_evidential_marker_detection(self):
        """Test detection of evidential markers."""
        evidential_words = ["apparently", "evidently", "obviously", "reportedly", "allegedly", "supposedly"]
        
        for word in evidential_words:
            analysis = LinguisticAnalysis(
                tokens=[word.capitalize(), "he", "left"],
                pos_tags=["ADV", "PRON", "VERB"],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
            
            meta = self.detector.detect_meta(analysis)
            assert meta == META.EVIDENTIAL, f"Failed to detect evidential for word: {word}"
    
    def test_emotive_marker_detection(self):
        """Test detection of emotive markers."""
        emotive_words = ["unfortunately", "sadly", "happily", "luckily", "surprisingly", "thankfully"]
        
        for word in emotive_words:
            analysis = LinguisticAnalysis(
                tokens=[word.capitalize(), "he", "arrived"],
                pos_tags=["ADV", "PRON", "VERB"],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
            
            meta = self.detector.detect_meta(analysis)
            assert meta == META.EMOTIVE, f"Failed to detect emotive for word: {word}"
    
    def test_ironic_marker_detection(self):
        """Test detection of ironic markers (basic heuristic)."""
        # Test multiple ironic markers (simple heuristic)
        analysis = LinguisticAnalysis(
            tokens=["Yeah", "right", "that", "is", "totally", "obvious"],
            pos_tags=["INTJ", "ADV", "PRON", "AUX", "ADV", "ADJ"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.IRONIC
    
    def test_priority_order_question_over_uncertain(self):
        """Test that question detection takes priority over uncertainty."""
        analysis = LinguisticAnalysis(
            tokens=["Do", "you", "think", "he", "will", "come", "?"],
            pos_tags=["AUX", "PRON", "VERB", "PRON", "AUX", "VERB", "PUNCT"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.QUESTION  # Should be QUESTION, not UNCERTAIN despite "think"
    
    def test_priority_order_command_over_emotive(self):
        """Test that command detection takes priority over emotive."""
        analysis = LinguisticAnalysis(
            tokens=["Please", "sadly", "go", "away"],
            pos_tags=["INTJ", "ADV", "VERB", "ADV"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.COMMAND  # Should be COMMAND, not EMOTIVE despite "sadly"
    
    def test_epistemic_priority_uncertain_over_evidential(self):
        """Test that uncertainty takes priority over evidential markers."""
        analysis = LinguisticAnalysis(
            tokens=["I", "think", "apparently", "he", "left"],
            pos_tags=["PRON", "VERB", "ADV", "PRON", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        assert meta == META.UNCERTAIN  # Should be UNCERTAIN, not EVIDENTIAL
    
    def test_complex_sentence_with_multiple_markers(self):
        """Test complex sentence with multiple potential META markers."""
        analysis = LinguisticAnalysis(
            tokens=["I", "think", "unfortunately", "he", "probably", "left"],
            pos_tags=["PRON", "VERB", "ADV", "PRON", "ADV", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        # Should detect UNCERTAIN (from "think" and "probably") as highest priority epistemic
        assert meta == META.UNCERTAIN
    
    def test_optional_meta_handling(self):
        """Test that META component is optional and can be None."""
        # Simple declarative sentence with no special markers
        analysis = LinguisticAnalysis(
            tokens=["The", "cat", "sleeps"],
            pos_tags=["DET", "NOUN", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        meta = self.detector.detect_meta(analysis)
        # Should default to ASSERTIVE for simple declarative sentences
        assert meta == META.ASSERTIVE