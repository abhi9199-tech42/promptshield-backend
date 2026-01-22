"""
Unit tests for PTIL CSC serializer component.

Tests specific examples and edge cases for CSC serialization functionality.
"""

import pytest
from ptil.models import ROOT, Operator, Role, META, CSC, Entity
from ptil.csc_serializer import CSCSerializer


class TestCSCSerializer:
    """Unit tests for CSC serializer specific examples and edge cases."""
    
    def setup_method(self):
        """Set up CSC serializer for each test."""
        self.serializer = CSCSerializer()
    
    def test_specific_serialization_example(self):
        """
        Test "The boy will not go to school tomorrow" serialization.
        
        Expected output: "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <TIME=TOMORROW> <META=ASSERTIVE>"
        
        **Validates: Requirements 6.4**
        """
        # Create entities
        boy_entity = Entity(text="the boy", normalized="BOY")
        school_entity = Entity(text="to school", normalized="SCHOOL")
        tomorrow_entity = Entity(text="tomorrow", normalized="TOMORROW")
        
        # Create CSC for "The boy will not go to school tomorrow"
        csc = CSC(
            root=ROOT.MOTION,
            ops=[Operator.FUTURE, Operator.NEGATION],
            roles={
                Role.AGENT: boy_entity,
                Role.GOAL: school_entity,
                Role.TIME: tomorrow_entity
            },
            meta=META.ASSERTIVE
        )
        
        # Serialize
        serialized = self.serializer.serialize(csc)
        
        # Verify expected format
        expected = "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <TIME=TOMORROW> <META=ASSERTIVE>"
        assert serialized == expected, f"Expected: {expected}, Got: {serialized}"
    
    def test_empty_ops_serialization(self):
        """Test serialization with empty operators list."""
        csc = CSC(
            root=ROOT.EXISTENCE,
            ops=[],
            roles={Role.THEME: Entity(text="cat", normalized="CAT")},
            meta=None
        )
        
        serialized = self.serializer.serialize(csc)
        expected = "<ROOT=EXISTENCE> <OPS=> <THEME=CAT>"
        assert serialized == expected
    
    def test_empty_roles_serialization(self):
        """Test serialization with empty roles dictionary."""
        csc = CSC(
            root=ROOT.EXISTENCE,
            ops=[Operator.PRESENT],
            roles={},
            meta=META.ASSERTIVE
        )
        
        serialized = self.serializer.serialize(csc)
        expected = "<ROOT=EXISTENCE> <OPS=PRESENT> <META=ASSERTIVE>"
        assert serialized == expected
    
    def test_no_meta_serialization(self):
        """Test serialization without META component."""
        csc = CSC(
            root=ROOT.COMMUNICATION,
            ops=[Operator.PAST],
            roles={Role.AGENT: Entity(text="she", normalized="SHE")},
            meta=None
        )
        
        serialized = self.serializer.serialize(csc)
        expected = "<ROOT=COMMUNICATION> <OPS=PAST> <AGENT=SHE>"
        assert serialized == expected
    
    def test_multiple_operators_serialization(self):
        """Test serialization with multiple operators."""
        csc = CSC(
            root=ROOT.MOTION,
            ops=[Operator.PAST, Operator.CONTINUOUS, Operator.NEGATION],
            roles={Role.AGENT: Entity(text="runner", normalized="RUNNER")},
            meta=None
        )
        
        serialized = self.serializer.serialize(csc)
        expected = "<ROOT=MOTION> <OPS=PAST|CONTINUOUS|NEGATION> <AGENT=RUNNER>"
        assert serialized == expected
    
    def test_multiple_roles_serialization(self):
        """Test serialization with multiple roles (sorted order)."""
        csc = CSC(
            root=ROOT.TRANSFER,
            ops=[Operator.PRESENT],
            roles={
                Role.THEME: Entity(text="book", normalized="BOOK"),
                Role.AGENT: Entity(text="teacher", normalized="TEACHER"),
                Role.GOAL: Entity(text="student", normalized="STUDENT")
            },
            meta=None
        )
        
        serialized = self.serializer.serialize(csc)
        # Roles should be sorted alphabetically: AGENT, GOAL, THEME
        expected = "<ROOT=TRANSFER> <OPS=PRESENT> <AGENT=TEACHER> <GOAL=STUDENT> <THEME=BOOK>"
        assert serialized == expected
    
    def test_serialize_multiple_cscs(self):
        """Test serialization of multiple CSC structures."""
        csc1 = CSC(
            root=ROOT.MOTION,
            ops=[Operator.PRESENT],
            roles={Role.AGENT: Entity(text="cat", normalized="CAT")},
            meta=None
        )
        
        csc2 = CSC(
            root=ROOT.COMMUNICATION,
            ops=[Operator.PAST],
            roles={Role.AGENT: Entity(text="dog", normalized="DOG")},
            meta=META.ASSERTIVE
        )
        
        serialized = self.serializer.serialize_multiple([csc1, csc2])
        expected = "<ROOT=MOTION> <OPS=PRESENT> <AGENT=CAT> <ROOT=COMMUNICATION> <OPS=PAST> <AGENT=DOG> <META=ASSERTIVE>"
        assert serialized == expected
    
    def test_serialize_empty_list(self):
        """Test serialization of empty CSC list."""
        serialized = self.serializer.serialize_multiple([])
        assert serialized == ""
    
    def test_validation_errors(self):
        """Test serialization validation errors."""
        # Test None CSC
        with pytest.raises(ValueError, match="CSC cannot be None"):
            self.serializer.serialize(None)
        
        # Test CSC with None ROOT
        csc = CSC(root=None, ops=[], roles={}, meta=None)
        with pytest.raises(ValueError, match="ROOT component is mandatory"):
            self.serializer.serialize(csc)
    
    def test_format_validation(self):
        """Test serialization format validation."""
        # Valid format
        valid_serialized = "<ROOT=MOTION> <OPS=PRESENT> <AGENT=CAT>"
        assert self.serializer.validate_serialization_format(valid_serialized)
        
        # Invalid formats
        assert not self.serializer.validate_serialization_format("")
        assert not self.serializer.validate_serialization_format("plain text")
        assert not self.serializer.validate_serialization_format('{"root": "MOTION"}')  # JSON
        assert not self.serializer.validate_serialization_format("<OPS=PRESENT>")  # Missing ROOT
    
    def test_component_order_extraction(self):
        """Test extraction of component order from serialized CSC."""
        serialized = "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <META=ASSERTIVE>"
        order = self.serializer.extract_components_order(serialized)
        expected_order = ["ROOT", "OPS", "AGENT", "GOAL", "META"]
        assert order == expected_order