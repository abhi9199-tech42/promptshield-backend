# PTIL API Reference

## Overview

The Pre-Tokenization Intelligence Layer (PTIL) provides a comprehensive API for converting natural language text into Compressed Semantic Code (CSC) representations. This document covers all public classes, methods, and data structures.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Data Models](#data-models)
3. [Configuration Classes](#configuration-classes)
4. [Analysis Classes](#analysis-classes)
5. [Validation Classes](#validation-classes)
6. [Usage Examples](#usage-examples)
7. [Error Handling](#error-handling)

## Core Classes

### PTILEncoder

The main encoder class that provides end-to-end text-to-CSC processing.

```python
class PTILEncoder:
    def __init__(self, model_name: str = "en_core_web_sm", language: Optional[str] = None)
    
    @classmethod
    def create_for_language(cls, language: str) -> 'PTILEncoder'
    
    def encode(self, text: str) -> List[CSC]
    def encode_and_serialize(self, text: str, format: str = "verbose") -> str
    def encode_for_training(self, text: str, config: Optional[TrainingConfig] = None) -> str
    
    def set_training_config(self, config: TrainingConfig) -> None
    def get_training_config(self) -> TrainingConfig
    def get_component_status(self) -> Dict[str, bool]
```

#### Constructor Parameters

- **model_name** (str, optional): spaCy model name for linguistic analysis. Default: "en_core_web_sm"
- **language** (str, optional): Language code for language-specific processing. Default: None

#### Methods

##### `encode(text: str) -> List[CSC]`

Converts raw text to CSC representations.

**Parameters:**
- `text` (str): Raw input text to encode

**Returns:**
- `List[CSC]`: List of compressed semantic code structures

**Raises:**
- `ValueError`: If input text is invalid
- `RuntimeError`: If encoding fails due to system errors

**Example:**
```python
encoder = PTILEncoder()
cscs = encoder.encode("The boy runs to school.")
print(f"Generated {len(cscs)} CSC(s)")
```

##### `encode_and_serialize(text: str, format: str = "verbose") -> str`

Converts raw text to serialized CSC format.

**Parameters:**
- `text` (str): Raw input text to encode
- `format` (str): Serialization format ("verbose", "compact", "ultra")

**Returns:**
- `str`: Serialized CSC in specified format

**Example:**
```python
encoder = PTILEncoder()
verbose = encoder.encode_and_serialize("Hello world.", format="verbose")
compact = encoder.encode_and_serialize("Hello world.", format="compact")
ultra = encoder.encode_and_serialize("Hello world.", format="ultra")
```

##### `encode_for_training(text: str, config: Optional[TrainingConfig] = None) -> str`

Converts raw text to training format with CSC and original text.

**Parameters:**
- `text` (str): Raw input text to encode
- `config` (TrainingConfig, optional): Training configuration

**Returns:**
- `str`: Training format string in [CSC_SERIALIZATION] + [ORIGINAL_TEXT] format

**Example:**
```python
encoder = PTILEncoder()
config = TrainingConfig(format_type="mixed", csc_weight=2.0)
training_output = encoder.encode_for_training("Hello world.", config)
```

##### `create_for_language(language: str) -> PTILEncoder` (classmethod)

Creates a PTIL encoder for a specific language.

**Parameters:**
- `language` (str): Language code (e.g., 'en', 'es', 'fr')

**Returns:**
- `PTILEncoder`: Encoder configured for the specified language

**Raises:**
- `ValueError`: If language is not supported

**Example:**
```python
spanish_encoder = PTILEncoder.create_for_language("es")
french_encoder = PTILEncoder.create_for_language("fr")
```

### Component Classes

#### LinguisticAnalyzer

Performs shallow linguistic analysis to extract semantic information.

```python
class LinguisticAnalyzer:
    def __init__(self, model_name: str = "en_core_web_sm", language: Optional[str] = None)
    def analyze(self, text: str) -> LinguisticAnalysis
    
    @classmethod
    def create_for_language(cls, language: str) -> 'LinguisticAnalyzer'
```

#### ROOTMapper

Maps predicates to semantic primitives from finite ROOT set.

```python
class ROOTMapper:
    def __init__(self)
    def map_predicate(self, predicate: str, pos_context: str, dependency_context: Dict) -> ROOT
    def is_predicate_known(self, predicate: str) -> bool
```

#### OPSExtractor

Extracts and orders semantic operators from grammatical markers.

```python
class OPSExtractor:
    def __init__(self)
    def extract_operators(self, analysis: LinguisticAnalysis) -> List[Operator]
```

#### ROLESBinder

Binds entities to semantic roles independent of word order.

```python
class ROLESBinder:
    def __init__(self, model_name: str = "en_core_web_sm")
    def bind_roles(self, analysis: LinguisticAnalysis, root: ROOT) -> Dict[Role, Entity]
```

#### METADetector

Captures speech-level and epistemic information.

```python
class METADetector:
    def __init__(self)
    def detect_meta(self, analysis: LinguisticAnalysis) -> Optional[META]
```

#### CSCGenerator

Combines components into structured CSC format.

```python
class CSCGenerator:
    def __init__(self)
    def generate_csc(self, root: ROOT, ops: List[Operator], 
                     roles: Dict[Role, Entity], meta: Optional[META]) -> CSC
```

#### CSCSerializer

Converts CSC to tokenizer-friendly symbolic text.

```python
class CSCSerializer:
    def __init__(self)
    def serialize(self, csc: CSC) -> str
    def serialize_multiple(self, cscs: List[CSC]) -> str
```

## Data Models

### Core Enums

#### ROOT

Semantic anchor representing the type of event or state.

```python
class ROOT(Enum):
    MOTION = "MOTION"
    TRANSFER = "TRANSFER"
    COMMUNICATION = "COMMUNICATION"
    COGNITION = "COGNITION"
    PERCEPTION = "PERCEPTION"
    CREATION = "CREATION"
    DESTRUCTION = "DESTRUCTION"
    CHANGE = "CHANGE"
    POSSESSION = "POSSESSION"
    INTENTION = "INTENTION"
    EXISTENCE = "EXISTENCE"
```

#### Operator

Ordered semantic operators encoding grammar, tense, polarity, modality, and direction.

```python
class Operator(Enum):
    # Temporal operators
    PAST = "PAST"
    PRESENT = "PRESENT"
    FUTURE = "FUTURE"
    
    # Aspect operators
    CONTINUOUS = "CONTINUOUS"
    COMPLETED = "COMPLETED"
    HABITUAL = "HABITUAL"
    
    # Polarity operators
    NEGATION = "NEGATION"
    AFFIRMATION = "AFFIRMATION"
    
    # Modality operators
    POSSIBLE = "POSSIBLE"
    NECESSARY = "NECESSARY"
    OBLIGATORY = "OBLIGATORY"
    PERMITTED = "PERMITTED"
    
    # Causation operators
    CAUSATIVE = "CAUSATIVE"
    SELF_INITIATED = "SELF_INITIATED"
    FORCED = "FORCED"
    
    # Direction operators
    DIRECTION_IN = "DIRECTION_IN"
    DIRECTION_OUT = "DIRECTION_OUT"
    TOWARD = "TOWARD"
    AWAY = "AWAY"
```

#### Role

Semantic role bindings that map entities to their functional participation.

```python
class Role(Enum):
    AGENT = "AGENT"
    PATIENT = "PATIENT"
    THEME = "THEME"
    GOAL = "GOAL"
    SOURCE = "SOURCE"
    INSTRUMENT = "INSTRUMENT"
    LOCATION = "LOCATION"
    TIME = "TIME"
```

#### META

Context modifiers capturing speech-level and epistemic information.

```python
class META(Enum):
    ASSERTIVE = "ASSERTIVE"
    QUESTION = "QUESTION"
    COMMAND = "COMMAND"
    UNCERTAIN = "UNCERTAIN"
    EVIDENTIAL = "EVIDENTIAL"
    EMOTIVE = "EMOTIVE"
    IRONIC = "IRONIC"
```

### Data Classes

#### CSC

Compressed Semantic Code - structured meaning representation.

```python
@dataclass
class CSC:
    root: ROOT
    ops: List[Operator]
    roles: Dict[Role, Entity]
    meta: Optional[META] = None
```

#### Entity

Represents an entity with original text and normalized form.

```python
@dataclass
class Entity:
    text: str
    normalized: str
```

#### LinguisticAnalysis

Results of shallow linguistic analysis.

```python
@dataclass
class LinguisticAnalysis:
    tokens: List[str]
    pos_tags: List[str]
    dependencies: List[Tuple[int, str, int]]  # (head_idx, relation, dependent_idx)
    negation_markers: List[int]  # Token indices with negation markers
    tense_markers: Dict[str, List[int]]  # Tense type -> token indices
    aspect_markers: Dict[str, List[int]]  # Aspect type -> token indices
```

## Configuration Classes

### TrainingConfig

Configuration for training format output generation.

```python
@dataclass
class TrainingConfig:
    format_type: str = "standard"  # "standard", "csc_only", "mixed"
    csc_weight: float = 1.0  # Weight for CSC in mixed format
    original_weight: float = 1.0  # Weight for original text in mixed format
    separator: str = " "  # Separator between CSC and original text
    include_brackets: bool = True  # Whether to include [CSC] and [TEXT] brackets
```

**Format Types:**
- `"standard"`: [CSC_SERIALIZATION] + [ORIGINAL_TEXT] format
- `"csc_only"`: Only CSC serialization
- `"mixed"`: Weighted combination of CSC and original text

## Analysis Classes

### EfficiencyAnalyzer

Analyzes token reduction efficiency of PTIL encoding.

```python
class EfficiencyAnalyzer:
    def __init__(self)
    def analyze_efficiency(self, text: str, encoder: PTILEncoder) -> EfficiencyMetrics
    def calculate_aggregate_metrics(self, metrics_list: List[EfficiencyMetrics]) -> EfficiencyMetrics
```

#### EfficiencyMetrics

```python
@dataclass
class EfficiencyMetrics:
    original_tokens: int
    csc_tokens: int
    reduction_percentage: float
    compression_ratio: float
    efficiency_score: float
```

### CrossLingualValidator

Validates consistency of CSC representations across languages.

```python
class CrossLingualValidator:
    def __init__(self)
    def validate_consistency(self, csc1: CSC, csc2: CSC, lang1: str, lang2: str) -> bool
    def validate_root_consistency(self, csc1: CSC, csc2: CSC) -> bool
    def validate_structure_consistency(self, csc1: CSC, csc2: CSC) -> bool
```

## Validation Classes

### TokenizerCompatibilityValidator

Validates compatibility with different tokenizer types.

```python
class TokenizerCompatibilityValidator:
    def __init__(self)
    def validate_compatibility(self, text: str, tokenizer_type: TokenizerType) -> CompatibilityResult
```

#### TokenizerType

```python
class TokenizerType(Enum):
    BPE = "BPE"
    UNIGRAM = "UNIGRAM"
    WORDPIECE = "WORDPIECE"
```

#### CompatibilityResult

```python
@dataclass
class CompatibilityResult:
    is_compatible: bool
    token_count: int
    error_message: Optional[str] = None
    tokenizer_type: Optional[TokenizerType] = None
```

## Usage Examples

### Basic Usage

```python
from ptil import PTILEncoder

# Initialize encoder
encoder = PTILEncoder()

# Encode text
text = "The boy runs to school."
cscs = encoder.encode(text)

# Print results
for csc in cscs:
    print(f"ROOT: {csc.root.value}")
    print(f"OPS: {[op.value for op in csc.ops]}")
    print(f"ROLES: {[(role.value, entity.text) for role, entity in csc.roles.items()]}")
    print(f"META: {csc.meta.value if csc.meta else None}")
```

### Serialization

```python
from ptil import PTILEncoder

encoder = PTILEncoder()
text = "She will not go home tomorrow."

# Different formats
verbose = encoder.encode_and_serialize(text, format="verbose")
compact = encoder.encode_and_serialize(text, format="compact")
ultra = encoder.encode_and_serialize(text, format="ultra")

print(f"Verbose: {verbose}")
print(f"Compact: {compact}")
print(f"Ultra: {ultra}")
```

### Training Integration

```python
from ptil import PTILEncoder, TrainingConfig

encoder = PTILEncoder()

# Configure for training
config = TrainingConfig(
    format_type="mixed",
    csc_weight=2.0,
    original_weight=1.0,
    include_brackets=True
)

encoder.set_training_config(config)

# Generate training format
text = "The scientist discovered a new species."
training_output = encoder.encode_for_training(text)
print(training_output)
```

### Cross-Lingual Processing

```python
from ptil import PTILEncoder

# Create language-specific encoders
en_encoder = PTILEncoder.create_for_language("en")
es_encoder = PTILEncoder.create_for_language("es")

# Process equivalent sentences
en_cscs = en_encoder.encode("The boy runs.")
es_cscs = es_encoder.encode("El niño corre.")

# Compare results
print(f"English ROOT: {en_cscs[0].root.value}")
print(f"Spanish ROOT: {es_cscs[0].root.value}")
```

### Efficiency Analysis

```python
from ptil import PTILEncoder, EfficiencyAnalyzer

encoder = PTILEncoder()
analyzer = EfficiencyAnalyzer()

text = "The quick brown fox jumps over the lazy dog."
metrics = analyzer.analyze_efficiency(text, encoder)

print(f"Original tokens: {metrics.original_tokens}")
print(f"CSC tokens: {metrics.csc_tokens}")
print(f"Reduction: {metrics.reduction_percentage:.1f}%")
print(f"Compression ratio: {metrics.compression_ratio:.2f}x")
```

### Tokenizer Compatibility

```python
from ptil import PTILEncoder, TokenizerCompatibilityValidator, TokenizerType

encoder = PTILEncoder()
validator = TokenizerCompatibilityValidator()

text = "The AI system processes language efficiently."
serialized = encoder.encode_and_serialize(text)

# Test compatibility
result = validator.validate_compatibility(serialized, TokenizerType.BPE)

if result.is_compatible:
    print(f"Compatible with BPE tokenizer ({result.token_count} tokens)")
else:
    print(f"Incompatible: {result.error_message}")
```

## Error Handling

### Common Exceptions

- **ValueError**: Invalid input parameters
- **RuntimeError**: System initialization or processing failures
- **ImportError**: Missing dependencies (e.g., spaCy models)

### Error Recovery

The PTIL system implements graceful degradation:

1. **Linguistic Analysis Failures**: Falls back to basic tokenization
2. **ROOT Mapping Failures**: Uses fallback ROOT (EXISTENCE)
3. **Component Failures**: Creates minimal valid CSC structures
4. **Serialization Failures**: Returns empty string with error logging

### Best Practices

1. **Always check return values**: Empty lists or strings indicate processing issues
2. **Use try-catch blocks**: Wrap PTIL calls in exception handling
3. **Check component status**: Use `get_component_status()` for diagnostics
4. **Validate inputs**: Ensure text is non-empty and properly formatted

```python
from ptil import PTILEncoder

encoder = PTILEncoder()

# Check component status
status = encoder.get_component_status()
if not all(status.values()):
    print("Warning: Some components are not initialized")

# Safe encoding with error handling
try:
    cscs = encoder.encode(text)
    if not cscs:
        print("Warning: No CSCs generated")
    else:
        # Process CSCs
        pass
except ValueError as e:
    print(f"Input error: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Constants and Compatibility

### ROOT-ROLE Compatibility Matrix

```python
from ptil import ROOT_ROLE_COMPATIBILITY

# Check valid roles for a ROOT
valid_roles = ROOT_ROLE_COMPATIBILITY[ROOT.MOTION]
print(f"Valid roles for MOTION: {[role.value for role in valid_roles]}")
```

### Version Information

```python
import ptil
print(f"PTIL Version: {ptil.__version__}")
```

This API reference provides comprehensive coverage of all PTIL functionality. For additional examples and advanced usage patterns, see the example scripts in the `examples/` directory.