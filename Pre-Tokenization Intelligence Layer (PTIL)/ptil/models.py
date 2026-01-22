"""
Core data models for PTIL semantic encoder.

This module defines the fundamental data structures used throughout the PTIL system:
- Enums for ROOT, Operator, Role, and META components
- Dataclasses for CSC, Entity, and LinguisticAnalysis
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


class ROOT(Enum):
    """Semantic anchor representing the type of event or state."""
    MOTION = "MOTION"
    TRANSFER = "TRANSFER"
    COMMUNICATION = "COMMUNICATION"
    COGNITION = "COGNITION"
    PERCEPTION = "PERCEPTION"
    CREATION = "CREATION"
    DESTRUCTION = "DESTRUCTION"
    CHANGE = "CHANGE"
    POSSESSION = "POSSESSION"
    INTENTION = "INTENTION"
    EXISTENCE = "EXISTENCE"
    # Additional semantic primitives can be added up to 800 total


class Operator(Enum):
    """Ordered semantic operators encoding grammar, tense, polarity, modality, and direction."""
    
    # Temporal operators
    PAST = "PAST"
    PRESENT = "PRESENT"
    FUTURE = "FUTURE"
    
    # Aspect operators
    CONTINUOUS = "CONTINUOUS"
    COMPLETED = "COMPLETED"
    HABITUAL = "HABITUAL"
    
    # Polarity operators
    NEGATION = "NEGATION"
    AFFIRMATION = "AFFIRMATION"
    
    # Modality operators
    POSSIBLE = "POSSIBLE"
    NECESSARY = "NECESSARY"
    OBLIGATORY = "OBLIGATORY"
    PERMITTED = "PERMITTED"
    
    # Causation operators
    CAUSATIVE = "CAUSATIVE"
    SELF_INITIATED = "SELF_INITIATED"
    FORCED = "FORCED"
    
    # Direction operators
    DIRECTION_IN = "DIRECTION_IN"
    DIRECTION_OUT = "DIRECTION_OUT"
    TOWARD = "TOWARD"
    AWAY = "AWAY"


class Role(Enum):
    """Semantic role bindings that map entities to their functional participation."""
    AGENT = "AGENT"
    PATIENT = "PATIENT"
    THEME = "THEME"
    GOAL = "GOAL"
    SOURCE = "SOURCE"
    INSTRUMENT = "INSTRUMENT"
    LOCATION = "LOCATION"
    TIME = "TIME"


class META(Enum):
    """Context modifiers capturing speech-level and epistemic information."""
    ASSERTIVE = "ASSERTIVE"
    QUESTION = "QUESTION"
    COMMAND = "COMMAND"
    UNCERTAIN = "UNCERTAIN"
    EVIDENTIAL = "EVIDENTIAL"
    EMOTIVE = "EMOTIVE"
    IRONIC = "IRONIC"


@dataclass
class Entity:
    """Represents an entity with original text and normalized form."""
    text: str
    normalized: str


@dataclass
class LinguisticAnalysis:
    """Results of shallow linguistic analysis."""
    tokens: List[str]
    pos_tags: List[str]
    dependencies: List[Tuple[int, str, int]]  # (head_idx, relation, dependent_idx)
    negation_markers: List[int]  # Token indices with negation markers
    tense_markers: Dict[str, List[int]]  # Tense type -> token indices
    aspect_markers: Dict[str, List[int]]  # Aspect type -> token indices


@dataclass
class CSC:
    """Compressed Semantic Code - structured meaning representation."""
    root: ROOT
    ops: List[Operator]
    roles: Dict[Role, Entity]
    meta: Optional[META] = None