"""
CSC Serializer for PTIL semantic encoder.

This module provides the CSCSerializer class that converts CSC structures into
tokenizer-friendly symbolic text format. The serializer ensures proper component
ordering and creates flat, tokenizer-compatible output.
"""

from typing import List
from .models import CSC, Operator, Role


class CSCSerializer:
    """
    Serializer for Compressed Semantic Code (CSC) structures.
    
    Converts CSC objects into symbolic text format that is compatible with
    standard tokenizers (BPE, Unigram, WordPiece).
    """
    
    def serialize(self, csc: CSC) -> str:
        """
        Serialize a single CSC to symbolic text format.
        
        Args:
            csc: The CSC structure to serialize
            
        Returns:
            str: Serialized CSC in format: <ROOT=X> <OPS=Y|Z> <ROLE=ENTITY> <META=W>
        """
        if csc is None:
            raise ValueError("CSC cannot be None")
        
        components = []
        
        # 1. ROOT component (mandatory)
        if csc.root is None:
            raise ValueError("ROOT component is mandatory")
        components.append(f"<ROOT={csc.root.value}>")
        
        # 2. OPS component (mandatory, can be empty)
        if csc.ops:
            ops_values = [op.value for op in csc.ops]
            ops_str = "|".join(ops_values)
            components.append(f"<OPS={ops_str}>")
        else:
            components.append("<OPS=>")
        
        # 3. ROLES component (mandatory, can be empty)
        if csc.roles:
            # Sort roles for consistent output
            sorted_roles = sorted(csc.roles.items(), key=lambda x: x[0].value)
            for role, entity in sorted_roles:
                components.append(f"<{role.value}={entity.normalized}>")
        
        # 4. META component (optional)
        if csc.meta is not None:
            components.append(f"<META={csc.meta.value}>")
        
        return " ".join(components)
    
    def serialize_multiple(self, csc_list: List[CSC]) -> str:
        """
        Serialize multiple CSC structures.
        
        Args:
            csc_list: List of CSC structures to serialize
            
        Returns:
            str: Serialized CSCs separated by spaces
        """
        if not csc_list:
            return ""
        
        serialized_cscs = []
        for csc in csc_list:
            serialized_cscs.append(self.serialize(csc))
        
        return " ".join(serialized_cscs)
    
    def validate_serialization_format(self, serialized: str) -> bool:
        """
        Validate that a serialized string follows the correct format.
        
        Args:
            serialized: The serialized CSC string to validate
            
        Returns:
            bool: True if format is valid, False otherwise
        """
        if not serialized:
            return False
        
        # Check that it contains angle brackets (symbolic format)
        if "<" not in serialized or ">" not in serialized:
            return False
        
        # Check that it's not JSON format
        if serialized.strip().startswith("{") or serialized.strip().startswith("["):
            return False
        
        # Check for required ROOT component
        if "<ROOT=" not in serialized:
            return False
        
        # Check for required OPS component (even if empty)
        if "<OPS=" not in serialized:
            return False
        
        return True
    
    def extract_components_order(self, serialized: str) -> List[str]:
        """
        Extract the order of components from a serialized CSC.
        
        Args:
            serialized: The serialized CSC string
            
        Returns:
            List[str]: List of component types in order (e.g., ['ROOT', 'OPS', 'AGENT', 'META'])
        """
        import re
        
        # Find all component tags
        pattern = r'<([^=]+)='
        matches = re.findall(pattern, serialized)
        
        return matches