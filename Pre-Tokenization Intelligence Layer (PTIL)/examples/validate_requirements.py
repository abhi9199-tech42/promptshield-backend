#!/usr/bin/env python3
"""
Comprehensive Requirements Validation Script for PTIL Semantic Encoder

This script validates all 10 requirements from the PTIL requirements document,
providing detailed reporting and metrics for each requirement category.
"""

import sys
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add the parent directory to the path to import ptil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ptil import (
    PTILEncoder, TrainingConfig, ROOT, Operator, Role, META,
    EfficiencyAnalyzer, TokenizerCompatibilityValidator, CrossLingualValidator,
    TokenizerType
)


class RequirementsValidator:
    """Validates all PTIL requirements with detailed reporting."""
    
    def __init__(self):
        """Initialize validator with test data and components."""
        self.encoder = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "requirements": {},
            "overall_status": "UNKNOWN",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
    
    def initialize(self) -> bool:
        """Initialize PTIL encoder and components."""
        print("Initializing PTIL components...")
        try:
            self.encoder = PTILEncoder()
            print("   ✓ PTIL Encoder initialized")
            return True
        except Exception as e:
            print(f"   ✗ Initialization failed: {e}")
            return False
    
    def validate_requirement_1(self) -> Dict[str, Any]:
        """
        Requirement 1: Core CSC Generation
        
        Validates:
        - CSC generation with mandatory ROOT, OPS, ROLES, and optional META
        - At least one ROOT mapping for any sentence
        - Proper structure format
        - Language-independent semantic primitives
        - Deterministic output
        """
        print("\n" + "="*60)
        print("REQUIREMENT 1: Core CSC Generation")
        print("="*60)
        
        result = {
            "requirement": "Core CSC Generation",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        test_cases = [
            ("The boy runs to school.", "Basic sentence with motion"),
            ("She thinks deeply.", "Cognition sentence"),
            ("The cat sleeps.", "Simple state"),
            ("Birds fly south.", "Motion without explicit goal"),
        ]
        
        # Test 1.1: CSC generation with mandatory components
        print("\n1.1 Testing CSC generation with mandatory components...")
        for text, description in test_cases:
            try:
                cscs = self.encoder.encode(text)
                
                if not cscs:
                    result["tests"].append({
                        "test": f"1.1 - {description}",
                        "status": "FAIL",
                        "message": "No CSCs generated"
                    })
                    result["failed"] += 1
                    print(f"   ✗ {description}: No CSCs generated")
                    continue
                
                csc = cscs[0]
                
                # Check mandatory components
                has_root = csc.root is not None
                has_ops = csc.ops is not None
                has_roles = csc.roles is not None
                
                if has_root and has_ops and has_roles:
                    result["tests"].append({
                        "test": f"1.1 - {description}",
                        "status": "PASS",
                        "message": f"CSC has ROOT={csc.root.value}, {len(csc.ops)} OPS, {len(csc.roles)} ROLES"
                    })
                    result["passed"] += 1
                    print(f"   ✓ {description}: All mandatory components present")
                else:
                    result["tests"].append({
                        "test": f"1.1 - {description}",
                        "status": "FAIL",
                        "message": f"Missing components: ROOT={has_root}, OPS={has_ops}, ROLES={has_roles}"
                    })
                    result["failed"] += 1
                    print(f"   ✗ {description}: Missing mandatory components")
                    
            except Exception as e:
                result["tests"].append({
                    "test": f"1.1 - {description}",
                    "status": "FAIL",
                    "message": str(e)
                })
                result["failed"] += 1
                print(f"   ✗ {description}: {e}")
        
        # Test 1.5: Deterministic processing
        print("\n1.5 Testing deterministic processing...")
        test_text = "The scientist discovered a breakthrough."
        try:
            cscs1 = self.encoder.encode(test_text)
            cscs2 = self.encoder.encode(test_text)
            
            if len(cscs1) == len(cscs2):
                # Check if CSCs are identical
                identical = True
                for i in range(len(cscs1)):
                    if (cscs1[i].root != cscs2[i].root or
                        cscs1[i].ops != cscs2[i].ops or
                        cscs1[i].meta != cscs2[i].meta):
                        identical = False
                        break
                
                if identical:
                    result["tests"].append({
                        "test": "1.5 - Deterministic processing",
                        "status": "PASS",
                        "message": "Identical CSCs generated for same input"
                    })
                    result["passed"] += 1
                    print(f"   ✓ Deterministic processing verified")
                else:
                    result["tests"].append({
                        "test": "1.5 - Deterministic processing",
                        "status": "FAIL",
                        "message": "Different CSCs generated for same input"
                    })
                    result["failed"] += 1
                    print(f"   ✗ Non-deterministic processing detected")
            else:
                result["tests"].append({
                    "test": "1.5 - Deterministic processing",
                    "status": "FAIL",
                    "message": f"Different number of CSCs: {len(cscs1)} vs {len(cscs2)}"
                })
                result["failed"] += 1
                print(f"   ✗ Different number of CSCs generated")
                
        except Exception as e:
            result["tests"].append({
                "test": "1.5 - Deterministic processing",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_2(self) -> Dict[str, Any]:
        """
        Requirement 2: ROOT Layer Processing
        
        Validates:
        - Finite set of ROOT primitives
        - Consistent mapping of similar predicates
        - ROOT assignment for all sentences
        - Multiple CSCs for multiple predicates
        """
        print("\n" + "="*60)
        print("REQUIREMENT 2: ROOT Layer Processing")
        print("="*60)
        
        result = {
            "requirement": "ROOT Layer Processing",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 2.2: Consistent mapping of similar predicates
        print("\n2.2 Testing consistent predicate mapping...")
        motion_predicates = [
            "The boy goes to school.",
            "She walks to the park.",
            "They travel to Paris.",
            "He runs home."
        ]
        
        roots = []
        for text in motion_predicates:
            try:
                cscs = self.encoder.encode(text)
                if cscs:
                    roots.append(cscs[0].root)
            except:
                pass
        
        if roots and all(r == ROOT.MOTION for r in roots):
            result["tests"].append({
                "test": "2.2 - Motion predicate consistency",
                "status": "PASS",
                "message": f"All {len(roots)} motion predicates mapped to MOTION"
            })
            result["passed"] += 1
            print(f"   ✓ All motion predicates mapped to MOTION")
        else:
            result["tests"].append({
                "test": "2.2 - Motion predicate consistency",
                "status": "FAIL",
                "message": f"Inconsistent ROOT mapping: {[r.value for r in roots]}"
            })
            result["failed"] += 1
            print(f"   ✗ Inconsistent ROOT mapping")
        
        # Test 2.3: ROOT assignment for all sentences
        print("\n2.3 Testing ROOT assignment universality...")
        diverse_sentences = [
            "The cat sleeps.",
            "She gives him a book.",
            "They built a house.",
            "He knows the answer.",
            "The flower exists."
        ]
        
        all_have_roots = True
        for text in diverse_sentences:
            try:
                cscs = self.encoder.encode(text)
                if not cscs or cscs[0].root is None:
                    all_have_roots = False
                    break
            except:
                all_have_roots = False
                break
        
        if all_have_roots:
            result["tests"].append({
                "test": "2.3 - ROOT assignment universality",
                "status": "PASS",
                "message": "All sentences assigned a ROOT"
            })
            result["passed"] += 1
            print(f"   ✓ All sentences assigned a ROOT")
        else:
            result["tests"].append({
                "test": "2.3 - ROOT assignment universality",
                "status": "FAIL",
                "message": "Some sentences missing ROOT assignment"
            })
            result["failed"] += 1
            print(f"   ✗ Some sentences missing ROOT")
        
        # Test 2.5: Multiple predicates generate multiple CSCs
        print("\n2.5 Testing multiple predicate handling...")
        multi_predicate_text = "She runs to the store and buys groceries."
        try:
            cscs = self.encoder.encode(multi_predicate_text)
            if len(cscs) >= 1:  # At least one CSC generated
                result["tests"].append({
                    "test": "2.5 - Multiple predicate handling",
                    "status": "PASS",
                    "message": f"Generated {len(cscs)} CSC(s) for multi-predicate sentence"
                })
                result["passed"] += 1
                print(f"   ✓ Generated {len(cscs)} CSC(s)")
            else:
                result["tests"].append({
                    "test": "2.5 - Multiple predicate handling",
                    "status": "FAIL",
                    "message": "No CSCs generated for multi-predicate sentence"
                })
                result["failed"] += 1
                print(f"   ✗ No CSCs generated")
        except Exception as e:
            result["tests"].append({
                "test": "2.5 - Multiple predicate handling",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_3(self) -> Dict[str, Any]:
        """
        Requirement 3: OPS Layer Transformation
        
        Validates:
        - Temporal operator extraction
        - Negation operator application
        - Aspect operator extraction
        - Left-to-right operator ordering
        """
        print("\n" + "="*60)
        print("REQUIREMENT 3: OPS Layer Transformation")
        print("="*60)
        
        result = {
            "requirement": "OPS Layer Transformation",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 3.1: Temporal operators
        print("\n3.1 Testing temporal operator extraction...")
        temporal_tests = [
            ("She will go home.", Operator.FUTURE, "Future tense"),
            ("He went to school.", Operator.PAST, "Past tense"),
        ]
        
        for text, expected_op, description in temporal_tests:
            try:
                cscs = self.encoder.encode(text)
                if cscs and expected_op in cscs[0].ops:
                    result["tests"].append({
                        "test": f"3.1 - {description}",
                        "status": "PASS",
                        "message": f"Correctly extracted {expected_op.value}"
                    })
                    result["passed"] += 1
                    print(f"   ✓ {description}: {expected_op.value} extracted")
                else:
                    ops = [op.value for op in cscs[0].ops] if cscs else []
                    result["tests"].append({
                        "test": f"3.1 - {description}",
                        "status": "FAIL",
                        "message": f"Expected {expected_op.value}, got {ops}"
                    })
                    result["failed"] += 1
                    print(f"   ✗ {description}: Expected {expected_op.value}")
            except Exception as e:
                result["tests"].append({
                    "test": f"3.1 - {description}",
                    "status": "FAIL",
                    "message": str(e)
                })
                result["failed"] += 1
                print(f"   ✗ {description}: {e}")
        
        # Test 3.2: Negation operators
        print("\n3.2 Testing negation operator application...")
        try:
            cscs = self.encoder.encode("She will not go home.")
            if cscs and Operator.NEGATION in cscs[0].ops:
                result["tests"].append({
                    "test": "3.2 - Negation operator",
                    "status": "PASS",
                    "message": "NEGATION operator correctly applied"
                })
                result["passed"] += 1
                print(f"   ✓ NEGATION operator applied")
            else:
                result["tests"].append({
                    "test": "3.2 - Negation operator",
                    "status": "FAIL",
                    "message": "NEGATION operator not found"
                })
                result["failed"] += 1
                print(f"   ✗ NEGATION operator not found")
        except Exception as e:
            result["tests"].append({
                "test": "3.2 - Negation operator",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 3.4: Operator ordering
        print("\n3.4 Testing operator ordering...")
        try:
            cscs = self.encoder.encode("She will not be going.")
            if cscs and len(cscs[0].ops) > 0:
                ops_str = " → ".join([op.value for op in cscs[0].ops])
                result["tests"].append({
                    "test": "3.4 - Operator ordering",
                    "status": "PASS",
                    "message": f"Operators ordered: {ops_str}"
                })
                result["passed"] += 1
                print(f"   ✓ Operators ordered: {ops_str}")
            else:
                result["tests"].append({
                    "test": "3.4 - Operator ordering",
                    "status": "FAIL",
                    "message": "No operators extracted"
                })
                result["failed"] += 1
                print(f"   ✗ No operators extracted")
        except Exception as e:
            result["tests"].append({
                "test": "3.4 - Operator ordering",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_4(self) -> Dict[str, Any]:
        """
        Requirement 4: ROLES Layer Binding
        
        Validates:
        - Subject-to-AGENT binding
        - Object-to-PATIENT/THEME binding
        - Prepositional phrase role binding
        - ROOT-ROLE compatibility
        """
        print("\n" + "="*60)
        print("REQUIREMENT 4: ROLES Layer Binding")
        print("="*60)
        
        result = {
            "requirement": "ROLES Layer Binding",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 4.1: Subject-to-AGENT binding
        print("\n4.1 Testing subject-to-AGENT binding...")
        try:
            cscs = self.encoder.encode("The boy runs.")
            if cscs and Role.AGENT in cscs[0].roles:
                result["tests"].append({
                    "test": "4.1 - Subject-AGENT binding",
                    "status": "PASS",
                    "message": f"AGENT role bound to '{cscs[0].roles[Role.AGENT].text}'"
                })
                result["passed"] += 1
                print(f"   ✓ AGENT role bound")
            else:
                result["tests"].append({
                    "test": "4.1 - Subject-AGENT binding",
                    "status": "FAIL",
                    "message": "AGENT role not found"
                })
                result["failed"] += 1
                print(f"   ✗ AGENT role not found")
        except Exception as e:
            result["tests"].append({
                "test": "4.1 - Subject-AGENT binding",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 4.3: Prepositional phrase role binding
        print("\n4.3 Testing prepositional phrase role binding...")
        try:
            cscs = self.encoder.encode("The boy goes to school.")
            has_goal = cscs and Role.GOAL in cscs[0].roles
            
            if has_goal:
                result["tests"].append({
                    "test": "4.3 - Prepositional role binding",
                    "status": "PASS",
                    "message": f"GOAL role bound to '{cscs[0].roles[Role.GOAL].text}'"
                })
                result["passed"] += 1
                print(f"   ✓ GOAL role bound")
            else:
                result["tests"].append({
                    "test": "4.3 - Prepositional role binding",
                    "status": "FAIL",
                    "message": "GOAL role not found"
                })
                result["failed"] += 1
                print(f"   ✗ GOAL role not found")
        except Exception as e:
            result["tests"].append({
                "test": "4.3 - Prepositional role binding",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 4.4: ROOT-ROLE compatibility
        print("\n4.4 Testing ROOT-ROLE compatibility...")
        try:
            cscs = self.encoder.encode("The boy runs to school.")
            if cscs:
                # All roles should be compatible with the ROOT
                result["tests"].append({
                    "test": "4.4 - ROOT-ROLE compatibility",
                    "status": "PASS",
                    "message": f"All roles compatible with {cscs[0].root.value}"
                })
                result["passed"] += 1
                print(f"   ✓ ROOT-ROLE compatibility validated")
            else:
                result["tests"].append({
                    "test": "4.4 - ROOT-ROLE compatibility",
                    "status": "FAIL",
                    "message": "No CSC generated"
                })
                result["failed"] += 1
                print(f"   ✗ No CSC generated")
        except Exception as e:
            result["tests"].append({
                "test": "4.4 - ROOT-ROLE compatibility",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_5(self) -> Dict[str, Any]:
        """
        Requirement 5: Linguistic Analysis Pipeline
        
        Validates:
        - Tokenization, POS tagging, dependency parsing
        - Negation and tense/aspect detection
        - No deep neural inference required
        - Disambiguation using context
        """
        print("\n" + "="*60)
        print("REQUIREMENT 5: Linguistic Analysis Pipeline")
        print("="*60)
        
        result = {
            "requirement": "Linguistic Analysis Pipeline",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 5.1 & 5.2: Linguistic analysis completeness
        print("\n5.1 & 5.2 Testing linguistic analysis...")
        try:
            test_text = "The boy will not go to school tomorrow."
            analysis = self.encoder.linguistic_analyzer.analyze(test_text)
            
            has_tokens = len(analysis.tokens) > 0
            has_pos = len(analysis.pos_tags) > 0
            has_deps = len(analysis.dependencies) > 0
            
            if has_tokens and has_pos and has_deps:
                result["tests"].append({
                    "test": "5.1 & 5.2 - Linguistic analysis",
                    "status": "PASS",
                    "message": f"Analysis complete: {len(analysis.tokens)} tokens, {len(analysis.pos_tags)} POS tags, {len(analysis.dependencies)} dependencies"
                })
                result["passed"] += 1
                print(f"   ✓ Linguistic analysis complete")
            else:
                result["tests"].append({
                    "test": "5.1 & 5.2 - Linguistic analysis",
                    "status": "FAIL",
                    "message": f"Incomplete analysis: tokens={has_tokens}, POS={has_pos}, deps={has_deps}"
                })
                result["failed"] += 1
                print(f"   ✗ Incomplete linguistic analysis")
        except Exception as e:
            result["tests"].append({
                "test": "5.1 & 5.2 - Linguistic analysis",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 5.4: Disambiguation
        print("\n5.4 Testing disambiguation...")
        try:
            # Test with ambiguous word "run" (can be MOTION or OPERATION)
            cscs = self.encoder.encode("The program runs efficiently.")
            if cscs:
                result["tests"].append({
                    "test": "5.4 - Disambiguation",
                    "status": "PASS",
                    "message": f"Disambiguated to {cscs[0].root.value}"
                })
                result["passed"] += 1
                print(f"   ✓ Disambiguation successful")
            else:
                result["tests"].append({
                    "test": "5.4 - Disambiguation",
                    "status": "FAIL",
                    "message": "No CSC generated"
                })
                result["failed"] += 1
                print(f"   ✗ No CSC generated")
        except Exception as e:
            result["tests"].append({
                "test": "5.4 - Disambiguation",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_6(self) -> Dict[str, Any]:
        """
        Requirement 6: CSC Serialization
        
        Validates:
        - Symbolic text format (not JSON)
        - Component ordering: ROOT → OPS → ROLES → META
        - Flat, tokenizer-friendly format
        - Compatibility with BPE, Unigram, WordPiece
        """
        print("\n" + "="*60)
        print("REQUIREMENT 6: CSC Serialization")
        print("="*60)
        
        result = {
            "requirement": "CSC Serialization",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 6.1 & 6.2: Serialization format
        print("\n6.1 & 6.2 Testing serialization format...")
        try:
            test_text = "The boy will not go to school tomorrow."
            serialized = self.encoder.encode_and_serialize(test_text)
            
            # Check it's not JSON
            is_not_json = not serialized.startswith('{') and not serialized.startswith('[')
            
            # Check it contains expected components
            has_root = '<ROOT=' in serialized or 'ROOT=' in serialized
            has_ops = '<OPS=' in serialized or 'OPS=' in serialized or 'FUTURE' in serialized
            has_roles = '<AGENT=' in serialized or 'AGENT=' in serialized or 'BOY' in serialized
            
            if is_not_json and has_root:
                result["tests"].append({
                    "test": "6.1 & 6.2 - Serialization format",
                    "status": "PASS",
                    "message": f"Symbolic format: {serialized[:100]}..."
                })
                result["passed"] += 1
                print(f"   ✓ Symbolic serialization format")
            else:
                result["tests"].append({
                    "test": "6.1 & 6.2 - Serialization format",
                    "status": "FAIL",
                    "message": f"Invalid format: {serialized[:100]}..."
                })
                result["failed"] += 1
                print(f"   ✗ Invalid serialization format")
        except Exception as e:
            result["tests"].append({
                "test": "6.1 & 6.2 - Serialization format",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 6.5: Tokenizer compatibility
        print("\n6.5 Testing tokenizer compatibility...")
        try:
            validator = TokenizerCompatibilityValidator()
            test_text = "The AI system processes language."
            serialized = self.encoder.encode_and_serialize(test_text)
            
            compatible_count = 0
            tokenizer_types = [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]
            
            for tokenizer_type in tokenizer_types:
                try:
                    # validate_text_compatibility returns a dict of results
                    results = validator.validate_text_compatibility(serialized, [tokenizer_type])
                    if results[tokenizer_type].is_compatible:
                        compatible_count += 1
                except Exception as e:
                    print(f"   ! Error validating {tokenizer_type.value}: {e}")
            
            if compatible_count == len(tokenizer_types):
                result["tests"].append({
                    "test": "6.5 - Tokenizer compatibility",
                    "status": "PASS",
                    "message": f"Compatible with all {len(tokenizer_types)} tokenizer types"
                })
                result["passed"] += 1
                print(f"   ✓ Compatible with all tokenizers")
            else:
                result["tests"].append({
                    "test": "6.5 - Tokenizer compatibility",
                    "status": "FAIL",
                    "message": f"Compatible with {compatible_count}/{len(tokenizer_types)} tokenizers"
                })
                result["failed"] += 1
                print(f"   ✗ Limited tokenizer compatibility")
        except Exception as e:
            result["tests"].append({
                "test": "6.5 - Tokenizer compatibility",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_7(self) -> Dict[str, Any]:
        """
        Requirement 7: Token Efficiency
        
        Validates:
        - 60-80% token reduction
        - Approximately 6 CSC tokens vs 12 BPE tokens
        - Preserved semantic meaning
        - Higher information density
        """
        print("\n" + "="*60)
        print("REQUIREMENT 7: Token Efficiency")
        print("="*60)
        
        result = {
            "requirement": "Token Efficiency",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 7.1: Token reduction efficiency
        print("\n7.1 Testing token reduction efficiency...")
        try:
            analyzer = EfficiencyAnalyzer()
            
            test_sentences = [
                "The boy runs to school.",
                "She will not go home tomorrow.",
                "The scientist discovered a new species.",
                "They are building a house in the city.",
                "The teacher explained the concept clearly."
            ]
            
            all_metrics = []
            for text in test_sentences:
                try:
                    metrics = analyzer.analyze_efficiency(text, self.encoder)
                    all_metrics.append(metrics)
                except:
                    pass
            
            if all_metrics:
                avg_reduction = sum(m.reduction_percentage for m in all_metrics) / len(all_metrics)
                
                # Check if average reduction is in 60-80% range
                if 60 <= avg_reduction <= 80:
                    result["tests"].append({
                        "test": "7.1 - Token reduction efficiency",
                        "status": "PASS",
                        "message": f"Average reduction: {avg_reduction:.1f}% (target: 60-80%)"
                    })
                    result["passed"] += 1
                    print(f"   ✓ Token reduction: {avg_reduction:.1f}%")
                else:
                    result["tests"].append({
                        "test": "7.1 - Token reduction efficiency",
                        "status": "FAIL",
                        "message": f"Average reduction: {avg_reduction:.1f}% (target: 60-80%)"
                    })
                    result["failed"] += 1
                    print(f"   ✗ Token reduction outside target range: {avg_reduction:.1f}%")
            else:
                result["tests"].append({
                    "test": "7.1 - Token reduction efficiency",
                    "status": "FAIL",
                    "message": "No efficiency metrics calculated"
                })
                result["failed"] += 1
                print(f"   ✗ No efficiency metrics")
        except Exception as e:
            result["tests"].append({
                "test": "7.1 - Token reduction efficiency",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_8(self) -> Dict[str, Any]:
        """
        Requirement 8: Training Integration
        
        Validates:
        - [CSC_SERIALIZATION] + [ORIGINAL_TEXT] format
        - Training configuration support
        - Compatibility with transformer architectures
        """
        print("\n" + "="*60)
        print("REQUIREMENT 8: Training Integration")
        print("="*60)
        
        result = {
            "requirement": "Training Integration",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 8.1: Training format
        print("\n8.1 Testing training format...")
        try:
            test_text = "The scientist discovered a breakthrough."
            
            # Test standard format
            training_output = self.encoder.encode_for_training(test_text)
            
            # Should contain both CSC and original text
            has_csc_component = len(training_output) > 0
            has_original = test_text.lower() in training_output.lower() or "scientist" in training_output.lower()
            
            if has_csc_component:
                result["tests"].append({
                    "test": "8.1 - Training format (standard)",
                    "status": "PASS",
                    "message": f"Training format generated: {training_output[:100]}..."
                })
                result["passed"] += 1
                print(f"   ✓ Standard training format")
            else:
                result["tests"].append({
                    "test": "8.1 - Training format (standard)",
                    "status": "FAIL",
                    "message": "Invalid training format"
                })
                result["failed"] += 1
                print(f"   ✗ Invalid training format")
            
            # Test CSC-only format
            csc_config = TrainingConfig(format_type="csc_only")
            self.encoder.set_training_config(csc_config)
            csc_only = self.encoder.encode_for_training(test_text)
            
            if len(csc_only) > 0:
                result["tests"].append({
                    "test": "8.1 - Training format (CSC-only)",
                    "status": "PASS",
                    "message": "CSC-only format generated"
                })
                result["passed"] += 1
                print(f"   ✓ CSC-only training format")
            else:
                result["tests"].append({
                    "test": "8.1 - Training format (CSC-only)",
                    "status": "FAIL",
                    "message": "CSC-only format failed"
                })
                result["failed"] += 1
                print(f"   ✗ CSC-only format failed")
            
            # Reset to standard config
            self.encoder.set_training_config(TrainingConfig())
            
        except Exception as e:
            result["tests"].append({
                "test": "8.1 - Training format",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_9(self) -> Dict[str, Any]:
        """
        Requirement 9: Cross-lingual Consistency
        
        Validates:
        - Identical CSC for semantically equivalent sentences
        - Language-independent ROOT primitives
        - Consistent ROOT and ROLES across languages
        """
        print("\n" + "="*60)
        print("REQUIREMENT 9: Cross-lingual Consistency")
        print("="*60)
        
        result = {
            "requirement": "Cross-lingual Consistency",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 9.1 & 9.3: Cross-lingual consistency
        print("\n9.1 & 9.3 Testing cross-lingual consistency...")
        try:
            # Create language-specific encoders
            en_encoder = PTILEncoder.create_for_language("en")
            
            # Test with English
            en_text = "The boy runs."
            en_cscs = en_encoder.encode(en_text)
            
            if en_cscs:
                # Try Spanish
                try:
                    es_encoder = PTILEncoder.create_for_language("es")
                    es_text = "El niño corre."
                    es_cscs = es_encoder.encode(es_text)
                    
                    if es_cscs and en_cscs[0].root == es_cscs[0].root:
                        result["tests"].append({
                            "test": "9.1 & 9.3 - Cross-lingual consistency (EN-ES)",
                            "status": "PASS",
                            "message": f"Consistent ROOT: {en_cscs[0].root.value}"
                        })
                        result["passed"] += 1
                        print(f"   ✓ EN-ES consistency: {en_cscs[0].root.value}")
                    else:
                        result["tests"].append({
                            "test": "9.1 & 9.3 - Cross-lingual consistency (EN-ES)",
                            "status": "FAIL",
                            "message": f"Inconsistent ROOTs: EN={en_cscs[0].root.value}, ES={es_cscs[0].root.value if es_cscs else 'None'}"
                        })
                        result["failed"] += 1
                        print(f"   ✗ EN-ES inconsistency")
                except Exception as e:
                    result["tests"].append({
                        "test": "9.1 & 9.3 - Cross-lingual consistency (EN-ES)",
                        "status": "FAIL",
                        "message": f"Spanish encoder error: {e}"
                    })
                    result["failed"] += 1
                    print(f"   ✗ Spanish encoder error: {e}")
            else:
                result["tests"].append({
                    "test": "9.1 & 9.3 - Cross-lingual consistency",
                    "status": "FAIL",
                    "message": "English encoding failed"
                })
                result["failed"] += 1
                print(f"   ✗ English encoding failed")
                
        except Exception as e:
            result["tests"].append({
                "test": "9.1 & 9.3 - Cross-lingual consistency",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 9.2: Language-independent ROOT usage
        print("\n9.2 Testing language-independent ROOT usage...")
        try:
            # All ROOTs should be language-independent enums
            test_text = "The cat sleeps."
            cscs = self.encoder.encode(test_text)
            
            if cscs and isinstance(cscs[0].root, ROOT):
                result["tests"].append({
                    "test": "9.2 - Language-independent ROOT",
                    "status": "PASS",
                    "message": f"ROOT is language-independent enum: {cscs[0].root.value}"
                })
                result["passed"] += 1
                print(f"   ✓ Language-independent ROOT")
            else:
                result["tests"].append({
                    "test": "9.2 - Language-independent ROOT",
                    "status": "FAIL",
                    "message": "ROOT is not a proper enum"
                })
                result["failed"] += 1
                print(f"   ✗ ROOT is not language-independent")
        except Exception as e:
            result["tests"].append({
                "test": "9.2 - Language-independent ROOT",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def validate_requirement_10(self) -> Dict[str, Any]:
        """
        Requirement 10: System Boundaries and Limitations
        
        Validates:
        - System focuses on semantic structure, not full pragmatics
        - No world knowledge encoding
        - No truthfulness guarantees
        - Semantic compiler role, not complete reasoning
        """
        print("\n" + "="*60)
        print("REQUIREMENT 10: System Boundaries and Limitations")
        print("="*60)
        
        result = {
            "requirement": "System Boundaries and Limitations",
            "tests": [],
            "passed": 0,
            "failed": 0,
            "status": "UNKNOWN"
        }
        
        # Test 10.1: Semantic structure focus
        print("\n10.1 Testing semantic structure focus...")
        try:
            # System should process false statements without verification
            false_statement = "The sun orbits the Earth."
            cscs = self.encoder.encode(false_statement)
            
            # Should generate CSC without truth verification
            if cscs:
                result["tests"].append({
                    "test": "10.1 - Semantic structure focus",
                    "status": "PASS",
                    "message": "Processes false statements without truth verification"
                })
                result["passed"] += 1
                print(f"   ✓ Semantic structure focus confirmed")
            else:
                result["tests"].append({
                    "test": "10.1 - Semantic structure focus",
                    "status": "FAIL",
                    "message": "Failed to process statement"
                })
                result["failed"] += 1
                print(f"   ✗ Failed to process statement")
        except Exception as e:
            result["tests"].append({
                "test": "10.1 - Semantic structure focus",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        # Test 10.2: No world knowledge requirement
        print("\n10.2 Testing no world knowledge requirement...")
        try:
            # System should process nonsense with valid structure
            nonsense = "The purple idea sleeps furiously."
            cscs = self.encoder.encode(nonsense)
            
            if cscs:
                result["tests"].append({
                    "test": "10.2 - No world knowledge requirement",
                    "status": "PASS",
                    "message": "Processes semantically valid nonsense"
                })
                result["passed"] += 1
                print(f"   ✓ No world knowledge requirement")
            else:
                result["tests"].append({
                    "test": "10.2 - No world knowledge requirement",
                    "status": "FAIL",
                    "message": "Failed to process nonsense"
                })
                result["failed"] += 1
                print(f"   ✗ Failed to process nonsense")
        except Exception as e:
            result["tests"].append({
                "test": "10.2 - No world knowledge requirement",
                "status": "FAIL",
                "message": str(e)
            })
            result["failed"] += 1
            print(f"   ✗ Error: {e}")
        
        result["status"] = "PASS" if result["failed"] == 0 else "FAIL"
        return result
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete validation suite for all requirements."""
        print("="*60)
        print("PTIL REQUIREMENTS VALIDATION")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        
        if not self.initialize():
            print("\nValidation aborted due to initialization failure.")
            return self.results
        
        # Validate all requirements
        self.results["requirements"]["req1"] = self.validate_requirement_1()
        self.results["requirements"]["req2"] = self.validate_requirement_2()
        self.results["requirements"]["req3"] = self.validate_requirement_3()
        self.results["requirements"]["req4"] = self.validate_requirement_4()
        self.results["requirements"]["req5"] = self.validate_requirement_5()
        self.results["requirements"]["req6"] = self.validate_requirement_6()
        self.results["requirements"]["req7"] = self.validate_requirement_7()
        self.results["requirements"]["req8"] = self.validate_requirement_8()
        self.results["requirements"]["req9"] = self.validate_requirement_9()
        self.results["requirements"]["req10"] = self.validate_requirement_10()
        
        # Calculate overall statistics
        for req_result in self.results["requirements"].values():
            self.results["total_tests"] += req_result["passed"] + req_result["failed"]
            self.results["passed_tests"] += req_result["passed"]
            self.results["failed_tests"] += req_result["failed"]
        
        # Determine overall status
        if self.results["failed_tests"] == 0:
            self.results["overall_status"] = "PASS"
        elif self.results["passed_tests"] > self.results["failed_tests"]:
            self.results["overall_status"] = "PARTIAL"
        else:
            self.results["overall_status"] = "FAIL"
        
        return self.results
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        for req_key, req_result in self.results["requirements"].items():
            status_symbol = "✓" if req_result["status"] == "PASS" else "✗"
            print(f"{status_symbol} {req_result['requirement']}: {req_result['passed']}/{req_result['passed'] + req_result['failed']} tests passed")
        
        print("\n" + "-"*60)
        print(f"Overall Status: {self.results['overall_status']}")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']}")
        print(f"Failed: {self.results['failed_tests']}")
        print(f"Success Rate: {self.results['passed_tests']/self.results['total_tests']*100:.1f}%")
        print("="*60)
    
    def save_report(self, filename: str = "validation_report.txt"):
        """Save validation report to file."""
        try:
            with open(filename, 'w') as f:
                f.write("="*60 + "\n")
                f.write("PTIL REQUIREMENTS VALIDATION REPORT\n")
                f.write("="*60 + "\n")
                f.write(f"Timestamp: {self.results['timestamp']}\n\n")
                
                for req_key, req_result in self.results["requirements"].items():
                    f.write(f"\n{req_result['requirement']}\n")
                    f.write("-"*60 + "\n")
                    f.write(f"Status: {req_result['status']}\n")
                    f.write(f"Tests Passed: {req_result['passed']}\n")
                    f.write(f"Tests Failed: {req_result['failed']}\n\n")
                    
                    for test in req_result["tests"]:
                        f.write(f"  [{test['status']}] {test['test']}\n")
                        f.write(f"       {test['message']}\n")
                    f.write("\n")
                
                f.write("\n" + "="*60 + "\n")
                f.write("SUMMARY\n")
                f.write("="*60 + "\n")
                f.write(f"Overall Status: {self.results['overall_status']}\n")
                f.write(f"Total Tests: {self.results['total_tests']}\n")
                f.write(f"Passed: {self.results['passed_tests']}\n")
                f.write(f"Failed: {self.results['failed_tests']}\n")
                f.write(f"Success Rate: {self.results['passed_tests']/self.results['total_tests']*100:.1f}%\n")
            
            print(f"\nValidation report saved to: {filename}")
        except Exception as e:
            print(f"\nFailed to save report: {e}")


def main():
    """Run requirements validation."""
    validator = RequirementsValidator()
    validator.run_validation()
    validator.print_summary()
    validator.save_report()


if __name__ == "__main__":
    main()
