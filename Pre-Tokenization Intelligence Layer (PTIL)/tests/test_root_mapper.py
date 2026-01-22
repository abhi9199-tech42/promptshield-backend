"""
Unit tests for PTIL ROOT mapper component.

Tests disambiguation scenarios and fallback behavior for unknown predicates.
Requirements: 5.4
"""

import pytest
from ptil.models import ROOT
from ptil.root_mapper import ROOTMapper


class TestROOTMapper:
    """Unit tests for ROOT mapper functionality."""
    
    def setup_method(self):
        """Set up ROOT mapper for each test."""
        self.mapper = ROOTMapper()
    
    def test_known_predicate_mapping(self):
        """Test mapping of known predicates to correct ROOTs."""
        # Test motion predicates
        assert self.mapper.map_predicate("go", "VB", {}) == ROOT.MOTION
        assert self.mapper.map_predicate("walk", "VB", {}) == ROOT.MOTION
        assert self.mapper.map_predicate("travel", "VB", {}) == ROOT.MOTION
        
        # Test communication predicates
        assert self.mapper.map_predicate("say", "VB", {}) == ROOT.COMMUNICATION
        assert self.mapper.map_predicate("tell", "VB", {}) == ROOT.COMMUNICATION
        
        # Test creation predicates
        assert self.mapper.map_predicate("make", "VB", {}) == ROOT.CREATION
        assert self.mapper.map_predicate("create", "VB", {}) == ROOT.CREATION
    
    def test_ambiguous_predicate_disambiguation(self):
        """Test disambiguation of ambiguous predicates using POS context."""
        # "develop" can be CREATION or CHANGE
        # With verb POS, should prefer action-oriented ROOT (CREATION)
        result = self.mapper.map_predicate("develop", "VB", {})
        assert result in {ROOT.CREATION, ROOT.CHANGE}
        
        # "plan" can be COGNITION or INTENTION
        # With verb POS, should prefer action-oriented ROOT
        result = self.mapper.map_predicate("plan", "VB", {})
        assert result in {ROOT.COGNITION, ROOT.INTENTION}
        
        # "want" can be INTENTION or POSSESSION
        result = self.mapper.map_predicate("want", "VB", {})
        assert result in {ROOT.INTENTION, ROOT.POSSESSION}
    
    def test_pos_based_disambiguation(self):
        """Test POS tag-based disambiguation."""
        # Verb context should prefer action-oriented ROOTs
        verb_result = self.mapper.map_predicate("develop", "VB", {})
        assert verb_result in {ROOT.CREATION, ROOT.CHANGE}
        
        # Noun context should prefer state-oriented ROOTs for predicative use
        noun_result = self.mapper.map_predicate("existence", "NN", {})
        # For unknown noun predicates, should fall back to EXISTENCE
        assert noun_result == ROOT.EXISTENCE
    
    def test_dependency_context_disambiguation(self):
        """Test disambiguation using dependency context."""
        # Predicate with direct object should prefer transitive ROOTs
        transitive_context = {"relations": ["dobj"]}
        result = self.mapper.map_predicate("develop", "VB", transitive_context)
        # Should prefer CREATION over CHANGE when there's a direct object
        assert result in {ROOT.CREATION, ROOT.CHANGE}
        
        # Predicate without direct object
        intransitive_context = {"relations": ["nsubj"]}
        result = self.mapper.map_predicate("develop", "VB", intransitive_context)
        assert result in {ROOT.CREATION, ROOT.CHANGE}
    
    def test_unknown_predicate_fallback(self):
        """Test fallback behavior for unknown predicates."""
        # Unknown verb should fall back to CHANGE (most general action)
        unknown_verb = self.mapper.map_predicate("flibbertigibbet", "VB", {})
        assert unknown_verb == ROOT.CHANGE
        
        # Unknown noun should fall back to EXISTENCE
        unknown_noun = self.mapper.map_predicate("whatsit", "NN", {})
        assert unknown_noun == ROOT.EXISTENCE
        
        # Unknown adjective should fall back to general fallback
        unknown_adj = self.mapper.map_predicate("bizzarre", "JJ", {})
        assert unknown_adj == ROOT.EXISTENCE
    
    def test_case_insensitive_mapping(self):
        """Test that predicate mapping is case-insensitive."""
        assert self.mapper.map_predicate("GO", "VB", {}) == ROOT.MOTION
        assert self.mapper.map_predicate("Go", "VB", {}) == ROOT.MOTION
        assert self.mapper.map_predicate("gO", "VB", {}) == ROOT.MOTION
        assert self.mapper.map_predicate("go", "VB", {}) == ROOT.MOTION
    
    def test_whitespace_handling(self):
        """Test that predicates with whitespace are handled correctly."""
        assert self.mapper.map_predicate("  go  ", "VB", {}) == ROOT.MOTION
        assert self.mapper.map_predicate("\trun\n", "VB", {}) == ROOT.MOTION
    
    def test_get_all_predicates_for_root(self):
        """Test retrieval of all predicates for a specific ROOT."""
        motion_predicates = self.mapper.get_all_predicates_for_root(ROOT.MOTION)
        assert "go" in motion_predicates
        assert "walk" in motion_predicates
        assert "travel" in motion_predicates
        assert "run" in motion_predicates
        
        # Should be sorted
        assert motion_predicates == sorted(motion_predicates)
        
        communication_predicates = self.mapper.get_all_predicates_for_root(ROOT.COMMUNICATION)
        assert "say" in communication_predicates
        assert "tell" in communication_predicates
        assert "speak" in communication_predicates
    
    def test_is_predicate_known(self):
        """Test checking if predicates are in the known dictionary."""
        # Known predicates
        assert self.mapper.is_predicate_known("go") is True
        assert self.mapper.is_predicate_known("say") is True
        assert self.mapper.is_predicate_known("make") is True
        
        # Unknown predicates
        assert self.mapper.is_predicate_known("flibbertigibbet") is False
        assert self.mapper.is_predicate_known("nonexistent") is False
        
        # Case insensitive
        assert self.mapper.is_predicate_known("GO") is True
        assert self.mapper.is_predicate_known("Say") is True
    
    def test_consistent_disambiguation(self):
        """Test that disambiguation is consistent across multiple calls."""
        # Same input should always produce same output
        predicate = "develop"
        pos_tag = "VB"
        context = {"relations": ["dobj"]}
        
        results = []
        for _ in range(10):
            result = self.mapper.map_predicate(predicate, pos_tag, context)
            results.append(result)
        
        # All results should be identical
        assert len(set(results)) == 1
    
    def test_empty_dependency_context(self):
        """Test handling of empty dependency context."""
        # Should not crash with empty context
        result = self.mapper.map_predicate("go", "VB", {})
        assert result == ROOT.MOTION
        
        # Should not crash with None values in context
        result = self.mapper.map_predicate("go", "VB", {"relations": None})
        assert result == ROOT.MOTION