# Implementation Plan: PTIL Semantic Encoder

## Overview

This implementation plan converts the PTIL semantic encoder design into a series of incremental coding tasks. The system will be built in Python using established NLP libraries like spaCy for linguistic analysis and Hypothesis for property-based testing. Each task builds on previous work to create a complete semantic abstraction system.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create Python package structure with proper imports
  - Define core enums (ROOT, Operator, Role, META) and dataclasses (CSC, Entity, LinguisticAnalysis)
  - Set up testing framework with pytest and Hypothesis
  - Create ROOT-ROLE compatibility matrix
  - _Requirements: 1.1, 2.1, 4.4_

- [x] 1.1 Write unit tests for data model validation
  - Test enum value constraints and dataclass structure
  - Test ROOT-ROLE compatibility matrix lookups
  - _Requirements: 2.1, 4.4_

- [x] 2. Implement linguistic analyzer component
  - [x] 2.1 Create LinguisticAnalyzer class with spaCy integration
    - Implement tokenization, POS tagging, and dependency parsing
    - Add negation marker detection using spaCy's built-in capabilities
    - Extract tense and aspect cues from grammatical features
    - _Requirements: 5.1, 5.2_

  - [x] 2.2 Write property test for linguistic analysis completeness
    - **Property 15: Linguistic Analysis Completeness**
    - **Validates: Requirements 5.1, 5.2**

  - [x] 2.3 Write unit tests for linguistic analysis edge cases
    - Test empty input, malformed text, and unsupported characters
    - Test negation detection with various negation patterns
    - _Requirements: 5.1, 5.2_

- [x] 3. Implement ROOT mapper component
  - [x] 3.1 Create ROOTMapper class with predicate-to-ROOT mapping
    - Build comprehensive predicate dictionary mapping surface forms to ROOTs
    - Implement disambiguation using POS tags and dependency context
    - Handle unknown predicates with fallback to generic ROOTs
    - _Requirements: 1.4, 2.2, 5.4_

  - [x] 3.2 Write property test for ROOT assignment universality
    - **Property 2: ROOT Assignment Universality**
    - **Validates: Requirements 1.2, 2.3**

  - [x] 3.3 Write property test for predicate consistency
    - **Property 5: Predicate Consistency**
    - **Validates: Requirements 2.2**

  - [x] 3.4 Write property test for ROOT set constraint
    - **Property 3: ROOT Set Constraint**
    - **Validates: Requirements 1.4**

  - [x] 3.5 Write unit tests for disambiguation scenarios
    - Test ambiguous predicates with different POS contexts
    - Test fallback behavior for unknown predicates
    - _Requirements: 5.4_

- [x] 4. Implement OPS extractor component
  - [x] 4.1 Create OPSExtractor class for operator identification
    - Implement temporal operator extraction from tense markers
    - Add negation operator detection and application
    - Implement aspect operator extraction from aspectual markers
    - Ensure left-to-right operator ordering with non-commutativity
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 4.2 Write property test for temporal operator extraction
    - **Property 7: Temporal Operator Extraction**
    - **Validates: Requirements 3.1**

  - [x] 4.3 Write property test for negation operator application
    - **Property 8: Negation Operator Application**
    - **Validates: Requirements 3.2**

  - [x] 4.4 Write property test for aspect operator extraction
    - **Property 9: Aspect Operator Extraction**
    - **Validates: Requirements 3.3**

  - [x] 4.5 Write property test for operator non-commutativity
    - **Property 10: Operator Non-Commutativity**
    - **Validates: Requirements 3.4**

- [x] 5. Checkpoint - Ensure core analysis components work together
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement ROLES binder component
  - [x] 6.1 Create ROLESBinder class for semantic role assignment
    - Implement subject-to-AGENT binding for agentive sentences
    - Add direct object binding to PATIENT/THEME based on ROOT requirements
    - Implement prepositional phrase role binding (GOAL, SOURCE, LOCATION)
    - Add ROOT-ROLE compatibility validation
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 6.2 Write property test for subject-agent binding
    - **Property 11: Subject-Agent Binding**
    - **Validates: Requirements 4.1**

  - [x] 6.3 Write property test for object role binding
    - **Property 12: Object Role Binding**
    - **Validates: Requirements 4.2**

  - [x] 6.4 Write property test for prepositional role binding
    - **Property 13: Prepositional Role Binding**
    - **Validates: Requirements 4.3**

  - [x] 6.5 Write property test for ROOT-ROLE compatibility
    - **Property 14: ROOT-ROLE Compatibility**
    - **Validates: Requirements 4.4**

- [x] 7. Implement META detector component
  - [x] 7.1 Create METADetector class for speech act detection
    - Implement sentence type detection (ASSERTIVE, QUESTION, COMMAND)
    - Add epistemic marker detection (UNCERTAIN, EVIDENTIAL)
    - Handle optional META component in CSC structure
    - _Requirements: 1.1_

  - [x] 7.2 Write unit tests for META detection
    - Test various sentence types and epistemic markers
    - Test optional META handling in CSC generation
    - _Requirements: 1.1_

