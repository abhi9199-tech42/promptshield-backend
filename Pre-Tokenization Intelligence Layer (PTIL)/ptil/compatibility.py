"""
ROOT-ROLE compatibility matrix for PTIL semantic encoder.

This module defines which semantic roles are compatible with each ROOT type,
ensuring that generated CSCs maintain semantic validity.
"""

from typing import Dict, Set
from .models import ROOT, Role


# ROOT-ROLE compatibility matrix
# Each ROOT defines the set of roles that are semantically valid for that event type
ROOT_ROLE_COMPATIBILITY: Dict[ROOT, Set[Role]] = {
    ROOT.MOTION: {
        Role.AGENT,      # Who is moving
        Role.THEME,      # What is being moved
        Role.SOURCE,     # Where movement starts
        Role.GOAL,       # Where movement ends
        Role.LOCATION,   # Where movement occurs
        Role.TIME,       # When movement occurs
        Role.INSTRUMENT  # How movement is accomplished
    },
    
    ROOT.TRANSFER: {
        Role.AGENT,      # Who transfers
        Role.THEME,      # What is transferred
        Role.SOURCE,     # From whom/where
        Role.GOAL,       # To whom/where
        Role.TIME,       # When transfer occurs
        Role.INSTRUMENT  # How transfer is accomplished
    },
    
    ROOT.COMMUNICATION: {
        Role.AGENT,      # Who communicates
        Role.PATIENT,    # To whom communication is directed
        Role.THEME,      # What is communicated
        Role.INSTRUMENT, # How communication occurs
        Role.TIME,       # When communication occurs
        Role.LOCATION    # Where communication occurs
    },
    
    ROOT.COGNITION: {
        Role.AGENT,      # Who thinks/knows
        Role.THEME,      # What is thought/known
        Role.TIME,       # When cognition occurs
        Role.INSTRUMENT  # How cognition is aided
    },
    
    ROOT.PERCEPTION: {
        Role.AGENT,      # Who perceives
        Role.THEME,      # What is perceived
        Role.INSTRUMENT, # How perception occurs
        Role.TIME,       # When perception occurs
        Role.LOCATION    # Where perception occurs
    },
    
    ROOT.CREATION: {
        Role.AGENT,      # Who creates
        Role.THEME,      # What is created
        Role.INSTRUMENT, # How creation occurs
        Role.TIME,       # When creation occurs
        Role.LOCATION,   # Where creation occurs
        Role.SOURCE      # From what creation occurs
    },
    
    ROOT.DESTRUCTION: {
        Role.AGENT,      # Who destroys
        Role.THEME,      # What is destroyed
        Role.INSTRUMENT, # How destruction occurs
        Role.TIME,       # When destruction occurs
        Role.LOCATION    # Where destruction occurs
    },
    
    ROOT.CHANGE: {
        Role.AGENT,      # Who causes change
        Role.THEME,      # What changes
        Role.SOURCE,     # Initial state
        Role.GOAL,       # Final state
        Role.TIME,       # When change occurs
        Role.LOCATION,   # Where change occurs
        Role.INSTRUMENT  # How change occurs
    },
    
    ROOT.POSSESSION: {
        Role.AGENT,      # Who possesses
        Role.THEME,      # What is possessed
        Role.SOURCE,     # From whom possession comes
        Role.TIME,       # When possession occurs
        Role.LOCATION    # Where possession occurs
    },
    
    ROOT.INTENTION: {
        Role.AGENT,      # Who intends
        Role.THEME,      # What is intended
        Role.GOAL,       # Intended outcome
        Role.TIME        # When intention occurs
    },
    
    ROOT.EXISTENCE: {
        Role.THEME,      # What exists
        Role.LOCATION,   # Where existence occurs
        Role.TIME        # When existence occurs
    }
}


def is_role_compatible(root: ROOT, role: Role) -> bool:
    """
    Check if a role is compatible with a given ROOT.
    
    Args:
        root: The ROOT to check compatibility for
        role: The Role to validate
        
    Returns:
        True if the role is compatible with the ROOT, False otherwise
    """
    return role in ROOT_ROLE_COMPATIBILITY.get(root, set())


def get_compatible_roles(root: ROOT) -> Set[Role]:
    """
    Get all roles compatible with a given ROOT.
    
    Args:
        root: The ROOT to get compatible roles for
        
    Returns:
        Set of compatible roles for the ROOT
    """
    return ROOT_ROLE_COMPATIBILITY.get(root, set()).copy()