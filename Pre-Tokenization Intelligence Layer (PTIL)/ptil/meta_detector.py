"""
META Detector component for PTIL semantic encoder.

This module detects speech acts and epistemic markers to capture speech-level
and epistemic information in the META component of CSC structures.
"""

from typing import Optional
from .models import META, LinguisticAnalysis


class METADetector:
    """
    Detects speech acts and epistemic markers for META component generation.
    
    Identifies sentence types (ASSERTIVE, QUESTION, COMMAND) and epistemic
    markers (UNCERTAIN, EVIDENTIAL, EMOTIVE, IRONIC) from linguistic analysis.
    """
    
    def __init__(self):
        """Initialize the META detector with detection rules."""
        # Question markers and patterns
        self.question_words = {
            "what", "who", "when", "where", "why", "how", "which", "whose"
        }
        
        # Command/imperative markers
        self.command_words = {
            "please", "let", "go", "come", "stop", "start", "do", "don't",
            "make", "take", "give", "put", "get", "bring", "send"
        }
        
        # Uncertainty markers
        self.uncertainty_words = {
            "maybe", "perhaps", "possibly", "probably", "might", "could",
            "seem", "appears", "looks", "sounds", "feels", "think", "believe",
            "guess", "suppose", "assume", "wonder", "doubt", "uncertain",
            "unsure", "unclear"
        }
        
        # Evidential markers (indicating source of information)
        self.evidential_words = {
            "apparently", "evidently", "obviously", "clearly", "reportedly",
            "allegedly", "supposedly", "presumably", "according", "heard",
            "seen", "told", "said", "claimed", "stated", "mentioned",
            "indicated", "suggested", "implied"
        }
        
        # Emotive markers
        self.emotive_words = {
            "unfortunately", "sadly", "happily", "luckily", "surprisingly",
            "amazingly", "shockingly", "disappointingly", "thankfully",
            "hopefully", "regrettably", "incredibly", "unbelievably"
        }
        
        # Ironic markers (often contextual, but some explicit indicators)
        self.ironic_words = {
            "yeah", "right", "sure", "obviously", "clearly", "definitely",
            "absolutely", "totally", "really", "seriously"
        }
    
    def detect_meta(self, analysis: LinguisticAnalysis) -> Optional[META]:
        """
        Detects speech acts and epistemic markers from linguistic analysis.
        
        Args:
            analysis: LinguisticAnalysis containing tokens and linguistic features
            
        Returns:
            META enum value if detected, None if no specific META component found
        """
        if not analysis.tokens:
            return None
        
        # Check for sentence types first (primary speech acts)
        sentence_type = self._detect_sentence_type(analysis)
        if sentence_type:
            return sentence_type
        
        # Check for epistemic markers (secondary)
        epistemic_marker = self._detect_epistemic_markers(analysis)
        if epistemic_marker:
            return epistemic_marker
        
        # Default to ASSERTIVE for declarative sentences
        return META.ASSERTIVE
    
    def _detect_sentence_type(self, analysis: LinguisticAnalysis) -> Optional[META]:
        """
        Detect primary sentence types: QUESTION, COMMAND, or ASSERTIVE.
        
        Args:
            analysis: LinguisticAnalysis with tokens and POS tags
            
        Returns:
            META enum for sentence type or None if not clearly determined
        """
        if not analysis.tokens:
            return None
        
        tokens_lower = [token.lower() for token in analysis.tokens]
        
        # Check for questions
        if self._is_question(analysis, tokens_lower):
            return META.QUESTION
        
        # Check for commands/imperatives
        if self._is_command(analysis, tokens_lower):
            return META.COMMAND
        
        # Default case handled by caller
        return None
    
    def _is_question(self, analysis: LinguisticAnalysis, tokens_lower: list) -> bool:
        """
        Determine if the sentence is a question.
        
        Args:
            analysis: LinguisticAnalysis with tokens and POS tags
            tokens_lower: Lowercase tokens for matching
            
        Returns:
            True if sentence is a question
        """
        # Check for question mark
        if "?" in analysis.tokens:
            return True
        
        # Check for WH-questions (what, who, when, etc.)
        for token in tokens_lower:
            if token in self.question_words:
                return True
        
        # Check for yes/no questions (auxiliary verb at beginning)
        if (analysis.pos_tags and 
            analysis.pos_tags[0] == "AUX" and 
            tokens_lower[0] in {"is", "are", "was", "were", "do", "does", "did", 
                               "can", "could", "will", "would", "should", "have", "has", "had"}):
            return True
        
        # Check for tag questions (e.g., "isn't it?", "don't you?")
        if len(tokens_lower) >= 2:
            last_two = " ".join(tokens_lower[-2:])
            tag_patterns = {
                "isn't it", "aren't they", "don't you", "doesn't he", "didn't she",
                "won't you", "wouldn't they", "can't you", "couldn't he", "aren't you",
                "are you", "is it", "do you", "does he", "did she", "will you", "would they"
            }
            if last_two in tag_patterns:
                return True
        
        return False
    
    def _is_command(self, analysis: LinguisticAnalysis, tokens_lower: list) -> bool:
        """
        Determine if the sentence is a command/imperative.
        
        Args:
            analysis: LinguisticAnalysis with tokens and POS tags
            tokens_lower: Lowercase tokens for matching
            
        Returns:
            True if sentence is a command
        """
        if not tokens_lower:
            return False
        
        # Check for imperative markers
        first_token = tokens_lower[0]
        
        # Direct imperative verbs
        if first_token in self.command_words:
            return True
        
        # Check for "please" anywhere in the sentence
        if "please" in tokens_lower:
            return True
        
        # Check for imperative mood based on POS patterns
        # Imperative sentences often start with base form verbs
        if (analysis.pos_tags and 
            analysis.pos_tags[0] == "VERB" and 
            first_token not in {"am", "is", "are", "was", "were"}):
            # Additional check: no explicit subject pronoun at the beginning
            if len(analysis.pos_tags) == 1 or analysis.pos_tags[1] != "PRON":
                return True
        
        # Check for "let's" constructions
        if len(tokens_lower) >= 2 and tokens_lower[0] == "let" and tokens_lower[1] in {"us", "'s"}:
            return True
        
        return False
    
    def _detect_epistemic_markers(self, analysis: LinguisticAnalysis) -> Optional[META]:
        """
        Detect epistemic markers: UNCERTAIN, EVIDENTIAL, EMOTIVE, IRONIC.
        
        Args:
            analysis: LinguisticAnalysis with tokens
            
        Returns:
            META enum for epistemic marker or None if not found
        """
        tokens_lower = [token.lower() for token in analysis.tokens]
        
        # Check for uncertainty markers (highest priority for epistemic)
        for token in tokens_lower:
            if token in self.uncertainty_words:
                return META.UNCERTAIN
        
        # Check for evidential markers
        for token in tokens_lower:
            if token in self.evidential_words:
                return META.EVIDENTIAL
        
        # Check for emotive markers
        for token in tokens_lower:
            if token in self.emotive_words:
                return META.EMOTIVE
        
        # Check for ironic markers (context-dependent, basic detection)
        # Note: True irony detection requires more sophisticated analysis
        for token in tokens_lower:
            if token in self.ironic_words:
                # Simple heuristic: if multiple "obvious" markers, might be ironic
                if tokens_lower.count(token) > 1 or len([t for t in tokens_lower if t in self.ironic_words]) > 1:
                    return META.IRONIC
        
        return None