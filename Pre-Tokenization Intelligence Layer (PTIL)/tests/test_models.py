"""
Unit tests for PTIL data models.

Tests enum value constraints, dataclass structure, and ROOT-ROLE compatibility matrix.
Requirements: 2.1, 4.4
"""

import pytest
from ptil.models import ROOT, Operator, Role, META, CSC, Entity, LinguisticAnalysis
from ptil.compatibility import ROOT_ROLE_COMPATIBILITY, is_role_compatible, get_compatible_roles


class TestEnums:
    """Test enum value constraints and structure."""
    
    def test_root_enum_values(self):
        """Test ROOT enum contains expected semantic primitives."""
        expected_roots = {
            "MOTION", "TRANSFER", "COMMUNICATION", "COGNITION", "PERCEPTION",
            "CREATION", "DESTRUCTION", "CHANGE", "POSSESSION", "INTENTION", "EXISTENCE"
        }
        actual_roots = {root.value for root in ROOT}
        assert expected_roots.issubset(actual_roots)
        
    def test_operator_enum_categories(self):
        """Test Operator enum contains all required categories."""
        # Temporal operators
        assert Operator.PAST.value == "PAST"
        assert Operator.PRESENT.value == "PRESENT"
        assert Operator.FUTURE.value == "FUTURE"
        
        # Aspect operators
        assert Operator.CONTINUOUS.value == "CONTINUOUS"
        assert Operator.COMPLETED.value == "COMPLETED"
        assert Operator.HABITUAL.value == "HABITUAL"
        
        # Polarity operators
        assert Operator.NEGATION.value == "NEGATION"
        assert Operator.AFFIRMATION.value == "AFFIRMATION"
        
        # Modality operators
        assert Operator.POSSIBLE.value == "POSSIBLE"
        assert Operator.NECESSARY.value == "NECESSARY"
        
    def test_role_enum_values(self):
        """Test Role enum contains core semantic roles."""
        expected_roles = {
            "AGENT", "PATIENT", "THEME", "GOAL", "SOURCE", 
            "INSTRUMENT", "LOCATION", "TIME"
        }
        actual_roles = {role.value for role in Role}
        assert expected_roles == actual_roles
        
    def test_meta_enum_values(self):
        """Test META enum contains speech act and epistemic markers."""
        expected_meta = {
            "ASSERTIVE", "QUESTION", "COMMAND", "UNCERTAIN", 
            "EVIDENTIAL", "EMOTIVE", "IRONIC"
        }
        actual_meta = {meta.value for meta in META}
        assert expected_meta == actual_meta


class TestDataclasses:
    """Test dataclass structure and validation."""
    
    def test_entity_structure(self):
        """Test Entity dataclass structure."""
        entity = Entity(text="the boy", normalized="BOY")
        assert entity.text == "the boy"
        assert entity.normalized == "BOY"
        
    def test_linguistic_analysis_structure(self):
        """Test LinguisticAnalysis dataclass structure."""
        analysis = LinguisticAnalysis(
            tokens=["the", "boy", "runs"],
            pos_tags=["DET", "NOUN", "VERB"],
            dependencies=[(2, "det", 0), (2, "nsubj", 1)],
            negation_markers=[],
            tense_markers={"present": [2]},
            aspect_markers={}
        )
        assert len(analysis.tokens) == 3
        assert len(analysis.pos_tags) == 3
        assert len(analysis.dependencies) == 2
        assert analysis.negation_markers == []
        
    def test_csc_structure_mandatory_components(self):
        """Test CSC dataclass with mandatory components."""
        entity = Entity(text="boy", normalized="BOY")
        csc = CSC(
            root=ROOT.MOTION,
            ops=[Operator.PRESENT],
            roles={Role.AGENT: entity}
        )
        assert csc.root == ROOT.MOTION
        assert csc.ops == [Operator.PRESENT]
        assert csc.roles[Role.AGENT] == entity
        assert csc.meta is None
        
    def test_csc_structure_with_meta(self):
        """Test CSC dataclass with optional META component."""
        entity = Entity(text="boy", normalized="BOY")
        csc = CSC(
            root=ROOT.MOTION,
            ops=[Operator.PRESENT],
            roles={Role.AGENT: entity},
            meta=META.ASSERTIVE
        )
        assert csc.meta == META.ASSERTIVE


class TestROOTRoleCompatibility:
    """Test ROOT-ROLE compatibility matrix lookups."""
    
    def test_compatibility_matrix_structure(self):
        """Test that compatibility matrix contains all ROOT types."""
        for root in ROOT:
            assert root in ROOT_ROLE_COMPATIBILITY
            assert isinstance(ROOT_ROLE_COMPATIBILITY[root], set)
            
    def test_motion_root_compatibility(self):
        """Test MOTION ROOT has expected compatible roles."""
        motion_roles = ROOT_ROLE_COMPATIBILITY[ROOT.MOTION]
        expected_roles = {Role.AGENT, Role.THEME, Role.SOURCE, Role.GOAL, Role.LOCATION, Role.TIME, Role.INSTRUMENT}
        assert expected_roles.issubset(motion_roles)
        
    def test_communication_root_compatibility(self):
        """Test COMMUNICATION ROOT has expected compatible roles."""
        comm_roles = ROOT_ROLE_COMPATIBILITY[ROOT.COMMUNICATION]
        expected_roles = {Role.AGENT, Role.PATIENT, Role.THEME, Role.INSTRUMENT, Role.TIME, Role.LOCATION}
        assert expected_roles.issubset(comm_roles)
        
    def test_is_role_compatible_function(self):
        """Test is_role_compatible function."""
        # Test valid compatibility
        assert is_role_compatible(ROOT.MOTION, Role.AGENT) is True
        assert is_role_compatible(ROOT.COMMUNICATION, Role.PATIENT) is True
        
        # Test invalid compatibility (PATIENT not typically compatible with MOTION)
        assert is_role_compatible(ROOT.MOTION, Role.PATIENT) is False
        
    def test_get_compatible_roles_function(self):
        """Test get_compatible_roles function."""
        motion_roles = get_compatible_roles(ROOT.MOTION)
        assert Role.AGENT in motion_roles
        assert Role.THEME in motion_roles
        assert Role.SOURCE in motion_roles
        
        # Test that returned set is a copy (modification doesn't affect original)
        original_size = len(ROOT_ROLE_COMPATIBILITY[ROOT.MOTION])
        motion_roles.add(Role.PATIENT)  # Add incompatible role to copy
        assert len(ROOT_ROLE_COMPATIBILITY[ROOT.MOTION]) == original_size
        
    def test_existence_root_minimal_roles(self):
        """Test EXISTENCE ROOT has minimal role set."""
        existence_roles = ROOT_ROLE_COMPATIBILITY[ROOT.EXISTENCE]
        # EXISTENCE typically only needs THEME, LOCATION, TIME
        assert Role.THEME in existence_roles
        assert Role.LOCATION in existence_roles
        assert Role.TIME in existence_roles
        # Should not have AGENT (nothing acts in pure existence)
        assert Role.AGENT not in existence_roles