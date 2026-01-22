"""
Unit tests for PTIL OPS extractor component.

Tests specific examples and edge cases for operator extraction functionality.
"""

import pytest
from ptil.models import Operator, LinguisticAnalysis
from ptil.ops_extractor import OPSExtractor


class TestOPSExtractor:
    """Unit tests for OPS extractor specific examples and edge cases."""
    
    def setup_method(self):
        """Set up OPS extractor for each test."""
        self.extractor = OPSExtractor()
    
    def test_empty_analysis(self):
        """Test that empty analysis returns empty operator list."""
        analysis = LinguisticAnalysis(
            tokens=[],
            pos_tags=[],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert operators == []
    
    def test_temporal_operator_extraction(self):
        """Test extraction of temporal operators from tense markers."""
        analysis = LinguisticAnalysis(
            tokens=["will", "go"],
            pos_tags=["AUX", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={"future": [0]},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.FUTURE in operators
    
    def test_negation_operator_extraction(self):
        """Test extraction of negation operators."""
        analysis = LinguisticAnalysis(
            tokens=["do", "not", "go"],
            pos_tags=["AUX", "PART", "VERB"],
            dependencies=[],
            negation_markers=[1],
            tense_markers={},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.NEGATION in operators
    
    def test_aspect_operator_extraction(self):
        """Test extraction of aspect operators."""
        analysis = LinguisticAnalysis(
            tokens=["is", "running"],
            pos_tags=["AUX", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={"continuous": [0]}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.CONTINUOUS in operators
    
    def test_modality_operator_extraction(self):
        """Test extraction of modality operators from keywords."""
        analysis = LinguisticAnalysis(
            tokens=["can", "go"],
            pos_tags=["AUX", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.POSSIBLE in operators
    
    def test_causation_operator_extraction(self):
        """Test extraction of causation operators."""
        analysis = LinguisticAnalysis(
            tokens=["make", "him", "go"],
            pos_tags=["VERB", "PRON", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.CAUSATIVE in operators
    
    def test_direction_operator_extraction(self):
        """Test extraction of direction operators."""
        analysis = LinguisticAnalysis(
            tokens=["go", "into", "house"],
            pos_tags=["VERB", "ADP", "NOUN"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.DIRECTION_IN in operators
    
    def test_multiple_operators_ordering(self):
        """Test that multiple operators maintain proper ordering."""
        analysis = LinguisticAnalysis(
            tokens=["will", "not", "be", "going"],
            pos_tags=["AUX", "PART", "AUX", "VERB"],
            dependencies=[],
            negation_markers=[1],
            tense_markers={"future": [0]},
            aspect_markers={"continuous": [2]}
        )
        
        operators = self.extractor.extract_operators(analysis)
        
        # Check that all expected operators are present
        assert Operator.FUTURE in operators
        assert Operator.CONTINUOUS in operators
        assert Operator.NEGATION in operators
        
        # Check ordering: temporal, aspect, negation
        future_idx = operators.index(Operator.FUTURE)
        continuous_idx = operators.index(Operator.CONTINUOUS)
        negation_idx = operators.index(Operator.NEGATION)
        
        assert future_idx < continuous_idx < negation_idx
    
    def test_duplicate_operator_removal(self):
        """Test that duplicate operators are removed while preserving order."""
        analysis = LinguisticAnalysis(
            tokens=["will", "will", "go"],
            pos_tags=["AUX", "AUX", "VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={"future": [0, 1]},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        
        # Should only have one FUTURE operator despite multiple markers
        future_count = operators.count(Operator.FUTURE)
        assert future_count == 1
    
    def test_default_present_tense(self):
        """Test that PRESENT tense is default when no tense markers found."""
        analysis = LinguisticAnalysis(
            tokens=["go"],
            pos_tags=["VERB"],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        
        operators = self.extractor.extract_operators(analysis)
        assert Operator.PRESENT in operators