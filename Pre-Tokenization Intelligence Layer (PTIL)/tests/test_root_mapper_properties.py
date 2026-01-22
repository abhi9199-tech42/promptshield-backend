"""
Property-based tests for PTIL ROOT mapper component.

Tests universal properties that should hold across all inputs for ROOT mapping functionality.
Uses Hypothesis for comprehensive property testing.
"""

import pytest
from hypothesis import given, strategies as st, assume
from ptil.models import ROOT
from ptil.root_mapper import ROOTMapper


class TestROOTMapperProperties:
    """Property-based tests for ROOT mapper universality and consistency."""
    
    def setup_method(self):
        """Set up ROOT mapper for each test."""
        self.mapper = ROOTMapper()
    
    @given(
        predicate=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu")), min_size=1, max_size=20),
        pos_tag=st.sampled_from(["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "NN", "NNS", "NNP", "NNPS", "JJ", "RB"])
    )
    def test_root_assignment_universality(self, predicate, pos_tag):
        """
        Property 2: ROOT Assignment Universality
        For any sentence, the system should map it to at least one ROOT from the finite semantic primitive set.
        
        **Feature: ptil-semantic-encoder, Property 2: ROOT Assignment Universality**
        **Validates: Requirements 1.2, 2.3**
        """
        # Create minimal dependency context
        dependency_context = {"relations": []}
        
        # Map predicate to ROOT
        result_root = self.mapper.map_predicate(predicate, pos_tag, dependency_context)
        
        # Verify that a ROOT is always assigned
        assert result_root is not None
        assert isinstance(result_root, ROOT)
        
        # Verify the ROOT is from the finite semantic primitive set
        assert result_root in ROOT
    
    @given(
        predicate=st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu")), min_size=1, max_size=20),
        pos_tag=st.sampled_from(["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "NN", "NNS"])
    )
    def test_root_set_constraint(self, predicate, pos_tag):
        """
        Property 3: ROOT Set Constraint
        For any generated ROOT, it should be a member of the predefined finite set of semantic primitives.
        
        **Feature: ptil-semantic-encoder, Property 3: ROOT Set Constraint**
        **Validates: Requirements 1.4**
        """
        dependency_context = {"relations": []}
        
        result_root = self.mapper.map_predicate(predicate, pos_tag, dependency_context)
        
        # Verify ROOT is from predefined finite set
        assert result_root in ROOT
        
        # Verify ROOT is one of the expected semantic primitives
        expected_roots = {
            ROOT.MOTION, ROOT.TRANSFER, ROOT.COMMUNICATION, ROOT.COGNITION,
            ROOT.PERCEPTION, ROOT.CREATION, ROOT.DESTRUCTION, ROOT.CHANGE,
            ROOT.POSSESSION, ROOT.INTENTION, ROOT.EXISTENCE
        }
        assert result_root in expected_roots
    
    @given(
        equivalent_predicates=st.lists(
            st.sampled_from(["go", "walk", "travel", "move"]),  # Known equivalent predicates
            min_size=2, max_size=4, unique=True
        ),
        pos_tag=st.sampled_from(["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"])
    )
    def test_predicate_consistency(self, equivalent_predicates, pos_tag):
        """
        Property 5: Predicate Consistency
        For any set of semantically equivalent predicates, they should map to the same ROOT.
        
        **Feature: ptil-semantic-encoder, Property 5: Predicate Consistency**
        **Validates: Requirements 2.2**
        """
        dependency_context = {"relations": []}
        
        # Map all equivalent predicates
        mapped_roots = []
        for predicate in equivalent_predicates:
            root = self.mapper.map_predicate(predicate, pos_tag, dependency_context)
            mapped_roots.append(root)
        
        # Verify all equivalent predicates map to the same ROOT
        assert len(set(mapped_roots)) == 1, f"Equivalent predicates {equivalent_predicates} mapped to different ROOTs: {mapped_roots}"
        
        # Verify they all map to MOTION (since these are motion predicates)
        assert all(root == ROOT.MOTION for root in mapped_roots)