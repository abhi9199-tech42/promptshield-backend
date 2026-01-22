"""
Property-based tests for PTIL CSC generator component.

Tests universal properties that should hold across all inputs for CSC generation functionality.
Uses Hypothesis for comprehensive property testing.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from ptil.models import ROOT, Operator, Role, META, CSC, Entity
from ptil.csc_generator import CSCGenerator


class TestCSCGeneratorProperties:
    """Property-based tests for CSC generator universality and consistency."""
    
    def setup_method(self):
        """Set up CSC generator for each test."""
        self.generator = CSCGenerator()
    
    @given(
        root=st.sampled_from(list(ROOT)),
        ops=st.lists(st.sampled_from(list(Operator)), max_size=5),
        roles=st.dictionaries(
            keys=st.sampled_from(list(Role)),
            values=st.builds(Entity, 
                text=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                normalized=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
            ),
            max_size=5
        ),
        meta=st.one_of(st.none(), st.sampled_from(list(META)))
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_csc_structure_completeness(self, root, ops, roles, meta):
        """
        Property 1: CSC Structure Completeness
        For any input text, the generated CSC should contain mandatory ROOT, OPS, and ROLES components,
        with META being optional.
        
        **Feature: ptil-semantic-encoder, Property 1: CSC Structure Completeness**
        **Validates: Requirements 1.1**
        """
        try:
            # Generate CSC
            csc = self.generator.generate_csc(root, ops, roles, meta)
            
            # Verify CSC structure completeness
            assert csc is not None, "CSC should not be None"
            assert isinstance(csc, CSC), "Generated object should be a CSC instance"
            
            # Verify mandatory components are present
            assert csc.root is not None, "ROOT component is mandatory"
            assert csc.ops is not None, "OPS component is mandatory (can be empty list)"
            assert csc.roles is not None, "ROLES component is mandatory (can be empty dict)"
            
            # Verify component types
            assert isinstance(csc.root, ROOT), "ROOT should be a ROOT enum"
            assert isinstance(csc.ops, list), "OPS should be a list"
            assert isinstance(csc.roles, dict), "ROLES should be a dictionary"
            
            # Verify operators are valid
            for op in csc.ops:
                assert isinstance(op, Operator), f"All operators should be Operator enums, got {type(op)}"
            
            # Verify roles are valid
            for role, entity in csc.roles.items():
                assert isinstance(role, Role), f"All role keys should be Role enums, got {type(role)}"
                assert isinstance(entity, Entity), f"All role values should be Entity objects, got {type(entity)}"
            
            # Verify META is optional and correct type when present
            if csc.meta is not None:
                assert isinstance(csc.meta, META), "META should be a META enum when present"
            
            # Verify CSC completeness validation
            assert self.generator.validate_csc_completeness(csc), "CSC should pass completeness validation"
            
        except ValueError as e:
            # If role compatibility fails, that's expected for some combinations
            if "not compatible with ROOT" in str(e):
                # This is expected behavior for incompatible role-root combinations
                pass
            else:
                # Re-raise unexpected errors
                raise
    
    @given(
        predicates_data=st.lists(
            st.fixed_dictionaries({
                'root': st.sampled_from(list(ROOT)),
                'ops': st.lists(st.sampled_from(list(Operator)), max_size=3),
                'roles': st.dictionaries(
                    keys=st.sampled_from(list(Role)),
                    values=st.builds(Entity, 
                        text=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
                        normalized=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
                    ),
                    max_size=3
                ),
                'meta': st.one_of(st.none(), st.sampled_from(list(META)))
            }),
            min_size=2, max_size=4
        )
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_multiple_predicate_handling(self, predicates_data):
        """
        Property 6: Multiple Predicate Handling
        For any sentence containing multiple predicates, the system should generate multiple CSC instances as needed.
        
        **Feature: ptil-semantic-encoder, Property 6: Multiple Predicate Handling**
        **Validates: Requirements 2.5**
        """
        try:
            # Generate multiple CSCs
            csc_list = self.generator.generate_multiple_csc(predicates_data)
            
            # Verify multiple CSCs are generated
            assert csc_list is not None, "CSC list should not be None"
            assert isinstance(csc_list, list), "Result should be a list"
            assert len(csc_list) == len(predicates_data), "Should generate one CSC per predicate"
            assert len(csc_list) >= 2, "Should handle multiple predicates (at least 2)"
            
            # Verify each CSC in the list
            for i, csc in enumerate(csc_list):
                assert isinstance(csc, CSC), f"Each item should be a CSC instance, got {type(csc)} at index {i}"
                
                # Verify structure completeness for each CSC
                assert csc.root is not None, f"ROOT is mandatory for CSC {i}"
                assert csc.ops is not None, f"OPS is mandatory for CSC {i}"
                assert csc.roles is not None, f"ROLES is mandatory for CSC {i}"
                
                # Verify CSC completeness
                assert self.generator.validate_csc_completeness(csc), f"CSC {i} should pass completeness validation"
            
            # Verify that different predicates can produce different CSCs
            if len(set(csc.root for csc in csc_list)) > 1:
                # If we have different roots, verify they're handled correctly
                roots = [csc.root for csc in csc_list]
                assert len(roots) == len(csc_list), "Each CSC should have a root"
            
        except ValueError as e:
            # If role compatibility fails, that's expected for some combinations
            if "not compatible with ROOT" in str(e):
                # This is expected behavior for incompatible role-root combinations
                pass
            else:
                # Re-raise unexpected errors
                raise