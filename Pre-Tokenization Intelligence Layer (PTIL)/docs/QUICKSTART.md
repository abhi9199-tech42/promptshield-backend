# PTIL Quick Start Guide

Welcome to the Pre-Tokenization Intelligence Layer (PTIL)! This guide will help you get started with converting natural language text into Compressed Semantic Code (CSC) representations.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd "c:\Users\kriti\OneDrive\Pre-Tokenization Intelligence Layer (PTIL)"
pip install -r requirements.txt
```

### Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

For other languages:
```bash
python -m spacy download es_core_news_sm  # Spanish
python -m spacy download fr_core_news_sm  # French
```

## Your First Encoding

Create a simple Python script to encode your first sentence:

```python
from ptil import PTILEncoder

# Initialize the encoder
encoder = PTILEncoder()

# Encode a sentence
text = "The boy runs to school."
cscs = encoder.encode(text)

# Print the results
for csc in cscs:
    print(f"ROOT: {csc.root.value}")
    print(f"OPS: {[op.value for op in csc.ops]}")
    print(f"ROLES: {[(role.value, entity.text) for role, entity in csc.roles.items()]}")
    print(f"META: {csc.meta.value if csc.meta else None}")
```

**Output:**
```
ROOT: MOTION
OPS: ['PRESENT']
ROLES: [('AGENT', 'boy'), ('GOAL', 'school')]
META: ASSERTIVE
```

## Serialization Formats

PTIL supports three serialization formats:

### Verbose Format (Default)

```python
serialized = encoder.encode_and_serialize(text, format="verbose")
print(serialized)
# Output: <ROOT=MOTION> <OPS=PRESENT> <AGENT=BOY> <GOAL=SCHOOL> <META=ASSERTIVE>
```

### Compact Format

```python
serialized = encoder.encode_and_serialize(text, format="compact")
print(serialized)
# Output: R:MOTION O:PRESENT A:BOY G:SCHOOL M:ASSERTIVE
```

### Ultra-Compact Format

```python
serialized = encoder.encode_and_serialize(text, format="ultra")
print(serialized)
# Output: M|P|A:BOY|G:SCHOOL|AS
```

## Common Use Cases

### 1. Token Reduction for LLM Training
    
> *Note: Token reduction is most effective for semantic-dense text (n >= 5 tokens). Short utterances may experience representation overhead.*
    
```python
from ptil import PTILEncoder, EfficiencyAnalyzer

encoder = PTILEncoder()
analyzer = EfficiencyAnalyzer()

text = "The scientist discovered a groundbreaking new theory."
metrics = analyzer.analyze_efficiency(text, encoder)

print(f"Original tokens: {metrics.original_tokens}")
print(f"CSC tokens: {metrics.csc_tokens}")
print(f"Reduction: {metrics.reduction_percentage:.1f}%")
```

### 2. Training Data Preparation

```python
from ptil import PTILEncoder, TrainingConfig

encoder = PTILEncoder()

# Configure for training
config = TrainingConfig(
    format_type="standard",  # [CSC] + [ORIGINAL_TEXT]
    include_brackets=True
)
encoder.set_training_config(config)

# Generate training format
text = "The AI system processes natural language efficiently."
training_output = encoder.encode_for_training(text)
print(training_output)
```

### 3. Cross-Lingual Processing

```python
from ptil import PTILEncoder

# Create language-specific encoders
en_encoder = PTILEncoder.create_for_language("en")
es_encoder = PTILEncoder.create_for_language("es")

# Process equivalent sentences
en_cscs = en_encoder.encode("The boy runs.")
es_cscs = es_encoder.encode("El niño corre.")

# Both should have the same ROOT
print(f"English ROOT: {en_cscs[0].root.value}")
print(f"Spanish ROOT: {es_cscs[0].root.value}")
# Both output: MOTION
```

## Running Example Scripts

PTIL includes several example scripts to demonstrate different features:

### Basic Usage

```bash
python examples/basic_usage.py
```

Shows fundamental encoder usage, serialization formats, and training configurations.

### Advanced Features

```bash
python examples/advanced_features.py
```

Demonstrates error handling, batch processing, efficiency analysis, and tokenizer compatibility.

### Cross-Lingual Demo

```bash
python examples/cross_lingual_demo.py
```

Shows cross-lingual consistency across English, Spanish, and French.

### Performance Benchmark

```bash
python examples/performance_benchmark.py
```

Comprehensive performance benchmarking including speed, efficiency, and memory usage.

### Requirements Validation

```bash
python examples/validate_requirements.py
```

Validates all 10 PTIL requirements with detailed reporting.

## Testing

Run the test suite to verify your installation:

```bash
pytest tests/ -v
```

Run specific test categories:

```bash
# Test core components
pytest tests/test_encoder.py -v

# Test properties
pytest tests/test_encoder_properties.py -v

# Test efficiency
pytest tests/test_efficiency_properties.py -v
```

## Next Steps

- **Read the [User Guide](USER_GUIDE.md)** for comprehensive documentation
- **Explore the [API Reference](API_REFERENCE.md)** for detailed API documentation
- **Check the [Requirements Traceability](REQUIREMENTS_TRACEABILITY.md)** to understand validation coverage
- **Review example scripts** in the `examples/` directory

## Getting Help

If you encounter issues:

1. Check the **User Guide** troubleshooting section
2. Review the **API Reference** for correct usage
3. Run the validation script to check your setup:
   ```bash
   python examples/validate_requirements.py
   ```
4. Examine example scripts for working code patterns

## Key Concepts

- **ROOT**: Semantic anchor representing event/state type (e.g., MOTION, COGNITION)
- **OPS**: Ordered operators encoding tense, aspect, polarity, modality
- **ROLES**: Semantic role bindings (AGENT, PATIENT, GOAL, etc.)
- **META**: Context modifiers (ASSERTIVE, QUESTION, COMMAND, etc.)
- **CSC**: Compressed Semantic Code - the complete structured representation

### Efficiency Targets
- **Scientific/Technical**: 80-85% reduction
- **Long Declarative**: 50-70% reduction
- **Short Utterances**: n < 5 tokens excluded (overhead dominance)

## Quick Reference

```python
from ptil import PTILEncoder, TrainingConfig, EfficiencyAnalyzer

# Initialize
encoder = PTILEncoder()

# Basic encoding
cscs = encoder.encode("Your text here")

# Serialization
serialized = encoder.encode_and_serialize("Your text", format="compact")

# Training format
training_output = encoder.encode_for_training("Your text")

# Efficiency analysis
analyzer = EfficiencyAnalyzer()
metrics = analyzer.analyze_efficiency("Your text", encoder)

# Multi-language
es_encoder = PTILEncoder.create_for_language("es")
```

Happy encoding! 🚀
