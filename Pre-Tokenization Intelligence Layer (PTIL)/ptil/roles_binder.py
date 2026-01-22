"""
ROLES Binder component for PTIL semantic encoder.

This module provides semantic role assignment functionality, binding entities
to their functional roles (AGENT, PATIENT, THEME, etc.) based on syntactic
analysis and ROOT requirements.
"""

import spacy
from spacy.tokens import Token
from typing import Dict, List, Optional, Set, Tuple
from .models import ROOT, Role, Entity, LinguisticAnalysis
from .compatibility import is_role_compatible, get_compatible_roles


class ROLESBinder:
    """
    Binds entities to semantic roles independent of word order and syntax.
    
    The ROLESBinder analyzes syntactic dependencies and maps them to semantic
    roles based on the identified ROOT and its compatibility requirements.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the ROLES binder with a spaCy model.
        
        Args:
            model_name: Name of the spaCy model to use for analysis
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{model_name}' not found. "
                f"Please install it with: python -m spacy download {model_name}"
            )
    
    def bind_roles(self, analysis: LinguisticAnalysis, root: ROOT) -> Dict[Role, Entity]:
        """
        Assigns entities to semantic roles based on ROOT requirements.
        
        Args:
            analysis: Linguistic analysis containing dependencies and tokens
            root: The identified ROOT for role compatibility validation
            
        Returns:
            Dictionary mapping roles to entities
        """
        if not analysis.tokens:
            return {}
        
        # Re-process text to get spaCy doc for detailed analysis
        text = " ".join(analysis.tokens)
        doc = self.nlp(text)
        
        roles = {}
        compatible_roles = get_compatible_roles(root)
        
        # Find the main verb (predicate) in the sentence
        main_verb = self._find_main_verb(doc)
        if not main_verb:
            return roles
        
        # Bind subject to AGENT role for agentive sentences
        subject_entity = self._bind_subject_to_agent(doc, main_verb, compatible_roles)
        if subject_entity:
            roles[Role.AGENT] = subject_entity
        
        # Bind direct objects to PATIENT/THEME roles
        object_roles = self._bind_objects_to_roles(doc, main_verb, root, compatible_roles)
        roles.update(object_roles)
        
        # Bind prepositional phrases to semantic roles
        prep_roles = self._bind_prepositional_phrases(doc, main_verb, compatible_roles)
        roles.update(prep_roles)
        
        # Validate all assigned roles are compatible with ROOT
        validated_roles = self._validate_role_compatibility(roles, root)
        
        return validated_roles
    
    def _find_main_verb(self, doc) -> Optional[Token]:
        """
        Find the main verb (predicate) in the sentence.
        
        Args:
            doc: spaCy document
            
        Returns:
            Main verb token or None if not found
        """
        # Look for the root verb
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ in ["VERB", "AUX"]:
                return token
        
        # Fallback: find any verb
        for token in doc:
            if token.pos_ == "VERB":
                return token
        
        return None
    
    def _bind_subject_to_agent(self, doc, main_verb: Token, 
                              compatible_roles: Set[Role]) -> Optional[Entity]:
        """
        Bind subject to AGENT role for agentive sentences.
        
        Args:
            doc: spaCy document
            main_verb: Main verb token
            compatible_roles: Set of roles compatible with current ROOT
            
        Returns:
            Entity bound to AGENT role or None
        """
        if Role.AGENT not in compatible_roles:
            return None
        
        # Find subject dependencies
        # Exclude passive subjects (nsubjpass, csubjpass) as they are typically PATIENT/THEME, not AGENT
        subject_deps = {"nsubj", "csubj"}
        
        for token in doc:
            if token.head == main_verb and token.dep_ in subject_deps:
                # Get the full noun phrase for the subject
                subject_text = self._extract_noun_phrase(token)
                return Entity(
                    text=subject_text,
                    normalized=token.lemma_.lower()
                )
        
        return None
    
    def _bind_objects_to_roles(self, doc, main_verb: Token, root: ROOT,
                              compatible_roles: Set[Role]) -> Dict[Role, Entity]:
        """
        Bind direct objects to PATIENT/THEME roles based on ROOT requirements.
        
        Args:
            doc: spaCy document
            main_verb: Main verb token
            root: Current ROOT for role selection
            compatible_roles: Set of roles compatible with current ROOT
            
        Returns:
            Dictionary of object role bindings
        """
        roles = {}
        
        # Find direct object dependencies
        object_deps = {"dobj", "pobj", "iobj"}
        
        for token in doc:
            if token.head == main_verb and token.dep_ in object_deps:
                object_text = self._extract_noun_phrase(token)
                entity = Entity(
                    text=object_text,
                    normalized=token.lemma_.lower()
                )
                
                # Choose appropriate role based on ROOT and availability
                role = self._select_object_role(root, compatible_roles, roles)
                if role:
                    roles[role] = entity
        
        return roles
    
    def _select_object_role(self, root: ROOT, compatible_roles: Set[Role],
                           existing_roles: Dict[Role, Entity]) -> Optional[Role]:
        """
        Select appropriate role for object based on ROOT and existing assignments.
        
        Args:
            root: Current ROOT
            compatible_roles: Set of compatible roles
            existing_roles: Already assigned roles
            
        Returns:
            Selected role or None
        """
        # Priority order for object roles
        object_role_priority = [Role.PATIENT, Role.THEME]
        
        for role in object_role_priority:
            if role in compatible_roles and role not in existing_roles:
                return role
        
        return None
    
    def _bind_prepositional_phrases(self, doc, main_verb: Token,
                                   compatible_roles: Set[Role]) -> Dict[Role, Entity]:
        """
        Bind prepositional phrases to appropriate semantic roles.
        
        Args:
            doc: spaCy document
            main_verb: Main verb token
            compatible_roles: Set of roles compatible with current ROOT
            
        Returns:
            Dictionary of prepositional role bindings
        """
        roles = {}
        
        # Preposition to role mappings
        prep_role_map = {
            # Goal/destination prepositions
            "to": Role.GOAL,
            "into": Role.GOAL,
            "toward": Role.GOAL,
            "towards": Role.GOAL,
            
            # Source/origin prepositions
            "from": Role.SOURCE,
            "out": Role.SOURCE,
            "off": Role.SOURCE,
            
            # Location prepositions
            "at": Role.LOCATION,
            "in": Role.LOCATION,
            "on": Role.LOCATION,
            "under": Role.LOCATION,
            "over": Role.LOCATION,
            "beside": Role.LOCATION,
            "near": Role.LOCATION,
            
            # Time prepositions
            "during": Role.TIME,
            "before": Role.TIME,
            "after": Role.TIME,
            "while": Role.TIME,
            
            # Instrument prepositions
            "with": Role.INSTRUMENT,
            "by": Role.INSTRUMENT,
            "using": Role.INSTRUMENT,
        }
        
        # Find prepositional phrases
        for token in doc:
            if token.pos_ == "ADP":  # Preposition
                prep_text = token.text.lower()
                
                # Get the role for this preposition
                role = prep_role_map.get(prep_text)
                if not role or role not in compatible_roles or role in roles:
                    continue
                
                # Find the object of the preposition
                prep_object = None
                for child in token.children:
                    if child.dep_ == "pobj":
                        prep_object = child
                        break
                
                if prep_object:
                    object_text = self._extract_noun_phrase(prep_object)
                    roles[role] = Entity(
                        text=object_text,
                        normalized=prep_object.lemma_.lower()
                    )
        
        return roles
    
    def _extract_noun_phrase(self, token: Token) -> str:
        """
        Extract the full noun phrase containing the given token.
        
        Args:
            token: Head token of the noun phrase
            
        Returns:
            Full noun phrase text
        """
        # Get the noun phrase span
        if token.pos_ in ["NOUN", "PROPN", "PRON"]:
            # Find the leftmost and rightmost tokens in the noun phrase
            left_bound = token.left_edge.i
            right_bound = token.right_edge.i + 1
            
            # Extract the text span
            doc = token.doc
            return doc[left_bound:right_bound].text
        
        return token.text
    
    def _validate_role_compatibility(self, roles: Dict[Role, Entity], 
                                   root: ROOT) -> Dict[Role, Entity]:
        """
        Validate that all assigned roles are compatible with the ROOT.
        
        Args:
            roles: Dictionary of role assignments
            root: Current ROOT for validation
            
        Returns:
            Validated dictionary with only compatible roles
        """
        validated_roles = {}
        
        for role, entity in roles.items():
            if is_role_compatible(root, role):
                validated_roles[role] = entity
        
        return validated_roles