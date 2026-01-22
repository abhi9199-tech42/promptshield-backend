# Requirements Document

## Introduction

The Pre-Tokenization Intelligence Layer (PTIL) is a deterministic semantic abstraction system that converts raw natural language text into compact, structured meaning representations called Compressed Semantic Code (CSC) before tokenization and model ingestion. The system aims to reduce token count, make semantic structure explicit, improve reasoning efficiency, and maintain compatibility with existing LLM architectures.

## Glossary

- **PTIL**: Pre-Tokenization Intelligence Layer - the complete semantic abstraction system
- **CSC**: Compressed Semantic Code - structured meaning representation output by PTIL
- **ROOT**: Semantic anchor representing the type of event or state (finite set of 300-800 primitives)
- **OPS**: Ordered semantic operators encoding grammar, tense, polarity, modality, and direction
- **ROLES**: Semantic role bindings that map entities to their functional participation
- **META**: Context modifiers capturing speech-level and epistemic information
- **Encoder**: The PTIL component that converts raw text to CSC
- **Serializer**: Component that converts CSC to tokenizer-friendly symbolic text

## Requirements

### Requirement 1: Core CSC Generation

**User Story:** As an AI researcher, I want to convert natural language text into structured semantic representations, so that I can reduce token count and make meaning explicit for model training.

#### Acceptance Criteria

1. WHEN raw text is provided to the PTIL Encoder, THE System SHALL generate a CSC with mandatory ROOT, OPS, ROLES, and optional META components
2. WHEN processing any sentence, THE System SHALL map it to at least one ROOT from the finite semantic primitive set
3. WHEN generating CSC, THE System SHALL ensure all four components (ROOT, OPS, ROLES, META) follow the specified structure format
4. WHEN creating ROOT mappings, THE System SHALL use only language-independent semantic primitives from the predefined set
5. THE System SHALL maintain deterministic output for identical input text

### Requirement 2: ROOT Layer Processing

**User Story:** As a system architect, I want semantic anchors to represent event types consistently, so that meaning is captured independently of surface language variations.

#### Acceptance Criteria

1. THE System SHALL maintain a finite set of 300-800 mutually distinct ROOT primitives
2. WHEN encountering predicates like "go", "walk", "travel", THE System SHALL map them to the same ROOT (MOTION)
3. WHEN processing any sentence, THE System SHALL identify and assign at least one ROOT from the predefined set
4. THE System SHALL use verb-centric ROOTs but include state roots when appropriate
5. WHEN multiple predicates exist, THE System SHALL generate multiple CSC instances as needed

### Requirement 3: OPS Layer Transformation

**User Story:** As a linguist, I want grammatical information encoded as ordered operators, so that tense, aspect, polarity, and modality are explicitly represented.

#### Acceptance Criteria

1. WHEN detecting temporal markers like "will" or "did", THE System SHALL apply appropriate temporal operators (FUTURE, PAST)
2. WHEN processing negation markers like "not", THE System SHALL apply NEGATION operator
3. WHEN encountering aspectual markers, THE System SHALL apply appropriate aspect operators (CONTINUOUS, COMPLETED, HABITUAL)
4. THE System SHALL apply OPS in left-to-right order maintaining non-commutativity
5. WHEN combining operators, THE System SHALL ensure NEGATION(FUTURE(MOTION)) differs from FUTURE(NEGATION(MOTION))

### Requirement 4: ROLES Layer Binding

**User Story:** As a semantic analyst, I want entities bound to their functional roles, so that meaning is independent of word order and syntax.

#### Acceptance Criteria

1. WHEN processing subjects, THE System SHALL bind them to AGENT role where appropriate
2. WHEN processing direct objects, THE System SHALL bind them to PATIENT or THEME roles based on ROOT requirements
3. WHEN encountering prepositional phrases, THE System SHALL bind them to appropriate roles (GOAL, SOURCE, LOCATION)
4. THE System SHALL validate that assigned ROLES are compatible with the identified ROOT
5. WHEN ROOT is MOTION, THE System SHALL allow AGENT, THEME, SOURCE, GOAL roles

