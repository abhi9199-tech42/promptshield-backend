"""
Property-based tests for ROLESBinder component.

These tests validate universal properties of semantic role assignment
using Hypothesis for comprehensive input coverage.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck
from ptil import ROLESBinder, LinguisticAnalyzer, ROOT, Role, Entity
from ptil.compatibility import get_compatible_roles


class TestROLESBinderProperties:
    """Property-based tests for ROLESBinder component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LinguisticAnalyzer()
        self.binder = ROLESBinder()
    
    @given(
        subject=st.sampled_from(["boy", "girl", "man", "woman", "cat", "dog", "bird", "person"]),
        verb=st.sampled_from(["runs", "walks", "goes", "moves", "travels", "flies"]),
        root=st.sampled_from([ROOT.MOTION, ROOT.TRANSFER, ROOT.COMMUNICATION])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_subject_agent_binding_property(self, subject, verb, root):
        """
        Property 11: Subject-Agent Binding
        For any sentence with an agentive subject, the subject should be bound 
        to the AGENT role where semantically appropriate.
        
        **Feature: ptil-semantic-encoder, Property 11: Subject-Agent Binding**
        **Validates: Requirements 4.1**
        """
        # Skip if AGENT role is not compatible with this ROOT
        compatible_roles = get_compatible_roles(root)
        assume(Role.AGENT in compatible_roles)
        
        # Create a simple agentive sentence
        sentence = f"The {subject} {verb}"
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        assume(len(analysis.tokens) >= 2)  # Ensure we have subject and verb
        
        # Bind roles
        roles = self.binder.bind_roles(analysis, root)
        
        # Property: If AGENT role is compatible and we have a subject,
        # the subject should be bound to AGENT role
        if Role.AGENT in compatible_roles:
            assert Role.AGENT in roles, f"AGENT role should be assigned for agentive sentence: '{sentence}'"
            
            # The bound entity should contain the subject
            agent_entity = roles[Role.AGENT]
            assert isinstance(agent_entity, Entity)
            assert subject.lower() in agent_entity.text.lower(), \
                f"Subject '{subject}' should be in agent entity text '{agent_entity.text}'"
    
    @given(
        subject=st.sampled_from(["boy", "girl", "man", "woman", "person"]),
        verb=st.sampled_from(["sees", "hears", "knows", "thinks", "believes"]),
        obj=st.sampled_from(["cat", "dog", "book", "tree", "house"]),
        root=st.sampled_from([ROOT.PERCEPTION, ROOT.COGNITION])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_object_role_binding_property(self, subject, verb, obj, root):
        """
        Property 12: Object Role Binding
        For any sentence with direct objects, they should be bound to PATIENT 
        or THEME roles based on ROOT requirements.
        
        **Feature: ptil-semantic-encoder, Property 12: Object Role Binding**
        **Validates: Requirements 4.2**
        """
        compatible_roles = get_compatible_roles(root)
        
        # Create a sentence with subject, verb, and object
        sentence = f"The {subject} {verb} the {obj}"
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        assume(len(analysis.tokens) >= 4)  # Ensure we have all components
        
        # Bind roles
        roles = self.binder.bind_roles(analysis, root)
        
        # Property: If we have an object and compatible object roles exist,
        # the object should be bound to PATIENT or THEME
        object_roles = {Role.PATIENT, Role.THEME} & compatible_roles
        if object_roles:
            # At least one object role should be assigned
            assigned_object_roles = set(roles.keys()) & object_roles
            assert len(assigned_object_roles) > 0, \
                f"Object should be bound to PATIENT or THEME role in: '{sentence}'"
            
            # The bound entity should contain the object
            for role in assigned_object_roles:
                entity = roles[role]
                assert isinstance(entity, Entity)
                assert obj.lower() in entity.text.lower(), \
                    f"Object '{obj}' should be in {role.value} entity text '{entity.text}'"
    
    @given(
        subject=st.sampled_from(["boy", "girl", "man", "woman", "person"]),
        verb=st.sampled_from(["goes", "moves", "travels", "walks"]),
        prep=st.sampled_from(["to", "from", "at", "in"]),
        location=st.sampled_from(["school", "home", "park", "store", "office"]),
        root=st.sampled_from([ROOT.MOTION])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_prepositional_role_binding_property(self, subject, verb, prep, location, root):
        """
        Property 13: Prepositional Role Binding
        For any sentence with prepositional phrases, they should be bound to 
        appropriate semantic roles (GOAL, SOURCE, LOCATION).
        
        **Feature: ptil-semantic-encoder, Property 13: Prepositional Role Binding**
        **Validates: Requirements 4.3**
        """
        compatible_roles = get_compatible_roles(root)
        
        # Create a sentence with prepositional phrase
        sentence = f"The {subject} {verb} {prep} the {location}"
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        assume(len(analysis.tokens) >= 5)  # Ensure we have all components
        
        # Bind roles
        roles = self.binder.bind_roles(analysis, root)
        
        # Property: Prepositional phrases should be bound to appropriate roles
        # Map prepositions to expected roles
        prep_role_map = {
            "to": Role.GOAL,
            "from": Role.SOURCE,
            "at": Role.LOCATION,
            "in": Role.LOCATION
        }
        
        expected_role = prep_role_map.get(prep)
        if expected_role and expected_role in compatible_roles:
            assert expected_role in roles, \
                f"Prepositional phrase '{prep} the {location}' should be bound to {expected_role.value} role"
            
            # The bound entity should contain the location
            entity = roles[expected_role]
            assert isinstance(entity, Entity)
            assert location.lower() in entity.text.lower(), \
                f"Location '{location}' should be in {expected_role.value} entity text '{entity.text}'"
    
    @given(
        root=st.sampled_from(list(ROOT)),
        words=st.lists(
            st.sampled_from(["boy", "girl", "runs", "walks", "sees", "book", "home", "quickly"]),
            min_size=2, max_size=5
        )
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow], deadline=None)
    def test_root_role_compatibility_property(self, root, words):
        """
        Property 14: ROOT-ROLE Compatibility
        For any CSC, all assigned ROLES should be compatible with the 
        identified ROOT according to the compatibility matrix.
        
        **Feature: ptil-semantic-encoder, Property 14: ROOT-ROLE Compatibility**
        **Validates: Requirements 4.4**
        """
        # Create a simple sentence from words
        sentence = " ".join(words)
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        assume(len(analysis.tokens) >= 2)
        
        # Bind roles
        roles = self.binder.bind_roles(analysis, root)
        
        # Property: All assigned roles must be compatible with the ROOT
        compatible_roles = get_compatible_roles(root)
        
        for assigned_role in roles.keys():
            assert assigned_role in compatible_roles, \
                f"Role {assigned_role.value} is not compatible with ROOT {root.value}. " \
                f"Compatible roles: {[r.value for r in compatible_roles]}"