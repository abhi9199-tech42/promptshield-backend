"""
Unit tests for ROLESBinder component.

These tests validate specific examples and edge cases for semantic role assignment.
"""

import pytest
from ptil import ROLESBinder, LinguisticAnalyzer, ROOT, Role, Entity


class TestROLESBinder:
    """Unit tests for ROLESBinder component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LinguisticAnalyzer()
        self.binder = ROLESBinder()
    
    def test_simple_subject_agent_binding(self):
        """Test basic subject to AGENT role binding."""
        sentence = "The boy runs"
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        
        # Bind roles with MOTION root
        roles = self.binder.bind_roles(analysis, ROOT.MOTION)
        
        # Debug: print what we got
        print(f"Sentence: {sentence}")
        print(f"Tokens: {analysis.tokens}")
        print(f"POS tags: {analysis.pos_tags}")
        print(f"Dependencies: {analysis.dependencies}")
        print(f"Roles: {roles}")
        
        # Should have AGENT role bound to "boy"
        assert Role.AGENT in roles
        assert "boy" in roles[Role.AGENT].text.lower()
    
    def test_subject_verb_object_binding(self):
        """Test subject-verb-object role binding."""
        sentence = "The man sees the cat"
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        
        # Bind roles with PERCEPTION root
        roles = self.binder.bind_roles(analysis, ROOT.PERCEPTION)
        
        # Debug: print what we got
        print(f"Sentence: {sentence}")
        print(f"Tokens: {analysis.tokens}")
        print(f"POS tags: {analysis.pos_tags}")
        print(f"Dependencies: {analysis.dependencies}")
        print(f"Roles: {roles}")
        
        # Should have AGENT and THEME roles
        assert Role.AGENT in roles
        assert Role.THEME in roles
        assert "man" in roles[Role.AGENT].text.lower()
        assert "cat" in roles[Role.THEME].text.lower()
    
    def test_prepositional_phrase_binding(self):
        """Test prepositional phrase role binding."""
        sentence = "The boy goes to school"
        
        # Analyze the sentence
        analysis = self.analyzer.analyze(sentence)
        
        # Bind roles with MOTION root
        roles = self.binder.bind_roles(analysis, ROOT.MOTION)
        
        # Debug: print what we got
        print(f"Sentence: {sentence}")
        print(f"Tokens: {analysis.tokens}")
        print(f"POS tags: {analysis.pos_tags}")
        print(f"Dependencies: {analysis.dependencies}")
        print(f"Roles: {roles}")
        
        # Should have AGENT and GOAL roles
        assert Role.AGENT in roles
        assert Role.GOAL in roles
        assert "boy" in roles[Role.AGENT].text.lower()
        assert "school" in roles[Role.GOAL].text.lower()