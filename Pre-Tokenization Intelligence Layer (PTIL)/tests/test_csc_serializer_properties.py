"""
Property-based tests for PTIL CSC serializer component.

Tests universal properties that should hold across all inputs for CSC serialization functionality.
Uses Hypothesis for comprehensive property testing.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from ptil.models import ROOT, Operator, Role, META, CSC, Entity
from ptil.csc_serializer import CSCSerializer


class TestCSCSerializerProperties:
    """Property-based tests for CSC serializer universality and consistency."""
    
    def setup_method(self):
        """Set up CSC serializer for each test."""
        self.serializer = CSCSerializer()
    
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
    def test_serialization_format_validation(self, root, ops, roles, meta):
        """
        Property 17: Serialization Format Validation
        For any CSC, the serialized output should be symbolic text format (not JSON) 
        with components ordered as ROOT → OPS → ROLES → META.
        
        **Feature: ptil-semantic-encoder, Property 17: Serialization Format Validation**
        **Validates: Requirements 6.1, 6.2**
        """
        # Create CSC
        csc = CSC(root=root, ops=ops, roles=roles, meta=meta)
        
        # Serialize CSC
        serialized = self.serializer.serialize(csc)
        
        # Verify serialization format validation
        assert self.serializer.validate_serialization_format(serialized), "Serialized output should pass format validation"
        
        # Verify it's symbolic text format, not JSON
        assert not serialized.strip().startswith("{"), "Output should not be JSON format"
        assert not serialized.strip().startswith("["), "Output should not be JSON array format"
        assert "<" in serialized and ">" in serialized, "Output should use symbolic angle bracket format"
        
        # Verify required components are present
        assert "<ROOT=" in serialized, "ROOT component should be present"
        assert "<OPS=" in serialized, "OPS component should be present (even if empty)"
        
        # Verify component ordering: ROOT → OPS → ROLES → META
        components_order = self.serializer.extract_components_order(serialized)
        
        # ROOT should be first
        assert components_order[0] == "ROOT", f"ROOT should be first component, got {components_order}"
        
        # OPS should be second
        assert components_order[1] == "OPS", f"OPS should be second component, got {components_order}"
        
        # If roles are present, they should come after OPS
        role_components = [comp for comp in components_order if comp in [role.value for role in Role]]
        if role_components:
            ops_index = components_order.index("OPS")
            first_role_index = components_order.index(role_components[0])
            assert first_role_index > ops_index, "ROLES should come after OPS"
        
        # If META is present, it should be last
        if meta is not None:
            assert "META" in components_order, "META should be in components when present"
            meta_index = components_order.index("META")
            assert meta_index == len(components_order) - 1, "META should be the last component"
        
        # Verify flat, tokenizer-compatible format
        # Should not contain nested structures
        assert "{" not in serialized, "Should not contain nested JSON-like structures"
        assert "[" not in serialized, "Should not contain array-like structures"
        
        # Should be space-separated components
        components = serialized.split()
        assert len(components) >= 2, "Should have at least ROOT and OPS components"
        
        # Each component should be in <TAG=VALUE> format
        for component in components:
            assert component.startswith("<") and component.endswith(">"), f"Component {component} should be in <TAG=VALUE> format"
            assert "=" in component, f"Component {component} should contain = separator"
    
    @given(
        csc_list=st.lists(
            st.builds(CSC,
                root=st.sampled_from(list(ROOT)),
                ops=st.lists(st.sampled_from(list(Operator)), max_size=3),
                roles=st.dictionaries(
                    keys=st.sampled_from(list(Role)),
                    values=st.builds(Entity, 
                        text=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
                        normalized=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
                    ),
                    max_size=3
                ),
                meta=st.one_of(st.none(), st.sampled_from(list(META)))
            ),
            min_size=1, max_size=3
        )
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_multiple_csc_serialization_format(self, csc_list):
        """
        Test serialization format for multiple CSCs.
        Verifies that multiple CSCs maintain proper format when serialized together.
        """
        # Serialize multiple CSCs
        serialized = self.serializer.serialize_multiple(csc_list)
        
        if not csc_list:
            assert serialized == "", "Empty CSC list should produce empty string"
            return
        
        # Verify overall format
        assert self.serializer.validate_serialization_format(serialized), "Multiple CSC serialization should pass format validation"
        
        # Verify each CSC maintains proper format
        # Split by ROOT components to identify individual CSCs
        root_positions = []
        components = serialized.split()
        for i, component in enumerate(components):
            if component.startswith("<ROOT="):
                root_positions.append(i)
        
        assert len(root_positions) == len(csc_list), "Should have one ROOT per CSC"
        
        # Verify each CSC section maintains proper ordering
        for i, root_pos in enumerate(root_positions):
            # Find the end of this CSC (start of next CSC or end of string)
            end_pos = root_positions[i + 1] if i + 1 < len(root_positions) else len(components)
            csc_components = components[root_pos:end_pos]
            
            # Extract component order for this CSC
            csc_serialized = " ".join(csc_components)
            csc_order = self.serializer.extract_components_order(csc_serialized)
            
            # Verify ordering for this CSC
            assert csc_order[0] == "ROOT", f"CSC {i}: ROOT should be first"
            assert csc_order[1] == "OPS", f"CSC {i}: OPS should be second"