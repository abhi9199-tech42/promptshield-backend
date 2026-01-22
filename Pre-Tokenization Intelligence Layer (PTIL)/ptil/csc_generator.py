"""
CSC Generator for PTIL semantic encoder.

This module provides the CSCGenerator class that combines ROOT, OPS, ROLES, and optional META
components into structured CSC representations. It validates CSC completeness and handles
multiple predicate scenarios.
"""

from typing import List, Dict, Optional
from .models import ROOT, Operator, Role, META, CSC, Entity
from .compatibility import ROOT_ROLE_COMPATIBILITY


class CSCGenerator:
    """
    Generator for Compressed Semantic Code (CSC) structures.
    
    Combines semantic components into validated CSC representations with proper
    structure validation and multiple predicate handling.
    """
    
    def generate_csc(
        self, 
        root: ROOT, 
        ops: List[Operator], 
        roles: Dict[Role, Entity], 
        meta: Optional[META] = None
    ) -> CSC:
        """
        Generate a single CSC from semantic components.
        
        Args:
            root: The semantic ROOT primitive
            ops: List of ordered semantic operators
            roles: Dictionary mapping roles to entities
            meta: Optional META component for speech acts and epistemic info
            
        Returns:
            CSC: Validated compressed semantic code structure
            
        Raises:
            ValueError: If CSC structure is invalid or incomplete
        """
        # Validate mandatory components
        if root is None:
            raise ValueError("ROOT component is mandatory for CSC generation")
        
        if ops is None:
            ops = []
        
        if roles is None:
            roles = {}
        
        # Validate ROOT-ROLE compatibility
        self._validate_role_compatibility(root, roles)
        
        # Create CSC structure
        csc = CSC(
            root=root,
            ops=ops,
            roles=roles,
            meta=meta
        )
        
        return csc
    
    def generate_multiple_csc(
        self,
        predicates_data: List[Dict]
    ) -> List[CSC]:
        """
        Generate multiple CSC instances for sentences with multiple predicates.
        
        Args:
            predicates_data: List of dictionaries, each containing:
                - 'root': ROOT primitive
                - 'ops': List of operators
                - 'roles': Dict of role bindings
                - 'meta': Optional META component
                
        Returns:
            List[CSC]: List of validated CSC structures
            
        Raises:
            ValueError: If any CSC structure is invalid
        """
        if not predicates_data:
            raise ValueError("At least one predicate is required for CSC generation")
        
        csc_list = []
        
        for predicate_data in predicates_data:
            root = predicate_data.get('root')
            ops = predicate_data.get('ops', [])
            roles = predicate_data.get('roles', {})
            meta = predicate_data.get('meta')
            
            csc = self.generate_csc(root, ops, roles, meta)
            csc_list.append(csc)
        
        return csc_list
    
    def _validate_role_compatibility(self, root: ROOT, roles: Dict[Role, Entity]) -> None:
        """
        Validate that assigned roles are compatible with the ROOT.
        
        Args:
            root: The ROOT primitive to validate against
            roles: Dictionary of role assignments
            
        Raises:
            ValueError: If any role is incompatible with the ROOT
        """
        if root not in ROOT_ROLE_COMPATIBILITY:
            # If ROOT not in compatibility matrix, allow all roles (graceful handling)
            return
        
        compatible_roles = ROOT_ROLE_COMPATIBILITY[root]
        
        for role in roles.keys():
            if role not in compatible_roles:
                raise ValueError(
                    f"Role {role.value} is not compatible with ROOT {root.value}. "
                    f"Compatible roles: {[r.value for r in compatible_roles]}"
                )
    
    def validate_csc_completeness(self, csc: CSC) -> bool:
        """
        Validate that a CSC has all mandatory components.
        
        Args:
            csc: The CSC to validate
            
        Returns:
            bool: True if CSC is complete, False otherwise
        """
        # Check mandatory components
        if csc.root is None:
            return False
        
        if csc.ops is None:
            return False
        
        if csc.roles is None:
            return False
        
        # META is optional, so we don't check it
        
        return True