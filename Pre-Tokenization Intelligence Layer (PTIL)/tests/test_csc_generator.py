"""
Unit tests for PTIL CSC generator component.

Tests specific examples and edge cases for CSC generation functionality.
"""

import pytest
from ptil.models import ROOT, Operator, Role, META, CSC, Entity
from ptil.csc_generator import CSCGenerator


class TestCSCGenerator:
    """Unit tests for CSC generator specific examples and edge cases."""
    
    def setup_method(self):
        """Set up CSC generator for each test."""
        self.generator = CSCGenerator()
    
    def test_basic_csc_generation(self):
        """Test basic CSC generation with all components."""
        root = ROOT.MOTION
        ops = [Operator.FUTURE, Operator.NEGATION]
        roles = {
            Role.AGENT: Entity(text="boy", normalized="BOY"),
            Role.GOAL: Entity(text="school", normalized="SCHOOL")
        }
        meta = META.ASSERTIVE
        
        csc = self.generator.generate_csc(root, ops, roles, meta)
        
        assert csc.root == root
        assert csc.ops == ops
        assert csc.roles == roles
        assert csc.meta == meta
    
    def test_csc_generation_without_meta(self):
        """Test CSC generation without META component."""
        root = ROOT.EXISTENCE
        ops = [Operator.PRESENT]
        roles = {Role.THEME: Entity(text="cat", normalized="CAT")}
        
        csc = self.generator.generate_csc(root, ops, roles)
        
        assert csc.root == root
        assert csc.ops == ops
        assert csc.roles == roles
        assert csc.meta is None
    
    def test_csc_generation_with_empty_ops_and_roles(self):
        """Test CSC generation with empty operators and roles."""
        root = ROOT.EXISTENCE
        ops = []
        roles = {}
        
        csc = self.generator.generate_csc(root, ops, roles)
        
        assert csc.root == root
        assert csc.ops == []
        assert csc.roles == {}
        assert csc.meta is None
    
    def test_validation_errors(self):
        """Test validation errors for invalid CSC generation."""
        # Test None ROOT
        with pytest.raises(ValueError, match="ROOT component is mandatory"):
            self.generator.generate_csc(None, [], {})
    
    def test_multiple_csc_generation(self):
        """Test generation of multiple CSCs."""
        predicates_data = [
            {
                'root': ROOT.MOTION,
                'ops': [Operator.PRESENT],
                'roles': {Role.AGENT: Entity(text="cat", normalized="CAT")},
                'meta': None
            },
            {
                'root': ROOT.COMMUNICATION,
                'ops': [Operator.PAST],
                'roles': {Role.AGENT: Entity(text="dog", normalized="DOG")},
                'meta': META.ASSERTIVE
            }
        ]
        
        csc_list = self.generator.generate_multiple_csc(predicates_data)
        
        assert len(csc_list) == 2
        assert csc_list[0].root == ROOT.MOTION
        assert csc_list[1].root == ROOT.COMMUNICATION
        assert csc_list[1].meta == META.ASSERTIVE
    
    def test_multiple_csc_empty_list_error(self):
        """Test error for empty predicate list."""
        with pytest.raises(ValueError, match="At least one predicate is required"):
            self.generator.generate_multiple_csc([])
    
    def test_csc_completeness_validation(self):
        """Test CSC completeness validation."""
        # Valid CSC
        valid_csc = CSC(
            root=ROOT.MOTION,
            ops=[Operator.PRESENT],
            roles={Role.AGENT: Entity(text="cat", normalized="CAT")},
            meta=None
        )
        assert self.generator.validate_csc_completeness(valid_csc)
        
        # Invalid CSC with None ROOT
        invalid_csc = CSC(root=None, ops=[], roles={}, meta=None)
        assert not self.generator.validate_csc_completeness(invalid_csc)
        
        # Invalid CSC with None OPS
        invalid_csc2 = CSC(root=ROOT.MOTION, ops=None, roles={}, meta=None)
        assert not self.generator.validate_csc_completeness(invalid_csc2)
        
        # Invalid CSC with None ROLES
        invalid_csc3 = CSC(root=ROOT.MOTION, ops=[], roles=None, meta=None)
        assert not self.generator.validate_csc_completeness(invalid_csc3)