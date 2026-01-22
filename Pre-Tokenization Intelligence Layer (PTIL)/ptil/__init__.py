"""
Pre-Tokenization Intelligence Layer (PTIL) - Semantic Encoder

A deterministic semantic abstraction system that converts raw natural language text 
into compact, structured meaning representations called Compressed Semantic Code (CSC).
"""

from .models import ROOT, Operator, Role, META, CSC, Entity, LinguisticAnalysis
from .compatibility import ROOT_ROLE_COMPATIBILITY
from .linguistic_analyzer import LinguisticAnalyzer
from .root_mapper import ROOTMapper
from .ops_extractor import OPSExtractor
from .roles_binder import ROLESBinder
from .meta_detector import METADetector
from .csc_generator import CSCGenerator
from .csc_serializer import CSCSerializer
from .encoder import PTILEncoder, TrainingConfig
from .efficiency_analyzer import EfficiencyAnalyzer, EfficiencyMetrics
from .tokenizer_compatibility import TokenizerCompatibilityValidator, CompatibilityResult, TokenizerType
from .compact_serializer import CompactCSCSerializer
from .ultra_compact_serializer import UltraCompactCSCSerializer
from .cross_lingual_validator import CrossLingualValidator

__version__ = "0.1.0"
__all__ = [
    "ROOT",
    "Operator", 
    "Role",
    "META",
    "CSC",
    "Entity",
    "LinguisticAnalysis",
    "ROOT_ROLE_COMPATIBILITY",
    "LinguisticAnalyzer",
    "ROOTMapper",
    "OPSExtractor",
    "ROLESBinder",
    "METADetector",
    "CSCGenerator",
    "CSCSerializer",
    "PTILEncoder",
    "TrainingConfig",
    "EfficiencyAnalyzer",
    "EfficiencyMetrics",
    "TokenizerCompatibilityValidator",
    "CompatibilityResult",
    "TokenizerType",
    "CompactCSCSerializer",
    "UltraCompactCSCSerializer",
    "CrossLingualValidator"
]