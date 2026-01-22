"""
OPS Extractor component for PTIL semantic encoder.

This module extracts and orders semantic operators from grammatical markers,
including temporal, aspect, polarity, modality, causation, and direction operators.
Maintains left-to-right operator ordering with non-commutativity.
"""

from typing import List
from .models import Operator, LinguisticAnalysis


class OPSExtractor:
    """
    Extracts and orders semantic operators from linguistic analysis.
    
    Processes temporal, aspect, polarity, modality, causation, and direction
    operators while maintaining non-commutative left-to-right ordering.
    """
    
    def __init__(self):
        """Initialize the OPS extractor with operator mapping rules."""
        # Temporal operator mappings
        self.temporal_mappings = {
            "past": Operator.PAST,
            "present": Operator.PRESENT,
            "future": Operator.FUTURE
        }
        
        # Aspect operator mappings
        self.aspect_mappings = {
            "continuous": Operator.CONTINUOUS,
            "completed": Operator.COMPLETED,
            "habitual": Operator.HABITUAL
        }
        
        # Modality keywords for operator detection
        self.modality_keywords = {
            "can": Operator.POSSIBLE,
            "could": Operator.POSSIBLE,
            "may": Operator.POSSIBLE,
            "might": Operator.POSSIBLE,
            "must": Operator.NECESSARY,
            "should": Operator.OBLIGATORY,
            "ought": Operator.OBLIGATORY,
            "shall": Operator.OBLIGATORY,
            "allowed": Operator.PERMITTED,
            "permitted": Operator.PERMITTED
        }
        
        # Causation keywords
        self.causation_keywords = {
            "make": Operator.CAUSATIVE,
            "cause": Operator.CAUSATIVE,
            "force": Operator.FORCED,
            "compel": Operator.FORCED,
            "decide": Operator.SELF_INITIATED,
            "choose": Operator.SELF_INITIATED
        }
        
        # Direction keywords
        self.direction_keywords = {
            "into": Operator.DIRECTION_IN,
            "in": Operator.DIRECTION_IN,
            "out": Operator.DIRECTION_OUT,
            "toward": Operator.TOWARD,
            "towards": Operator.TOWARD,
            "to": Operator.TOWARD,
            "away": Operator.AWAY,
            "from": Operator.AWAY
        }
    
    def extract_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extracts ordered operators maintaining non-commutativity.
        
        Args:
            analysis: LinguisticAnalysis containing tokens and markers
            
        Returns:
            List of operators in left-to-right order
        """
        if not analysis.tokens:
            return []
        
        operators = []
        
        # Extract operators in order of precedence and position
        # 1. Temporal operators (from tense markers)
        temporal_ops = self._extract_temporal_operators(analysis)
        operators.extend(temporal_ops)
        
        # 2. Aspect operators (from aspect markers)
        aspect_ops = self._extract_aspect_operators(analysis)
        operators.extend(aspect_ops)
        
        # 3. Negation operators (from negation markers)
        negation_ops = self._extract_negation_operators(analysis)
        operators.extend(negation_ops)
        
        # 4. Modality operators (from modal verbs and keywords)
        modality_ops = self._extract_modality_operators(analysis)
        operators.extend(modality_ops)
        
        # 5. Causation operators (from causative constructions)
        causation_ops = self._extract_causation_operators(analysis)
        operators.extend(causation_ops)
        
        # 6. Direction operators (from directional prepositions)
        direction_ops = self._extract_direction_operators(analysis)
        operators.extend(direction_ops)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_operators = []
        for op in operators:
            if op not in seen:
                seen.add(op)
                unique_operators.append(op)
        
        return unique_operators
    
    def _extract_temporal_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extract temporal operators from tense markers.
        
        Args:
            analysis: LinguisticAnalysis with tense markers
            
        Returns:
            List of temporal operators
        """
        temporal_ops = []
        
        # Process tense markers in order of appearance
        for tense_type, indices in analysis.tense_markers.items():
            if indices and tense_type in self.temporal_mappings:
                temporal_ops.append(self.temporal_mappings[tense_type])
        
        # Default to PRESENT if no explicit tense markers found
        if not temporal_ops:
            temporal_ops.append(Operator.PRESENT)
        
        return temporal_ops
    
    def _extract_aspect_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extract aspect operators from aspectual markers.
        
        Args:
            analysis: LinguisticAnalysis with aspect markers
            
        Returns:
            List of aspect operators
        """
        aspect_ops = []
        
        # Process aspect markers in order of appearance
        for aspect_type, indices in analysis.aspect_markers.items():
            if indices and aspect_type in self.aspect_mappings:
                aspect_ops.append(self.aspect_mappings[aspect_type])
        
        return aspect_ops
    
    def _extract_negation_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extract negation operators from negation markers.
        
        Args:
            analysis: LinguisticAnalysis with negation markers
            
        Returns:
            List of negation operators
        """
        negation_ops = []
        
        # Add NEGATION operator if negation markers are present
        if analysis.negation_markers:
            negation_ops.append(Operator.NEGATION)
        
        return negation_ops
    
    def _extract_modality_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extract modality operators from modal verbs and keywords.
        
        Args:
            analysis: LinguisticAnalysis with tokens
            
        Returns:
            List of modality operators
        """
        modality_ops = []
        
        # Check tokens for modality keywords
        for i, token in enumerate(analysis.tokens):
            token_lower = token.lower()
            if token_lower in self.modality_keywords:
                modality_ops.append(self.modality_keywords[token_lower])
        
        return modality_ops
    
    def _extract_causation_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extract causation operators from causative constructions.
        
        Args:
            analysis: LinguisticAnalysis with tokens
            
        Returns:
            List of causation operators
        """
        causation_ops = []
        
        # Check tokens for causation keywords
        for i, token in enumerate(analysis.tokens):
            token_lower = token.lower()
            if token_lower in self.causation_keywords:
                causation_ops.append(self.causation_keywords[token_lower])
        
        return causation_ops
    
    def _extract_direction_operators(self, analysis: LinguisticAnalysis) -> List[Operator]:
        """
        Extract direction operators from directional prepositions.
        
        Args:
            analysis: LinguisticAnalysis with tokens
            
        Returns:
            List of direction operators
        """
        direction_ops = []
        
        # Check tokens for direction keywords
        for i, token in enumerate(analysis.tokens):
            token_lower = token.lower()
            if token_lower in self.direction_keywords:
                direction_ops.append(self.direction_keywords[token_lower])
        
        return direction_ops