# PTIL User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Core Concepts](#core-concepts)
4. [Usage Patterns](#usage-patterns)
5. [Serialization Formats](#serialization-formats)
6. [Training Integration](#training-integration)
7. [Cross-Lingual Processing](#cross-lingual-processing)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Introduction

The Pre-Tokenization Intelligence Layer (PTIL) is a deterministic semantic abstraction system that converts raw natural language text into compact, structured meaning representations called Compressed Semantic Code (CSC). PTIL reduces token count by 60-80%, makes semantic structure explicit, and maintains compatibility with existing LLM architectures.

### Key Benefits

- **Token Efficiency**: 60-80% reduction in token count
- **Semantic Clarity**: Explicit representation of meaning structure
- **Cross-Lingual Consistency**: Same meaning → same CSC across languages
- **Training Compatible**: Integrates with existing transformer architectures
- **Deterministic**: Identical input always produces identical output

### What PTIL Does

✓ Compresses meaning structure into semantic primitives  
✓ Extracts temporal, aspectual, and modal information  
✓ Binds entities to functional roles  
✓ Provides tokenizer-friendly serialization  

### What PTIL Doesn't Do

✗ Capture full pragmatics or conversational context  
✗ Encode world knowledge or common sense  
✗ Verify truthfulness of statements  
✗ Replace symbolic logic or reasoning systems  

## System Architecture

PTIL consists of six main components working in a pipeline:

```
Raw Text → Linguistic Analyzer → ROOT Mapper → OPS Extractor → ROLES Binder → META Detector → CSC Generator → Serializer → Output
```

### Component Overview

1. **Linguistic Analyzer**: Performs shallow NLP (tokenization, POS tagging, dependency parsing)
2. **ROOT Mapper**: Maps predicates to semantic primitives from finite ROOT set
3. **OPS Extractor**: Extracts ordered semantic operators (tense, aspect, polarity, modality)
4. **ROLES Binder**: Binds entities to semantic roles (AGENT, PATIENT, GOAL, etc.)
5. **META Detector**: Captures speech-level information (questions, commands, uncertainty)
6. **CSC Generator**: Combines components into structured CSC format
7. **Serializer**: Converts CSC to tokenizer-friendly symbolic text

## Core Concepts

### ROOT: Semantic Anchors

ROOT represents the type of event or state using a finite set of 300-800 semantic primitives.

**Common ROOT Types:**

- `MOTION`: Physical movement (go, walk, run, travel)
- `TRANSFER`: Transfer of possession (give, take, send, receive)
- `COMMUNICATION`: Information exchange (say, tell, ask, speak)
- `COGNITION`: Mental processes (think, know, believe, understand)
- `PERCEPTION`: Sensory experience (see, hear, feel, smell)
- `CREATION`: Bringing into existence (make, build, create, write)
- `DESTRUCTION`: Removing from existence (break, destroy, delete)
- `CHANGE`: State transformation (become, change, transform)
- `POSSESSION`: Having/owning (have, own, possess, belong)
- `EXISTENCE`: Being/existing (be, exist, live)

**Example:**
```python
encoder.encode("The boy runs.")  # ROOT: MOTION
encoder.encode("She thinks deeply.")  # ROOT: COGNITION
encoder.encode("He gave her a book.")  # ROOT: TRANSFER
```

### OPS: Semantic Operators

OPS are ordered operators encoding grammatical information in left-to-right sequence.

**Operator Categories:**

1. **Temporal**: PAST, PRESENT, FUTURE
2. **Aspect**: CONTINUOUS, COMPLETED, HABITUAL
3. **Polarity**: NEGATION, AFFIRMATION
4. **Modality**: POSSIBLE, NECESSARY, OBLIGATORY, PERMITTED
5. **Causation**: CAUSATIVE, SELF_INITIATED, FORCED
6. **Direction**: DIRECTION_IN, DIRECTION_OUT, TOWARD, AWAY

**Example:**
```python
encoder.encode("She will not go.")
# OPS: [FUTURE, NEGATION]
# Order matters: FUTURE(NEGATION(MOTION)) ≠ NEGATION(FUTURE(MOTION))
```

### ROLES: Semantic Role Bindings

ROLES map entities to their functional participation in the event, independent of word order.

**Role Types:**

- `AGENT`: Volitional actor performing the action
- `PATIENT`: Entity undergoing change or being affected
- `THEME`: Entity being moved or transferred
- `GOAL`: Destination or recipient
- `SOURCE`: Origin or starting point
- `INSTRUMENT`: Tool or means used
- `LOCATION`: Spatial location
- `TIME`: Temporal location

**Example:**
```python
encoder.encode("The boy runs to school.")
# ROLES: {AGENT: "boy", GOAL: "school"}

encoder.encode("To school runs the boy.")  # Same word order independence
# ROLES: {AGENT: "boy", GOAL: "school"}  # Identical!
```

### META: Context Modifiers

META captures speech-level and epistemic information (optional component).

**META Types:**

- `ASSERTIVE`: Declarative statement
- `QUESTION`: Interrogative
- `COMMAND`: Imperative
- `UNCERTAIN`: Epistemic uncertainty
- `EVIDENTIAL`: Evidence-based claim
- `EMOTIVE`: Emotional content
- `IRONIC`: Ironic or sarcastic

**Example:**
```python
encoder.encode("The cat sleeps.")  # META: ASSERTIVE
encoder.encode("Does the cat sleep?")  # META: QUESTION
encoder.encode("Sleep, cat!")  # META: COMMAND
encoder.encode("I think the cat might sleep.")  # META: UNCERTAIN
```

## Usage Patterns

### Basic Encoding

```python
from ptil import PTILEncoder

encoder = PTILEncoder()
cscs = encoder.encode("The scientist discovered a breakthrough.")

for csc in cscs:
    print(f"ROOT: {csc.root.value}")
    print(f"OPS: {[op.value for op in csc.ops]}")
    print(f"ROLES: {[(r.value, e.text) for r, e in csc.roles.items()]}")
    print(f"META: {csc.meta.value if csc.meta else None}")
```

### Batch Processing

```python
sentences = [
    "The cat sleeps.",
    "Birds fly south.",
    "She reads books."
]

results = []
for sentence in sentences:
    cscs = encoder.encode(sentence)
    serialized = encoder.encode_and_serialize(sentence, format="compact")
    results.append({
        "text": sentence,
        "cscs": cscs,
        "serialized": serialized
    })
```

### Error Handling

```python
try:
    cscs = encoder.encode(text)
    
    if not cscs:
        print("Warning: No CSCs generated")
    else:
        # Process CSCs
        serialized = encoder.encode_and_serialize(text)
        
except ValueError as e:
    print(f"Input error: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Component Introspection

```python
# Check component status
status = encoder.get_component_status()
for component, is_active in status.items():
    print(f"{component}: {'✓' if is_active else '✗'}")

# Access individual components
analysis = encoder.linguistic_analyzer.analyze(text)
root = encoder.root_mapper.map_predicate("run", "VERB", {})
ops = encoder.ops_extractor.extract_operators(analysis)
```

## Serialization Formats

PTIL supports three serialization formats for different use cases.

### Verbose Format

**Use Case**: Human-readable output, debugging, documentation

**Format**: `<ROOT=VALUE> <OPS=OP1|OP2> <ROLE=ENTITY> <META=VALUE>`

```python
serialized = encoder.encode_and_serialize(
    "The boy will not go to school.",
    format="verbose"
)
# Output: <ROOT=MOTION> <OPS=FUTURE|NEGATION> <AGENT=BOY> <GOAL=SCHOOL> <META=ASSERTIVE>
```

### Compact Format

**Use Case**: Balanced readability and efficiency

**Format**: `R:VALUE O:OP1|OP2 ROLE:ENTITY M:VALUE`

```python
serialized = encoder.encode_and_serialize(
    "The boy will not go to school.",
    format="compact"
)
# Output: R:MOTION O:FUTURE|NEGATION A:BOY G:SCHOOL M:ASSERTIVE
```

### Ultra-Compact Format

**Use Case**: Maximum token efficiency

**Format**: Minimal symbols and abbreviations

```python
serialized = encoder.encode_and_serialize(
    "The boy will not go to school.",
    format="ultra"
)
# Output: M|F|N|A:BOY|G:SCHOOL|AS
```

### Format Comparison

| Format | Readability | Token Count | Use Case |
|--------|-------------|-------------|----------|
| Verbose | High | Higher | Debugging, documentation |
| Compact | Medium | Medium | General purpose |
| Ultra | Low | Lowest | Maximum efficiency |

## Training Integration

PTIL provides flexible training integration formats for LLM fine-tuning.

### Standard Training Format

Combines CSC with original text: `[CSC_SERIALIZATION] + [ORIGINAL_TEXT]`

```python
from ptil import PTILEncoder, TrainingConfig

encoder = PTILEncoder()

config = TrainingConfig(
    format_type="standard",
    include_brackets=True,
    separator=" "
)
encoder.set_training_config(config)

training_output = encoder.encode_for_training(
    "The scientist discovered a breakthrough."
)
# Output: [CSC] <ROOT=COGNITION> ... [TEXT] The scientist discovered a breakthrough.
```

### CSC-Only Format

Only CSC serialization for pure semantic training:

```python
config = TrainingConfig(format_type="csc_only")
encoder.set_training_config(config)

training_output = encoder.encode_for_training(text)
# Output: <ROOT=COGNITION> <OPS=PAST> <AGENT=SCIENTIST> ...
```

### Mixed Format with Weights

Weighted combination for gradual semantic emphasis:

```python
config = TrainingConfig(
    format_type="mixed",
    csc_weight=2.0,      # CSC appears twice
    original_weight=1.0,  # Original text appears once
    separator=" | "
)
encoder.set_training_config(config)

training_output = encoder.encode_for_training(text)
# Output: [CSC] ... [CSC] ... [TEXT] ... (weighted repetition)
```

### Training Schedule Recommendations

**Early Epochs**: More original text, less CSC weight
```python
TrainingConfig(format_type="mixed", csc_weight=0.5, original_weight=2.0)
```

**Middle Epochs**: Balanced mix
```python
TrainingConfig(format_type="mixed", csc_weight=1.0, original_weight=1.0)
```

**Late Epochs**: More CSC emphasis
```python
TrainingConfig(format_type="mixed", csc_weight=2.0, original_weight=0.5)
```

**Fine-tuning Phase**: CSC-only
```python
TrainingConfig(format_type="csc_only")
```

## Cross-Lingual Processing

PTIL generates consistent CSC representations across languages for equivalent meanings.

### Creating Language-Specific Encoders

```python
from ptil import PTILEncoder

# Create encoders for different languages
en_encoder = PTILEncoder.create_for_language("en")
es_encoder = PTILEncoder.create_for_language("es")
fr_encoder = PTILEncoder.create_for_language("fr")
```

### Processing Equivalent Sentences

```python
# English
en_cscs = en_encoder.encode("The boy runs.")
print(f"EN ROOT: {en_cscs[0].root.value}")  # MOTION

# Spanish
es_cscs = es_encoder.encode("El niño corre.")
print(f"ES ROOT: {es_cscs[0].root.value}")  # MOTION

# French
fr_cscs = fr_encoder.encode("Le garçon court.")
print(f"FR ROOT: {fr_cscs[0].root.value}")  # MOTION

# All produce the same ROOT!
```

### Validating Cross-Lingual Consistency

```python
from ptil import CrossLingualValidator

validator = CrossLingualValidator()

is_consistent = validator.validate_consistency(
    en_cscs[0], es_cscs[0], "en", "es"
)
print(f"EN-ES Consistent: {is_consistent}")  # True
```

### Supported Languages

- English (en): `en_core_web_sm`
- Spanish (es): `es_core_news_sm`
- French (fr): `fr_core_news_sm`
- German (de): `de_core_news_sm`
- Italian (it): `it_core_news_sm`

Install language models:
```bash
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download fr_core_news_sm
```

## Performance Optimization

### Efficiency Analysis

```python
from ptil import EfficiencyAnalyzer

analyzer = EfficiencyAnalyzer()
metrics = analyzer.analyze_efficiency(text, encoder)

print(f"Original tokens: {metrics.original_tokens}")
print(f"CSC tokens: {metrics.csc_tokens}")
print(f"Reduction: {metrics.reduction_percentage:.1f}%")
print(f"Compression ratio: {metrics.compression_ratio:.2f}x")
```

### Batch Efficiency

```python
texts = ["sentence1", "sentence2", "sentence3", ...]
all_metrics = []

for text in texts:
    metrics = analyzer.analyze_efficiency(text, encoder)
    all_metrics.append(metrics)

# Aggregate metrics
aggregate = analyzer.calculate_aggregate_metrics(all_metrics)
print(f"Average reduction: {aggregate.reduction_percentage:.1f}%")
```

### Tokenizer Compatibility

```python
from ptil import TokenizerCompatibilityValidator, TokenizerType

validator = TokenizerCompatibilityValidator()
serialized = encoder.encode_and_serialize(text)

# Test with different tokenizers
for tokenizer_type in [TokenizerType.BPE, TokenizerType.UNIGRAM, TokenizerType.WORDPIECE]:
    result = validator.validate_compatibility(serialized, tokenizer_type)
    
    if result.is_compatible:
        print(f"✓ {tokenizer_type.value}: {result.token_count} tokens")
    else:
        print(f"✗ {tokenizer_type.value}: {result.error_message}")
```

### Performance Tips

1. **Reuse Encoder Instances**: Initialize once, use many times
2. **Batch Processing**: Process multiple sentences in loops
3. **Choose Appropriate Format**: Use ultra-compact for maximum efficiency
4. **Cache Results**: Store serialized CSCs for repeated use
5. **Profile Your Pipeline**: Use performance_benchmark.py to identify bottlenecks

## Troubleshooting

### Common Issues

#### Issue: "No CSCs generated"

**Cause**: Empty input, malformed text, or processing failure

**Solution**:
```python
# Check input
if not text or not text.strip():
    print("Error: Empty input")

# Check component status
status = encoder.get_component_status()
if not all(status.values()):
    print("Error: Some components not initialized")

# Try with simple text
test_cscs = encoder.encode("The cat sleeps.")
if not test_cscs:
    print("Error: Encoder not working properly")
```

#### Issue: "spaCy model not found"

**Cause**: Language model not installed

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

#### Issue: "Inconsistent cross-lingual results"

**Cause**: Language-specific idioms or structural differences

**Solution**:
- Use simpler, more literal translations
- Check that both sentences express the same core meaning
- Validate with CrossLingualValidator

#### Issue: "Low token reduction"

**Cause**: Very short sentences or already compact text

**Solution**:
- Token reduction is most effective on longer sentences
- Use ultra-compact format for maximum efficiency
- Check efficiency metrics to understand performance

### Debugging Strategies

1. **Enable Verbose Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Inspect Intermediate Steps**:
```python
analysis = encoder.linguistic_analyzer.analyze(text)
print(f"Tokens: {analysis.tokens}")
print(f"POS tags: {analysis.pos_tags}")
```

3. **Validate Components**:
```python
status = encoder.get_component_status()
for component, active in status.items():
    if not active:
        print(f"Inactive: {component}")
```

4. **Test with Known Examples**:
```python
# Should always work
test_cases = [
    "The cat sleeps.",
    "She runs fast.",
    "He gave her a book."
]

for test in test_cases:
    cscs = encoder.encode(test)
    assert cscs, f"Failed on: {test}"
```

## Best Practices

### Input Preparation

✓ **DO**: Use well-formed sentences with clear structure  
✓ **DO**: Normalize text (remove extra whitespace, fix encoding)  
✓ **DO**: Handle empty inputs gracefully  

✗ **DON'T**: Expect perfect results on fragments or malformed text  
✗ **DON'T**: Assume world knowledge or common sense reasoning  
✗ **DON'T**: Use for truth verification or fact-checking  

### Encoding Strategy

✓ **DO**: Choose serialization format based on use case  
✓ **DO**: Validate output before using in production  
✓ **DO**: Monitor efficiency metrics  

✗ **DON'T**: Mix serialization formats in same training batch  
✗ **DON'T**: Ignore failed encodings without investigation  
✗ **DON'T**: Assume 100% accuracy on all inputs  

### Training Integration

✓ **DO**: Start with mixed format, gradually increase CSC weight  
✓ **DO**: Monitor model fluency during training  
✓ **DO**: Include validation set with both CSC and original text  

✗ **DON'T**: Jump directly to CSC-only without gradual transition  
✗ **DON'T**: Ignore model performance degradation  
✗ **DON'T**: Use CSC for tasks requiring natural language output  

### Cross-Lingual Usage

✓ **DO**: Use literal translations for best consistency  
✓ **DO**: Validate consistency with CrossLingualValidator  
✓ **DO**: Install appropriate language models  

✗ **DON'T**: Expect perfect consistency on idiomatic expressions  
✗ **DON'T**: Mix languages in single encoder instance  
✗ **DON'T**: Assume all languages have same coverage  

### Production Deployment

✓ **DO**: Implement error handling and fallbacks  
✓ **DO**: Monitor performance metrics  
✓ **DO**: Cache encoder instances  
✓ **DO**: Validate inputs before processing  

✗ **DON'T**: Process untrusted input without validation  
✗ **DON'T**: Ignore performance degradation  
✗ **DON'T**: Deploy without testing on representative data  

## Summary

PTIL provides a powerful semantic abstraction layer that:

- Reduces token count by 60-80%
- Makes meaning structure explicit
- Maintains cross-lingual consistency
- Integrates with existing LLM architectures
- Operates deterministically and efficiently

For more information:
- [Quick Start Guide](QUICKSTART.md)
- [API Reference](API_REFERENCE.md)
- [Requirements Traceability](REQUIREMENTS_TRACEABILITY.md)
- Example scripts in `examples/` directory

Happy encoding! 🚀
