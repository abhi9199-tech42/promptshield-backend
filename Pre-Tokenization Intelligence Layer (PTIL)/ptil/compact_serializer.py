"""
Compact CSC Serializer for PTIL semantic encoder.

This module provides a highly optimized, compact serialization format
designed to achieve the target 60-80% token reduction compared to raw text.
"""

from typing import List, Dict
from .models import CSC, ROOT, Operator, Role, META


class CompactCSCSerializer:
    """
    Compact serializer for Compressed Semantic Code (CSC) structures.
    
    Uses numeric codes and minimal syntax to achieve maximum token efficiency
    while maintaining tokenizer compatibility.
    """
    
    def __init__(self):
        """Initialize the compact serializer with encoding mappings."""
        # ROOT mappings (R + single digit/letter)
        self.root_codes = {
            ROOT.MOTION: "R1",
            ROOT.TRANSFER: "R2", 
            ROOT.COMMUNICATION: "R3",
            ROOT.COGNITION: "R4",
            ROOT.PERCEPTION: "R5",
            ROOT.CREATION: "R6",
            ROOT.DESTRUCTION: "R7",
            ROOT.CHANGE: "R8",
            ROOT.POSSESSION: "R9",
            ROOT.INTENTION: "RA",
            ROOT.EXISTENCE: "RB"
        }
        
        # Operator mappings (O + single character)
        self.operator_codes = {
            # Temporal
            Operator.PAST: "O1",
            Operator.PRESENT: "O2", 
            Operator.FUTURE: "O3",
            # Aspect
            Operator.CONTINUOUS: "O4",
            Operator.COMPLETED: "O5",
            Operator.HABITUAL: "O6",
            # Polarity
            Operator.NEGATION: "O7",
            Operator.AFFIRMATION: "O8",
            # Modality
            Operator.POSSIBLE: "O9",
            Operator.NECESSARY: "OA",
            Operator.OBLIGATORY: "OB",
            Operator.PERMITTED: "OC",
            # Causation
            Operator.CAUSATIVE: "OD",
            Operator.SELF_INITIATED: "OE",
            Operator.FORCED: "OF",
            # Direction
            Operator.DIRECTION_IN: "OG",
            Operator.DIRECTION_OUT: "OH",
            Operator.TOWARD: "OI",
            Operator.AWAY: "OJ"
        }
        
        # Role mappings (single letter)
        self.role_codes = {
            Role.AGENT: "A",
            Role.PATIENT: "P", 
            Role.THEME: "T",
            Role.GOAL: "G",
            Role.SOURCE: "S",
            Role.INSTRUMENT: "I",
            Role.LOCATION: "L",
            Role.TIME: "M"  # M for tiMe (T taken by THEME)
        }
        
        # META mappings (M + single character)
        self.meta_codes = {
            META.ASSERTIVE: "M1",
            META.QUESTION: "M2",
            META.COMMAND: "M3", 
            META.UNCERTAIN: "M4",
            META.EVIDENTIAL: "M5",
            META.EMOTIVE: "M6",
            META.IRONIC: "M7"
        }
        
        # Create reverse mappings for deserialization
        self.code_to_root = {v: k for k, v in self.root_codes.items()}
        self.code_to_operator = {v: k for k, v in self.operator_codes.items()}
        self.code_to_role = {v: k for k, v in self.role_codes.items()}
        self.code_to_meta = {v: k for k, v in self.meta_codes.items()}
    
    def serialize(self, csc: CSC) -> str:
        """
        Serialize a single CSC to compact format.
        
        Format: R1 O3O7 A:boy G:school M1
        (ROOT OPERATORS ROLE:entity ROLE:entity META)
        
        Args:
            csc: The CSC structure to serialize
            
        Returns:
            str: Compact serialized CSC
        """
        if csc is None:
            raise ValueError("CSC cannot be None")
        
        components = []
        
        # 1. ROOT component (mandatory) - e.g., "R1"
        if csc.root is None:
            raise ValueError("ROOT component is mandatory")
        
        root_code = self.root_codes.get(csc.root)
        if root_code is None:
            raise ValueError(f"Unknown ROOT: {csc.root}")
        components.append(root_code)
        
        # 2. OPS component (if present) - e.g., "O3O7" for FUTURE|NEGATION
        if csc.ops:
            ops_codes = []
            for op in csc.ops:
                op_code = self.operator_codes.get(op)
                if op_code is None:
                    raise ValueError(f"Unknown operator: {op}")
                ops_codes.append(op_code)
            components.append("".join(ops_codes))
        
        # 3. ROLES component (if present) - e.g., "A:boy G:school"
        if csc.roles:
            # Sort roles for consistent output
            sorted_roles = sorted(csc.roles.items(), key=lambda x: x[0].value)
            for role, entity in sorted_roles:
                role_code = self.role_codes.get(role)
                if role_code is None:
                    raise ValueError(f"Unknown role: {role}")
                # Use normalized entity text, compress common words
                entity_text = self._compress_entity(entity.normalized)
                components.append(f"{role_code}:{entity_text}")
        
        # 4. META component (if present) - e.g., "M1"
        if csc.meta is not None:
            meta_code = self.meta_codes.get(csc.meta)
            if meta_code is None:
                raise ValueError(f"Unknown META: {csc.meta}")
            components.append(meta_code)
        
        return " ".join(components)
    
    def serialize_multiple(self, csc_list: List[CSC]) -> str:
        """
        Serialize multiple CSC structures.
        
        Args:
            csc_list: List of CSC structures to serialize
            
        Returns:
            str: Compact serialized CSCs separated by semicolons
        """
        if not csc_list:
            return ""
        
        serialized_cscs = []
        for csc in csc_list:
            serialized_cscs.append(self.serialize(csc))
        
        # Use semicolon to separate multiple CSCs for clarity
        return "; ".join(serialized_cscs)
    
    def _compress_entity(self, entity_text: str) -> str:
        """
        Compress common entity text for better token efficiency.
        
        Args:
            entity_text: Original entity text
            
        Returns:
            str: Compressed entity text
        """
        # More aggressive compressions using single characters
        compressions = {
            # Articles and determiners
            "the": "",  # Remove entirely
            "a": "",    # Remove entirely  
            "an": "",   # Remove entirely
            "this": "",
            "that": "",
            
            # Common nouns - single letters
            "boy": "b",
            "girl": "g", 
            "man": "m",
            "woman": "w",
            "school": "s",
            "house": "h",
            "car": "c",
            "book": "k",
            "library": "l",
            "project": "p",
            "task": "t",
            "mat": "m",
            "cat": "c",
            
            # Time expressions
            "tomorrow": "T",
            "yesterday": "Y",
            "today": "D",
            
            # Common verbs
            "working": "w",
            "reading": "r",
            "finish": "f",
            "been": "",  # Remove auxiliary
            "have": "",  # Remove auxiliary
            "should": "", # Captured in OPS
            "will": "",   # Captured in OPS
            "not": "",    # Captured in OPS
        }
        
        # Apply compressions word by word
        words = entity_text.lower().split()
        compressed_words = []
        
        for word in words:
            compressed = compressions.get(word, word[:2])  # Default: first 2 chars
            if compressed:  # Only add non-empty results
                compressed_words.append(compressed)
        
        result = "".join(compressed_words)
        
        # If result is empty, use first letter of original
        if not result and entity_text:
            result = entity_text[0].lower()
        
        # Limit length to prevent excessive tokens
        if len(result) > 4:
            result = result[:4]
        
        return result or "x"  # Fallback to 'x' if completely empty
    
    def get_format_description(self) -> str:
        """
        Get a description of the compact format.
        
        Returns:
            str: Format description
        """
        return """
Compact CSC Format:
- ROOT: R1-RB (R + digit/letter)
- OPS: O1-OJ concatenated (e.g., O3O7 for FUTURE|NEGATION)  
- ROLES: Letter:entity (e.g., A:boy G:sch)
- META: M1-M7 (M + digit)
- Multiple CSCs: separated by "; "

Example: "R1 O3O7 A:b G:sch M1" 
= <ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=boy> <GOAL=school> <META=ASSERTIVE>
"""
    
    def estimate_compression_ratio(self, original_format: str, compact_format: str) -> float:
        """
        Estimate compression ratio between formats.
        
        Args:
            original_format: Original verbose format
            compact_format: Compact format
            
        Returns:
            float: Compression ratio (original_length / compact_length)
        """
        if not compact_format:
            return 1.0
        
        return len(original_format) / len(compact_format)
    
    def validate_compact_format(self, serialized: str) -> bool:
        """
        Validate that a serialized string follows the compact format.
        
        Args:
            serialized: The compact serialized CSC string
            
        Returns:
            bool: True if format is valid, False otherwise
        """
        if not serialized or not serialized.strip():
            return False
        
        # Split by semicolon for multiple CSCs
        csc_parts = serialized.split(";")
        
        for csc_part in csc_parts:
            csc_part = csc_part.strip()
            if not csc_part:
                continue
                
            # Should start with ROOT code (R + digit/letter)
            if not (csc_part.startswith("R") and len(csc_part) >= 2):
                return False
            
            # Should not contain angle brackets (that's verbose format)
            if "<" in csc_part or ">" in csc_part:
                return False
        
        return True