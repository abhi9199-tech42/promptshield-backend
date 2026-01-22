"""
PTIL Encoder - Main pipeline for semantic encoding.

This module provides the PTILEncoder class that integrates all PTIL components
into a complete end-to-end text-to-CSC processing pipeline with error handling
and graceful degradation.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from .models import CSC, ROOT, LinguisticAnalysis


@dataclass
class TrainingConfig:
    """Configuration for training format output generation."""
    format_type: str = "standard"  # "standard", "csc_only", "mixed"
    csc_weight: float = 1.0  # Weight for CSC in mixed format
    original_weight: float = 1.0  # Weight for original text in mixed format
    separator: str = " "  # Separator between CSC and original text
    include_brackets: bool = True  # Whether to include [CSC] and [TEXT] brackets
from .linguistic_analyzer import LinguisticAnalyzer
from .root_mapper import ROOTMapper
from .ops_extractor import OPSExtractor
from .roles_binder import ROLESBinder
from .meta_detector import METADetector
from .csc_generator import CSCGenerator
from .csc_serializer import CSCSerializer
from .compact_serializer import CompactCSCSerializer
from .ultra_compact_serializer import UltraCompactCSCSerializer


class PTILEncoder:
    """
    Main PTIL encoder pipeline integrating all semantic processing components.
    
    Provides end-to-end text-to-CSC processing with deterministic output,
    error handling, and graceful degradation for robust semantic encoding.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm", language: Optional[str] = None):
        """
        Initialize the PTIL encoder with all component instances.
        
        Args:
            model_name: spaCy model name for linguistic analysis
            language: Language code for language-specific processing
        """
        self.logger = logging.getLogger(__name__)
        self.language = language
        
        # Default training configuration
        self.training_config = TrainingConfig()
        
        try:
            # Initialize all components
            self.linguistic_analyzer = LinguisticAnalyzer(model_name, language)
            self.root_mapper = ROOTMapper()
            self.ops_extractor = OPSExtractor()
            self.roles_binder = ROLESBinder(model_name)
            self.meta_detector = METADetector()
            self.csc_generator = CSCGenerator()
            self.csc_serializer = CSCSerializer()
            self.compact_serializer = CompactCSCSerializer()
            self.ultra_compact_serializer = UltraCompactCSCSerializer()
            
            self.logger.info(f"PTILEncoder initialized with model: {model_name}, language: {language}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PTILEncoder: {e}")
            raise RuntimeError(f"PTILEncoder initialization failed: {e}")
    
    @classmethod
    def create_for_language(cls, language: str) -> 'PTILEncoder':
        """
        Create a PTIL encoder for a specific language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            PTILEncoder: Encoder configured for the specified language
            
        Raises:
            ValueError: If language is not supported
        """
        analyzer = LinguisticAnalyzer.create_for_language(language)
        return cls(model_name=analyzer.model_name, language=language)
    
    def encode(self, text: str) -> List[CSC]:
        """
        Convert raw text to CSC representations.
        
        Args:
            text: Raw input text to encode
            
        Returns:
            List[CSC]: List of compressed semantic code structures
            
        Raises:
            ValueError: If input text is invalid
            RuntimeError: If encoding fails due to system errors
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        if not text or not text.strip():
            self.logger.warning("Empty input text provided")
            return []
        
        try:
            # Step 1: Linguistic Analysis
            analysis = self._perform_linguistic_analysis(text)
            if not analysis.tokens:
                self.logger.warning("No tokens found in linguistic analysis")
                return []
            
            # Step 2: Identify predicates and generate CSCs
            cscs = self._generate_cscs_from_analysis(text, analysis)
            
            self.logger.debug(f"Generated {len(cscs)} CSC(s) for input: {text[:50]}...")
            return cscs
            
        except Exception as e:
            self.logger.error(f"Encoding failed for text '{text[:50]}...': {e}")
            # Graceful degradation: return minimal CSC
            return self._create_fallback_csc(text)
    
    def encode_and_serialize(self, text: str, format: str = "verbose") -> str:
        """
        Convert raw text to serialized CSC format.
        
        Args:
            text: Raw input text to encode
            format: Serialization format ("verbose", "compact", "ultra")
            
        Returns:
            str: Serialized CSC in specified format
        """
        try:
            cscs = self.encode(text)
            if not cscs:
                return ""
            
            if format == "ultra":
                return self.ultra_compact_serializer.serialize_multiple(cscs)
            elif format == "compact":
                return self.compact_serializer.serialize_multiple(cscs)
            else:  # verbose
                return self.csc_serializer.serialize_multiple(cscs)
            
        except Exception as e:
            self.logger.error(f"Serialization failed for text '{text[:50]}...': {e}")
            return ""
    
    def encode_for_training(self, text: str, config: Optional[TrainingConfig] = None) -> str:
        """
        Convert raw text to training format with CSC and original text.
        
        Args:
            text: Raw input text to encode
            config: Training configuration (uses default if None)
            
        Returns:
            str: Training format string in [CSC_SERIALIZATION] + [ORIGINAL_TEXT] format
        """
        if config is None:
            config = self.training_config
        
        try:
            # Get CSC serialization
            csc_serialized = self.encode_and_serialize(text, format="verbose")
            
            # Generate training format based on configuration
            return self._format_for_training(csc_serialized, text, config)
            
        except Exception as e:
            self.logger.error(f"Training format generation failed for text '{text[:50]}...': {e}")
            # Fallback: return original text only
            return f"[TEXT] {text}" if config.include_brackets else text
    
    def set_training_config(self, config: TrainingConfig) -> None:
        """
        Set the training configuration for the encoder.
        
        Args:
            config: New training configuration
        """
        self.training_config = config
        self.logger.info(f"Training configuration updated: {config.format_type}")
    
    def get_training_config(self) -> TrainingConfig:
        """
        Get the current training configuration.
        
        Returns:
            TrainingConfig: Current training configuration
        """
        return self.training_config
    
    def _format_for_training(self, csc_serialized: str, original_text: str, 
                           config: TrainingConfig) -> str:
        """
        Format CSC and original text according to training configuration.
        
        Args:
            csc_serialized: Serialized CSC string
            original_text: Original input text
            config: Training configuration
            
        Returns:
            str: Formatted training string
        """
        if config.format_type == "csc_only":
            # Return only CSC serialization
            if config.include_brackets:
                return f"[CSC] {csc_serialized}"
            else:
                return csc_serialized
        
        elif config.format_type == "mixed":
            # Return weighted combination
            if config.include_brackets:
                csc_part = f"[CSC] {csc_serialized}"
                text_part = f"[TEXT] {original_text}"
            else:
                csc_part = csc_serialized
                text_part = original_text
            
            # Apply weights (for now, just repeat based on weights)
            csc_repeats = max(1, int(config.csc_weight))
            text_repeats = max(1, int(config.original_weight))
            
            parts = []
            for _ in range(csc_repeats):
                parts.append(csc_part)
            for _ in range(text_repeats):
                parts.append(text_part)
            
            return config.separator.join(parts)
        
        else:  # "standard" format
            # Return [CSC_SERIALIZATION] + [ORIGINAL_TEXT] format
            if config.include_brackets:
                csc_part = f"[CSC] {csc_serialized}" if csc_serialized else "[CSC] "
                text_part = f"[TEXT] {original_text}"
                return f"{csc_part}{config.separator}{text_part}"
            else:
                return f"{csc_serialized}{config.separator}{original_text}"
    
    def _perform_linguistic_analysis(self, text: str) -> LinguisticAnalysis:
        """
        Perform linguistic analysis with error handling.
        
        Args:
            text: Input text to analyze
            
        Returns:
            LinguisticAnalysis: Analysis results with graceful degradation
        """
        try:
            return self.linguistic_analyzer.analyze(text)
        except Exception as e:
            self.logger.warning(f"Linguistic analysis failed: {e}. Using fallback.")
            # Fallback: basic tokenization
            tokens = text.split()
            return LinguisticAnalysis(
                tokens=tokens,
                pos_tags=["NOUN"] * len(tokens),  # Default POS
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
    
    def _generate_cscs_from_analysis(self, text: str, analysis: LinguisticAnalysis) -> List[CSC]:
        """
        Generate CSC structures from linguistic analysis.
        
        Args:
            text: Original input text
            analysis: Linguistic analysis results
            
        Returns:
            List[CSC]: Generated CSC structures
        """
        cscs = []
        
        try:
            # Find main predicates in the sentence
            predicates = self._identify_predicates(analysis)
            
            if not predicates:
                # No predicates found, create single CSC with fallback ROOT
                csc = self._create_single_csc(text, analysis, fallback=True)
                if csc:
                    cscs.append(csc)
            else:
                # Process each predicate
                for predicate_info in predicates:
                    csc = self._create_single_csc(text, analysis, predicate_info)
                    if csc:
                        cscs.append(csc)
            
        except Exception as e:
            self.logger.error(f"CSC generation failed: {e}")
            # Fallback: create minimal CSC
            fallback_csc = self._create_single_csc(text, analysis, fallback=True)
            if fallback_csc:
                cscs.append(fallback_csc)
        
        return cscs
    
    def _identify_predicates(self, analysis: LinguisticAnalysis) -> List[Dict[str, Any]]:
        """
        Identify predicates in the linguistic analysis.
        
        Args:
            analysis: Linguistic analysis results
            
        Returns:
            List[Dict]: List of predicate information dictionaries
        """
        predicates = []
        
        # Find verb tokens as potential predicates
        for i, (token, pos) in enumerate(zip(analysis.tokens, analysis.pos_tags)):
            if pos in ["VERB", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                predicates.append({
                    "token": token,
                    "index": i,
                    "pos": pos
                })
        
        # If no verbs found, look for other potential predicates
        if not predicates:
            for i, (token, pos) in enumerate(zip(analysis.tokens, analysis.pos_tags)):
                if pos in ["NOUN", "ADJ"] and self.root_mapper.is_predicate_known(token):
                    predicates.append({
                        "token": token,
                        "index": i,
                        "pos": pos
                    })
        
        return predicates
    
    def _create_single_csc(self, text: str, analysis: LinguisticAnalysis, 
                          predicate_info: Optional[Dict[str, Any]] = None,
                          fallback: bool = False) -> Optional[CSC]:
        """
        Create a single CSC from analysis and predicate information.
        
        Args:
            text: Original input text
            analysis: Linguistic analysis results
            predicate_info: Information about the predicate (optional)
            fallback: Whether this is a fallback CSC creation
            
        Returns:
            CSC: Generated CSC or None if creation fails
        """
        try:
            # Step 1: Map ROOT
            root = self._map_root(analysis, predicate_info, fallback)
            
            # Step 2: Extract operators
            ops = self._extract_operators(analysis)
            
            # Step 3: Bind roles
            roles = self._bind_roles(analysis, root)
            
            # Step 4: Detect META
            meta = self._detect_meta(analysis)
            
            # Step 5: Generate CSC
            csc = self.csc_generator.generate_csc(root, ops, roles, meta)
            
            return csc
            
        except Exception as e:
            self.logger.warning(f"Single CSC creation failed: {e}")
            if not fallback:
                # Try fallback creation
                return self._create_single_csc(text, analysis, fallback=True)
            return None
    
    def _map_root(self, analysis: LinguisticAnalysis, 
                  predicate_info: Optional[Dict[str, Any]] = None,
                  fallback: bool = False) -> ROOT:
        """
        Map predicate to ROOT with error handling.
        
        Args:
            analysis: Linguistic analysis results
            predicate_info: Predicate information
            fallback: Whether to use fallback mapping
            
        Returns:
            ROOT: Mapped semantic ROOT
        """
        try:
            if fallback or not predicate_info:
                return ROOT.EXISTENCE  # Fallback ROOT
            
            predicate = predicate_info["token"]
            pos_context = predicate_info["pos"]
            
            # Create dependency context (simplified)
            dependency_context = {
                "relations": [dep[1] for dep in analysis.dependencies]
            }
            
            return self.root_mapper.map_predicate(predicate, pos_context, dependency_context)
            
        except Exception as e:
            self.logger.warning(f"ROOT mapping failed: {e}. Using fallback.")
            return ROOT.EXISTENCE
    
    def _extract_operators(self, analysis: LinguisticAnalysis) -> List:
        """
        Extract operators with error handling.
        
        Args:
            analysis: Linguistic analysis results
            
        Returns:
            List[Operator]: Extracted operators
        """
        try:
            return self.ops_extractor.extract_operators(analysis)
        except Exception as e:
            self.logger.warning(f"Operator extraction failed: {e}")
            return []
    
    def _bind_roles(self, analysis: LinguisticAnalysis, root: ROOT) -> Dict:
        """
        Bind semantic roles with error handling.
        
        Args:
            analysis: Linguistic analysis results
            root: Identified ROOT for compatibility
            
        Returns:
            Dict[Role, Entity]: Role bindings
        """
        try:
            return self.roles_binder.bind_roles(analysis, root)
        except Exception as e:
            self.logger.warning(f"Role binding failed: {e}")
            return {}
    
    def _detect_meta(self, analysis: LinguisticAnalysis):
        """
        Detect META component with error handling.
        
        Args:
            analysis: Linguistic analysis results
            
        Returns:
            Optional[META]: Detected META component
        """
        try:
            return self.meta_detector.detect_meta(analysis)
        except Exception as e:
            self.logger.warning(f"META detection failed: {e}")
            return None
    
    def _create_fallback_csc(self, text: str) -> List[CSC]:
        """
        Create minimal fallback CSC for error recovery.
        
        Args:
            text: Original input text
            
        Returns:
            List[CSC]: Minimal CSC list
        """
        try:
            from .models import Entity, Role
            
            # Create minimal CSC with EXISTENCE ROOT
            fallback_csc = self.csc_generator.generate_csc(
                root=ROOT.EXISTENCE,
                ops=[],
                roles={},
                meta=None
            )
            
            return [fallback_csc]
            
        except Exception as e:
            self.logger.error(f"Fallback CSC creation failed: {e}")
            return []
    
    def get_component_status(self) -> Dict[str, bool]:
        """
        Get status of all encoder components.
        
        Returns:
            Dict[str, bool]: Component name to status mapping
        """
        status = {}
        
        components = [
            ("linguistic_analyzer", self.linguistic_analyzer),
            ("root_mapper", self.root_mapper),
            ("ops_extractor", self.ops_extractor),
            ("roles_binder", self.roles_binder),
            ("meta_detector", self.meta_detector),
            ("csc_generator", self.csc_generator),
            ("csc_serializer", self.csc_serializer)
        ]
        
        for name, component in components:
            status[name] = component is not None
        
        return status