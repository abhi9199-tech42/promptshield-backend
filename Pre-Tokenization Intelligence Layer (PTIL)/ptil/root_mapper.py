"""
ROOT mapper component for PTIL semantic encoder.

This module provides the ROOTMapper class that maps surface predicates to semantic ROOT primitives
using a comprehensive predicate dictionary and disambiguation based on POS tags and dependency context.
"""

from typing import Dict, List, Set, Optional, Tuple
from .models import ROOT, LinguisticAnalysis


class ROOTMapper:
    """
    Maps surface predicates to semantic ROOT primitives.
    
    Uses a comprehensive predicate dictionary with disambiguation based on POS tags
    and dependency context. Handles unknown predicates with fallback to generic ROOTs.
    """
    
    def __init__(self):
        """Initialize the ROOT mapper with predicate dictionary."""
        self._predicate_dict = self._build_predicate_dictionary()
        self._fallback_root = ROOT.EXISTENCE
    
    def map_predicate(self, predicate: str, pos_context: str, 
                     dependency_context: Dict) -> ROOT:
        """
        Map a surface predicate to a semantic ROOT primitive.
        
        Args:
            predicate: The surface form predicate to map
            pos_context: POS tag of the predicate for disambiguation
            dependency_context: Dependency parsing context for disambiguation
            
        Returns:
            ROOT primitive corresponding to the predicate
        """
        # Normalize predicate to lowercase for lookup
        normalized_predicate = predicate.lower().strip()
        
        # Direct lookup in predicate dictionary
        if normalized_predicate in self._predicate_dict:
            candidates = self._predicate_dict[normalized_predicate]
            
            # If only one candidate, return it
            if len(candidates) == 1:
                return list(candidates)[0]
            
            # Disambiguate using POS and dependency context
            return self._disambiguate(candidates, pos_context, dependency_context)
        
        # Handle unknown predicates with fallback
        return self._handle_unknown_predicate(normalized_predicate, pos_context)
    
    def _build_predicate_dictionary(self) -> Dict[str, Set[ROOT]]:
        """
        Build comprehensive predicate dictionary mapping surface forms to ROOTs.
        
        Returns:
            Dictionary mapping predicates to sets of possible ROOTs
        """
        predicate_dict = {
            # MOTION predicates
            "go": {ROOT.MOTION},
            "come": {ROOT.MOTION},
            "walk": {ROOT.MOTION},
            "run": {ROOT.MOTION},
            "travel": {ROOT.MOTION},
            "move": {ROOT.MOTION},
            "drive": {ROOT.MOTION},
            "fly": {ROOT.MOTION},
            "swim": {ROOT.MOTION},
            "jump": {ROOT.MOTION},
            "climb": {ROOT.MOTION},
            "fall": {ROOT.MOTION},
            "rise": {ROOT.MOTION},
            "descend": {ROOT.MOTION},
            "approach": {ROOT.MOTION},
            "depart": {ROOT.MOTION},
            "arrive": {ROOT.MOTION},
            "leave": {ROOT.MOTION},
            "enter": {ROOT.MOTION},
            "exit": {ROOT.MOTION},
            "return": {ROOT.MOTION},  # Added for cross-lingual consistency
            "jog": {ROOT.MOTION},    # Added for cross-lingual consistency
            "sprint": {ROOT.MOTION}, # Added for cross-lingual consistency
            "dash": {ROOT.MOTION},   # Added for cross-lingual consistency
            "hurry": {ROOT.MOTION},  # Added for cross-lingual consistency
            "rush": {ROOT.MOTION},   # Added for cross-lingual consistency
            
            # TRANSFER predicates
            "give": {ROOT.TRANSFER},
            "take": {ROOT.TRANSFER},
            "send": {ROOT.TRANSFER},
            "receive": {ROOT.TRANSFER},
            "deliver": {ROOT.TRANSFER},
            "hand": {ROOT.TRANSFER},
            "pass": {ROOT.TRANSFER},
            "provide": {ROOT.TRANSFER},
            "supply": {ROOT.TRANSFER},
            "offer": {ROOT.TRANSFER},
            "donate": {ROOT.TRANSFER},
            "lend": {ROOT.TRANSFER},
            "borrow": {ROOT.TRANSFER},
            "steal": {ROOT.TRANSFER},
            "rob": {ROOT.TRANSFER},
            
            # COMMUNICATION predicates
            "say": {ROOT.COMMUNICATION},
            "tell": {ROOT.COMMUNICATION},
            "speak": {ROOT.COMMUNICATION},
            "talk": {ROOT.COMMUNICATION},
            "communicate": {ROOT.COMMUNICATION},
            "discuss": {ROOT.COMMUNICATION},
            "explain": {ROOT.COMMUNICATION},
            "describe": {ROOT.COMMUNICATION},
            "announce": {ROOT.COMMUNICATION},
            "declare": {ROOT.COMMUNICATION},
            "whisper": {ROOT.COMMUNICATION},
            "shout": {ROOT.COMMUNICATION},
            "ask": {ROOT.COMMUNICATION},
            "answer": {ROOT.COMMUNICATION},
            "reply": {ROOT.COMMUNICATION},
            "respond": {ROOT.COMMUNICATION},
            "argue": {ROOT.COMMUNICATION},
            "debate": {ROOT.COMMUNICATION},
            
            # COGNITION predicates
            "think": {ROOT.COGNITION},
            "know": {ROOT.COGNITION},
            "understand": {ROOT.COGNITION},
            "realize": {ROOT.COGNITION},
            "remember": {ROOT.COGNITION},
            "forget": {ROOT.COGNITION},
            "learn": {ROOT.COGNITION},
            "study": {ROOT.COGNITION},
            "consider": {ROOT.COGNITION},
            "believe": {ROOT.COGNITION},
            "doubt": {ROOT.COGNITION},
            "wonder": {ROOT.COGNITION},
            "imagine": {ROOT.COGNITION},
            "dream": {ROOT.COGNITION},
            "plan": {ROOT.COGNITION},
            "decide": {ROOT.COGNITION},
            "choose": {ROOT.COGNITION},
            
            # PERCEPTION predicates
            "see": {ROOT.PERCEPTION},
            "look": {ROOT.PERCEPTION},
            "watch": {ROOT.PERCEPTION},
            "observe": {ROOT.PERCEPTION},
            "notice": {ROOT.PERCEPTION},
            "hear": {ROOT.PERCEPTION},
            "listen": {ROOT.PERCEPTION},
            "feel": {ROOT.PERCEPTION},
            "touch": {ROOT.PERCEPTION},
            "taste": {ROOT.PERCEPTION},
            "smell": {ROOT.PERCEPTION},
            "sense": {ROOT.PERCEPTION},
            "detect": {ROOT.PERCEPTION},
            "discover": {ROOT.PERCEPTION},
            "find": {ROOT.PERCEPTION},
            
            # CREATION predicates
            "make": {ROOT.CREATION},
            "create": {ROOT.CREATION},
            "build": {ROOT.CREATION},
            "construct": {ROOT.CREATION},
            "produce": {ROOT.CREATION},
            "manufacture": {ROOT.CREATION},
            "generate": {ROOT.CREATION},
            "develop": {ROOT.CREATION},
            "design": {ROOT.CREATION},
            "invent": {ROOT.CREATION},
            "compose": {ROOT.CREATION},
            "write": {ROOT.CREATION},
            "draw": {ROOT.CREATION},
            "paint": {ROOT.CREATION},
            "sculpt": {ROOT.CREATION},
            "craft": {ROOT.CREATION},
            "form": {ROOT.CREATION},
            "shape": {ROOT.CREATION},
            
            # DESTRUCTION predicates
            "destroy": {ROOT.DESTRUCTION},
            "break": {ROOT.DESTRUCTION},
            "damage": {ROOT.DESTRUCTION},
            "ruin": {ROOT.DESTRUCTION},
            "demolish": {ROOT.DESTRUCTION},
            "wreck": {ROOT.DESTRUCTION},
            "smash": {ROOT.DESTRUCTION},
            "crush": {ROOT.DESTRUCTION},
            "tear": {ROOT.DESTRUCTION},
            "cut": {ROOT.DESTRUCTION},
            "burn": {ROOT.DESTRUCTION},
            "melt": {ROOT.DESTRUCTION},
            "dissolve": {ROOT.DESTRUCTION},
            "erase": {ROOT.DESTRUCTION},
            "delete": {ROOT.DESTRUCTION},
            "remove": {ROOT.DESTRUCTION},
            "eliminate": {ROOT.DESTRUCTION},
            
            # CHANGE predicates
            "change": {ROOT.CHANGE},
            "transform": {ROOT.CHANGE},
            "convert": {ROOT.CHANGE},
            "alter": {ROOT.CHANGE},
            "modify": {ROOT.CHANGE},
            "adjust": {ROOT.CHANGE},
            "adapt": {ROOT.CHANGE},
            "evolve": {ROOT.CHANGE},
            "develop": {ROOT.CHANGE, ROOT.CREATION},  # Ambiguous
            "grow": {ROOT.CHANGE},
            "shrink": {ROOT.CHANGE},
            "expand": {ROOT.CHANGE},
            "contract": {ROOT.CHANGE},
            "improve": {ROOT.CHANGE},
            "worsen": {ROOT.CHANGE},
            "become": {ROOT.CHANGE},
            "turn": {ROOT.CHANGE},
            
            # POSSESSION predicates
            "have": {ROOT.POSSESSION},
            "own": {ROOT.POSSESSION},
            "possess": {ROOT.POSSESSION},
            "hold": {ROOT.POSSESSION},
            "keep": {ROOT.POSSESSION},
            "retain": {ROOT.POSSESSION},
            "acquire": {ROOT.POSSESSION},
            "obtain": {ROOT.POSSESSION},
            "gain": {ROOT.POSSESSION},
            "lose": {ROOT.POSSESSION},
            "lack": {ROOT.POSSESSION},
            "need": {ROOT.POSSESSION},
            "want": {ROOT.POSSESSION},
            "require": {ROOT.POSSESSION},
            
            # INTENTION predicates
            "intend": {ROOT.INTENTION},
            "plan": {ROOT.INTENTION, ROOT.COGNITION},  # Ambiguous
            "aim": {ROOT.INTENTION},
            "hope": {ROOT.INTENTION},
            "wish": {ROOT.INTENTION},
            "desire": {ROOT.INTENTION},
            "want": {ROOT.INTENTION, ROOT.POSSESSION},  # Ambiguous
            "try": {ROOT.INTENTION},
            "attempt": {ROOT.INTENTION},
            "strive": {ROOT.INTENTION},
            "seek": {ROOT.INTENTION},
            "pursue": {ROOT.INTENTION},
            
            # EXISTENCE predicates
            "be": {ROOT.EXISTENCE},
            "exist": {ROOT.EXISTENCE},
            "live": {ROOT.EXISTENCE},
            "die": {ROOT.EXISTENCE},
            "survive": {ROOT.EXISTENCE},
            "remain": {ROOT.EXISTENCE},
            "stay": {ROOT.EXISTENCE},
            "continue": {ROOT.EXISTENCE},
            "persist": {ROOT.EXISTENCE},
            "endure": {ROOT.EXISTENCE},
            "last": {ROOT.EXISTENCE},
            "occur": {ROOT.EXISTENCE},
            "happen": {ROOT.EXISTENCE},
            "take place": {ROOT.EXISTENCE},
        }
        
        return predicate_dict
    
    def _disambiguate(self, candidates: Set[ROOT], pos_context: str, 
                     dependency_context: Dict) -> ROOT:
        """
        Disambiguate between multiple ROOT candidates using context.
        
        Args:
            candidates: Set of possible ROOT candidates
            pos_context: POS tag for disambiguation
            dependency_context: Dependency information for disambiguation
            
        Returns:
            Most appropriate ROOT based on context
        """
        # If no disambiguation possible, return first candidate
        if not candidates:
            return self._fallback_root
        
        # Simple POS-based disambiguation rules
        if pos_context in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            # For verbs, prefer action-oriented ROOTs
            action_roots = {ROOT.MOTION, ROOT.TRANSFER, ROOT.COMMUNICATION, 
                          ROOT.CREATION, ROOT.DESTRUCTION, ROOT.CHANGE}
            action_candidates = candidates.intersection(action_roots)
            if action_candidates:
                return next(iter(action_candidates))
        
        elif pos_context in ["NN", "NNS", "NNP", "NNPS"]:
            # For nouns used as predicates, prefer state-oriented ROOTs
            state_roots = {ROOT.EXISTENCE, ROOT.POSSESSION, ROOT.COGNITION}
            state_candidates = candidates.intersection(state_roots)
            if state_candidates:
                return next(iter(state_candidates))
        
        # Check dependency context for additional clues
        if dependency_context:
            # If there's a direct object, prefer transitive ROOTs
            if "dobj" in dependency_context.get("relations", []):
                transitive_roots = {ROOT.TRANSFER, ROOT.CREATION, ROOT.DESTRUCTION, 
                                  ROOT.PERCEPTION, ROOT.COMMUNICATION}
                transitive_candidates = candidates.intersection(transitive_roots)
                if transitive_candidates:
                    return next(iter(transitive_candidates))
        
        # Default: return first candidate
        return next(iter(candidates))
    
    def _handle_unknown_predicate(self, predicate: str, pos_context: str) -> ROOT:
        """
        Handle unknown predicates with fallback to generic ROOTs.
        
        Args:
            predicate: Unknown predicate
            pos_context: POS tag for fallback selection
            
        Returns:
            Appropriate fallback ROOT
        """
        # POS-based fallback selection
        if pos_context in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            # For unknown verbs, default to CHANGE (most general action)
            return ROOT.CHANGE
        elif pos_context in ["NN", "NNS", "NNP", "NNPS"]:
            # For unknown nouns used as predicates, default to EXISTENCE
            return ROOT.EXISTENCE
        else:
            # General fallback
            return self._fallback_root
    
    def get_all_predicates_for_root(self, root: ROOT) -> List[str]:
        """
        Get all predicates that map to a specific ROOT.
        
        Args:
            root: The ROOT to find predicates for
            
        Returns:
            List of predicates that map to the given ROOT
        """
        predicates = []
        for predicate, roots in self._predicate_dict.items():
            if root in roots:
                predicates.append(predicate)
        return sorted(predicates)
    
    def is_predicate_known(self, predicate: str) -> bool:
        """
        Check if a predicate is in the known dictionary.
        
        Args:
            predicate: Predicate to check
            
        Returns:
            True if predicate is known, False otherwise
        """
        return predicate.lower().strip() in self._predicate_dict