### Requirement 5: Linguistic Analysis Pipeline

**User Story:** As a developer, I want shallow linguistic analysis to extract semantic information, so that CSC generation is efficient and doesn't require deep neural inference.

#### Acceptance Criteria

1. WHEN processing input text, THE System SHALL perform tokenization, POS tagging, and dependency parsing
2. WHEN analyzing text, THE System SHALL detect negation markers and tense/aspect cues
3. THE System SHALL complete linguistic analysis without requiring deep neural inference
4. WHEN ambiguity exists, THE System SHALL resolve ROOT mapping using POS tags and dependency context
5. THE System SHALL extract grammatical markers for operator identification

### Requirement 6: CSC Serialization

**User Story:** As a model trainer, I want CSC serialized as tokenizer-friendly symbolic text, so that it can be processed by standard tokenizers and transformers.

#### Acceptance Criteria

1. WHEN serializing CSC, THE System SHALL output symbolic text format, not JSON
2. THE System SHALL order serialized components as ROOT → OPS → ROLES → META
3. WHEN generating serialized output, THE System SHALL use flat, tokenizer-friendly format
4. THE System SHALL serialize "The boy will not go to school tomorrow" as "<ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <TIME=TOMORROW> <META=ASSERTIVE>"
5. THE System SHALL ensure serialized format is compatible with BPE, Unigram, and WordPiece tokenizers

### Requirement 7: Token Efficiency

**User Story:** As an AI trainer, I want significant token reduction, so that I can reduce context window pressure and improve training efficiency.

#### Acceptance Criteria

1. WHEN processing typical text, THE System SHALL achieve 60-80% token reduction compared to raw text
2. WHEN comparing token counts, THE System SHALL demonstrate CSC uses approximately 6 tokens versus 12 BPE tokens for equivalent meaning
3. THE System SHALL preserve semantic meaning while reducing token entropy
4. WHEN generating CSC, THE System SHALL maintain information density higher than raw text
5. THE System SHALL enable more efficient context window utilization

### Requirement 8: Training Integration

**User Story:** As a model architect, I want PTIL to integrate with existing training pipelines, so that I can enhance models without replacing core architectures.

#### Acceptance Criteria

1. WHEN integrating with training, THE System SHALL provide input format as [CSC_SERIALIZATION] + [ORIGINAL_TEXT]
2. THE System SHALL support training schedules with early epochs using more raw text and later epochs using higher CSC weight
3. WHEN used in training, THE System SHALL remain compatible with existing transformer architectures
4. THE System SHALL enable optional CSC-only fine-tuning phases
5. THE System SHALL preserve model fluency while enforcing semantic structure

### Requirement 9: Cross-lingual Consistency

**User Story:** As a multilingual AI researcher, I want the same semantic content to produce identical CSC across languages, so that I can achieve better cross-lingual alignment.

#### Acceptance Criteria

1. WHEN processing semantically equivalent sentences in different languages, THE System SHALL generate identical CSC representations
2. THE System SHALL use language-independent ROOT primitives across all supported languages
3. WHEN processing "The boy runs" and "El niño corre", THE System SHALL produce the same ROOT and ROLES bindings
4. THE System SHALL enable shared semantic latent space across languages
5. THE System SHALL maintain semantic consistency regardless of surface language variations

### Requirement 10: System Boundaries and Limitations

**User Story:** As a system user, I want clear understanding of what PTIL does and doesn't do, so that I have appropriate expectations for system capabilities.

#### Acceptance Criteria

1. THE System SHALL compress meaning structure without capturing full pragmatics
2. THE System SHALL not encode world knowledge or replace symbolic logic systems
3. THE System SHALL not guarantee truthfulness of processed content
4. WHEN processing text, THE System SHALL focus on semantic structure compression rather than reality verification
5. THE System SHALL operate as a semantic compiler for neural models, not a complete reasoning system