- [x] 8. Implement CSC generator and serializer
  - [x] 8.1 Create CSCGenerator class for structured CSC creation
    - Combine ROOT, OPS, ROLES, and optional META into CSC structure
    - Validate CSC completeness with mandatory components
    - Handle multiple predicate scenarios with multiple CSC instances
    - _Requirements: 1.1, 1.3, 2.5_

  - [x] 8.2 Create CSCSerializer class for tokenizer-friendly output
    - Implement symbolic text serialization (not JSON)
    - Ensure component ordering: ROOT → OPS → ROLES → META
    - Create flat, tokenizer-compatible format
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 8.3 Write property test for CSC structure completeness
    - **Property 1: CSC Structure Completeness**
    - **Validates: Requirements 1.1**

  - [x] 8.4 Write property test for multiple predicate handling
    - **Property 6: Multiple Predicate Handling**
    - **Validates: Requirements 2.5**

  - [x] 8.5 Write property test for serialization format validation
    - **Property 17: Serialization Format Validation**
    - **Validates: Requirements 6.1, 6.2**

  - [x] 8.6 Write unit test for specific serialization example
    - Test "The boy will not go to school tomorrow" serialization
    - _Requirements: 6.4_

- [x] 9. Implement main PTIL encoder pipeline
  - [x] 9.1 Create PTILEncoder class integrating all components
    - Wire together LinguisticAnalyzer, ROOTMapper, OPSExtractor, ROLESBinder, METADetector
    - Implement end-to-end text-to-CSC processing pipeline
    - Add error handling and graceful degradation
    - Ensure deterministic processing for identical inputs
    - _Requirements: 1.5, 5.1, 5.2, 5.4, 5.5_

  - [x] 9.2 Write property test for deterministic processing
    - **Property 4: Deterministic Processing**
    - **Validates: Requirements 1.5**

  - [x] 9.3 Write property test for disambiguation consistency
    - **Property 16: Disambiguation Consistency**
    - **Validates: Requirements 5.4**

  - [x] 9.4 Write integration tests for end-to-end pipeline
    - Test complete text processing with various sentence types
    - Test error handling and recovery scenarios
    - _Requirements: 1.5, 5.1, 5.2_

- [x] 10. Checkpoint - Ensure complete pipeline functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement efficiency and compatibility features
  - [x] 11.1 Add token reduction measurement and validation
    - Implement token counting for raw text vs CSC output
    - Validate 60-80% token reduction across diverse text samples
    - Add efficiency metrics and reporting
    - _Requirements: 7.1, 7.2_

  - [x] 11.2 Add tokenizer compatibility validation
    - Test CSC output with BPE, Unigram, and WordPiece tokenizers
    - Ensure serialized format processes without errors
    - _Requirements: 6.5_

  - [x] 11.3 Write property test for token reduction efficiency
    - **Property 19: Token Reduction Efficiency**
    - **Validates: Requirements 7.1**

  - [x] 11.4 Write property test for tokenizer compatibility
    - **Property 18: Tokenizer Compatibility**
    - **Validates: Requirements 6.5**

- [x] 12. Implement training integration features
  - [x] 12.1 Add training format output generation
    - Implement [CSC_SERIALIZATION] + [ORIGINAL_TEXT] format
    - Add configuration for different training modes
    - _Requirements: 8.1_

  - [x] 12.2 Write property test for training integration format
    - **Property 20: Training Integration Format**
    - **Validates: Requirements 8.1**

- [x] 13. Implement cross-lingual consistency features
  - [x] 13.1 Add multi-language support and validation
    - Extend linguistic analyzer for multiple languages using spaCy models
    - Implement cross-lingual CSC consistency validation
    - Ensure language-independent ROOT primitive usage
    - _Requirements: 9.1, 9.2, 9.5_

  - [x] 13.2 Write property test for cross-lingual consistency
    - **Property 21: Cross-Lingual Consistency**
    - **Validates: Requirements 9.1, 9.5**

  - [x] 13.3 Write property test for language-independent ROOT usage
    - **Property 22: Language-Independent ROOT Usage**
    - **Validates: Requirements 9.2**

  - [x] 13.4 Write unit test for specific cross-lingual example
    - Test "The boy runs" vs "El niño corre" consistency
    - _Requirements: 9.3_


- [x] 14. Final integration and validation
  - [x] 14.1 Create comprehensive example scripts and documentation
    - Build example usage scripts demonstrating key features
    - Add performance benchmarking and validation scripts
    - Create API documentation and usage examples
    - _Requirements: All requirements validation_

  - [x] 14.2 Write comprehensive integration tests
    - Test all properties together in realistic scenarios
    - Validate system boundaries and limitations
    - Test error handling across all components
    - _Requirements: All requirements validation_

- [x] 15. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- The implementation uses Python with spaCy for NLP and Hypothesis for property-based testing