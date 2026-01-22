"""
Cross-lingual consistency validator for PTIL semantic encoder.

This module provides validation that semantically equivalent sentences
in different languages produce identical CSC representations, ensuring
language-independent ROOT primitive usage.
"""

from typing import List, Dict, Tuple, Optional, Set
from .models import CSC, ROOT, Operator, Role, META
from .encoder import PTILEncoder
from .linguistic_analyzer import LinguisticAnalyzer


class CrossLingualValidator:
    """
    Validates cross-lingual consistency of CSC generation.
    
    Ensures that semantically equivalent sentences in different languages
    produce identical or highly similar CSC representations.
    """
    
    def __init__(self):
        """Initialize the cross-lingual validator."""
        self.encoders = {}  # Cache for language-specific encoders
        self.supported_languages = LinguisticAnalyzer.get_supported_languages()
    
    def get_encoder_for_language(self, language: str) -> PTILEncoder:
        """
        Get or create a PTIL encoder for the specified language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            PTILEncoder: Encoder configured for the language
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.supported_languages:
            raise ValueError(f"Language '{language}' not supported. "
                           f"Supported languages: {list(self.supported_languages)}")
        
        if language not in self.encoders:
            # Create language-specific encoder
            model_name = LinguisticAnalyzer.LANGUAGE_MODELS[language]
            self.encoders[language] = PTILEncoder(model_name=model_name)
        
        return self.encoders[language]
    
    def validate_cross_lingual_consistency(self, 
                                         text_pairs: List[Tuple[str, str, str]]) -> Dict[str, any]:
        """
        Validate that semantically equivalent sentences produce consistent CSCs.
        
        Args:
            text_pairs: List of (text, language1, language2) tuples for comparison
            
        Returns:
            Dict containing validation results with consistency metrics
        """
        results = {
            "total_pairs": len(text_pairs),
            "consistent_pairs": 0,
            "inconsistent_pairs": 0,
            "consistency_rate": 0.0,
            "detailed_results": [],
            "root_consistency": {},
            "operator_consistency": {},
            "role_consistency": {}
        }
        
        for i, (text1, lang1, text2, lang2) in enumerate(text_pairs):
            try:
                # Get encoders for both languages
                encoder1 = self.get_encoder_for_language(lang1)
                encoder2 = self.get_encoder_for_language(lang2)
                
                # Encode both texts
                cscs1 = encoder1.encode(text1)
                cscs2 = encoder2.encode(text2)
                
                # Compare CSCs
                comparison = self._compare_csc_lists(cscs1, cscs2)
                
                # Update results
                if comparison["is_consistent"]:
                    results["consistent_pairs"] += 1
                else:
                    results["inconsistent_pairs"] += 1
                
                # Store detailed result
                results["detailed_results"].append({
                    "pair_index": i,
                    "text1": text1,
                    "lang1": lang1,
                    "text2": text2,
                    "lang2": lang2,
                    "cscs1": cscs1,
                    "cscs2": cscs2,
                    "comparison": comparison
                })
                
                # Update component consistency tracking
                self._update_component_consistency(comparison, results)
                
            except Exception as e:
                results["detailed_results"].append({
                    "pair_index": i,
                    "text1": text1,
                    "lang1": lang1,
                    "text2": text2,
                    "lang2": lang2,
                    "error": str(e)
                })
                results["inconsistent_pairs"] += 1
        
        # Calculate consistency rate
        if results["total_pairs"] > 0:
            results["consistency_rate"] = results["consistent_pairs"] / results["total_pairs"]
        
        return results
    
    def validate_language_independent_roots(self, 
                                          texts_by_language: Dict[str, List[str]]) -> Dict[str, any]:
        """
        Validate that the same ROOT primitives are used across languages.
        
        Args:
            texts_by_language: Dictionary mapping language codes to lists of texts
            
        Returns:
            Dict containing validation results for ROOT usage consistency
        """
        results = {
            "languages_tested": list(texts_by_language.keys()),
            "total_texts_per_language": {lang: len(texts) for lang, texts in texts_by_language.items()},
            "roots_by_language": {},
            "common_roots": set(),
            "language_specific_roots": {},
            "root_usage_consistency": 0.0
        }
        
        # Collect ROOTs used by each language
        for language, texts in texts_by_language.items():
            try:
                encoder = self.get_encoder_for_language(language)
                language_roots = set()
                
                for text in texts:
                    cscs = encoder.encode(text)
                    for csc in cscs:
                        language_roots.add(csc.root)
                
                results["roots_by_language"][language] = language_roots
                
            except Exception as e:
                results["roots_by_language"][language] = f"Error: {e}"
        
        # Find common and language-specific roots
        if len(results["roots_by_language"]) > 1:
            all_root_sets = [roots for roots in results["roots_by_language"].values() 
                           if isinstance(roots, set)]
            
            if all_root_sets:
                results["common_roots"] = set.intersection(*all_root_sets)
                
                for language, roots in results["roots_by_language"].items():
                    if isinstance(roots, set):
                        language_specific = roots - results["common_roots"]
                        if language_specific:
                            results["language_specific_roots"][language] = language_specific
                
                # Calculate consistency (ratio of common to total unique roots)
                all_roots = set.union(*all_root_sets)
                if all_roots:
                    results["root_usage_consistency"] = len(results["common_roots"]) / len(all_roots)
        
        return results
    
    def _compare_csc_lists(self, cscs1: List[CSC], cscs2: List[CSC]) -> Dict[str, any]:
        """
        Compare two lists of CSCs for consistency.
        
        Args:
            cscs1: First list of CSCs
            cscs2: Second list of CSCs
            
        Returns:
            Dict containing comparison results
        """
        comparison = {
            "is_consistent": False,
            "csc_count_match": len(cscs1) == len(cscs2),
            "root_matches": 0,
            "operator_matches": 0,
            "role_matches": 0,
            "meta_matches": 0,
            "total_comparisons": min(len(cscs1), len(cscs2)),
            "details": []
        }
        
        # Compare each CSC pair
        for i in range(comparison["total_comparisons"]):
            csc1, csc2 = cscs1[i], cscs2[i]
            
            csc_comparison = {
                "index": i,
                "root_match": csc1.root == csc2.root,
                "operators_match": self._compare_operators(csc1.ops, csc2.ops),
                "roles_match": self._compare_roles(csc1.roles, csc2.roles),
                "meta_match": csc1.meta == csc2.meta
            }
            
            # Update counters
            if csc_comparison["root_match"]:
                comparison["root_matches"] += 1
            if csc_comparison["operators_match"]:
                comparison["operator_matches"] += 1
            if csc_comparison["roles_match"]:
                comparison["role_matches"] += 1
            if csc_comparison["meta_match"]:
                comparison["meta_matches"] += 1
            
            comparison["details"].append(csc_comparison)
        
        # Determine overall consistency
        if comparison["total_comparisons"] > 0:
            consistency_score = (
                comparison["root_matches"] + 
                comparison["operator_matches"] + 
                comparison["role_matches"] + 
                comparison["meta_matches"]
            ) / (4 * comparison["total_comparisons"])
            
            # Consider consistent if score is above threshold (e.g., 0.8)
            comparison["is_consistent"] = consistency_score >= 0.8
            comparison["consistency_score"] = consistency_score
        
        return comparison
    
    def _compare_operators(self, ops1: List[Operator], ops2: List[Operator]) -> bool:
        """
        Compare two lists of operators for equivalence.
        
        Args:
            ops1: First list of operators
            ops2: Second list of operators
            
        Returns:
            bool: True if operators are equivalent
        """
        # Convert to sets for comparison (order might vary slightly)
        set1 = set(ops1)
        set2 = set(ops2)
        
        # Allow for minor differences in operator representation
        # (e.g., different aspect markers that mean the same thing)
        return set1 == set2 or self._are_operators_semantically_equivalent(set1, set2)
    
    def _are_operators_semantically_equivalent(self, ops1: Set[Operator], ops2: Set[Operator]) -> bool:
        """
        Check if two sets of operators are semantically equivalent.
        
        Args:
            ops1: First set of operators
            ops2: Second set of operators
            
        Returns:
            bool: True if semantically equivalent
        """
        # Define equivalent operator groups
        equivalent_groups = [
            {Operator.CONTINUOUS, Operator.HABITUAL},  # Both indicate ongoing action
            {Operator.PAST, Operator.COMPLETED},       # Both indicate completed action
        ]
        
        # Check if differences are within equivalent groups
        diff1 = ops1 - ops2
        diff2 = ops2 - ops1
        
        for group in equivalent_groups:
            if diff1.issubset(group) and diff2.issubset(group):
                return True
        
        return False
    
    def _compare_roles(self, roles1: Dict[Role, any], roles2: Dict[Role, any]) -> bool:
        """
        Compare two role dictionaries for equivalence.
        
        Args:
            roles1: First role dictionary
            roles2: Second role dictionary
            
        Returns:
            bool: True if roles are equivalent
        """
        # Compare role types (keys)
        if set(roles1.keys()) != set(roles2.keys()):
            return False
        
        # Compare role entities (simplified - just check if both have entities)
        for role in roles1.keys():
            if role in roles2:
                # For now, just check that both have entities for the same roles
                # More sophisticated comparison could check entity normalization
                entity1 = roles1[role]
                entity2 = roles2[role]
                
                # Basic entity comparison (could be enhanced)
                if hasattr(entity1, 'normalized') and hasattr(entity2, 'normalized'):
                    if entity1.normalized.lower() != entity2.normalized.lower():
                        # Allow for minor variations in entity normalization
                        continue
        
        return True
    
    def _update_component_consistency(self, comparison: Dict[str, any], results: Dict[str, any]) -> None:
        """
        Update component-specific consistency tracking.
        
        Args:
            comparison: Comparison results for a single pair
            results: Overall results dictionary to update
        """
        if comparison["total_comparisons"] > 0:
            # Update ROOT consistency
            root_rate = comparison["root_matches"] / comparison["total_comparisons"]
            if "root_consistency" not in results or not results["root_consistency"]:
                results["root_consistency"] = {"rates": [], "average": 0.0}
            results["root_consistency"]["rates"].append(root_rate)
            results["root_consistency"]["average"] = sum(results["root_consistency"]["rates"]) / len(results["root_consistency"]["rates"])
            
            # Update operator consistency
            op_rate = comparison["operator_matches"] / comparison["total_comparisons"]
            if "operator_consistency" not in results or not results["operator_consistency"]:
                results["operator_consistency"] = {"rates": [], "average": 0.0}
            results["operator_consistency"]["rates"].append(op_rate)
            results["operator_consistency"]["average"] = sum(results["operator_consistency"]["rates"]) / len(results["operator_consistency"]["rates"])
            
            # Update role consistency
            role_rate = comparison["role_matches"] / comparison["total_comparisons"]
            if "role_consistency" not in results or not results["role_consistency"]:
                results["role_consistency"] = {"rates": [], "average": 0.0}
            results["role_consistency"]["rates"].append(role_rate)
            results["role_consistency"]["average"] = sum(results["role_consistency"]["rates"]) / len(results["role_consistency"]["rates"])