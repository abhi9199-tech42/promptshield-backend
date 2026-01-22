"""
Linguistic Analyzer component for PTIL semantic encoder.

This module provides shallow linguistic analysis including tokenization, POS tagging,
dependency parsing, negation detection, and tense/aspect cue extraction using spaCy.
Supports multiple languages for cross-lingual consistency.
"""

import spacy
from typing import List, Dict, Tuple, Optional, Set
from .models import LinguisticAnalysis


class LinguisticAnalyzer:
    """
    Performs shallow linguistic analysis to extract semantic information
    without requiring deep neural inference. Supports multiple languages
    for cross-lingual consistency validation.
    """
    
    # Language-specific model mappings
    LANGUAGE_MODELS = {
        'en': 'en_core_web_sm',
        'es': 'es_core_news_sm',
        'fr': 'fr_core_news_sm',
        'de': 'de_core_news_sm',
        'it': 'it_core_news_sm',
        'pt': 'pt_core_news_sm',
        'nl': 'nl_core_news_sm',
        'zh': 'zh_core_web_sm',
        'ja': 'ja_core_news_sm',
        'ru': 'ru_core_news_sm'
    }
    
    # Language-specific negation markers
    NEGATION_MARKERS = {
        'en': {"not", "n't", "no", "never", "nothing", "nobody", "nowhere",
               "neither", "nor", "none", "hardly", "scarcely", "barely"},
        'es': {"no", "nunca", "nada", "nadie", "ningún", "ninguna", "ninguno",
               "jamás", "tampoco", "ni"},
        'fr': {"ne", "pas", "non", "jamais", "rien", "personne", "aucun",
               "aucune", "ni", "plus"},
        'de': {"nicht", "kein", "keine", "keiner", "keines", "nie", "niemals",
               "nichts", "niemand", "weder", "noch"},
        'it': {"non", "mai", "niente", "nulla", "nessuno", "nessuna", "né",
               "neanche", "nemmeno", "neppure"},
        'pt': {"não", "nunca", "nada", "ninguém", "nenhum", "nenhuma",
               "jamais", "nem", "tampouco"},
        'nl': {"niet", "geen", "nooit", "niets", "niemand", "noch", "nergens"},
        'zh': {"不", "没", "没有", "不是", "从不", "决不", "无", "无人"},
        'ja': {"ない", "ません", "いない", "ではない", "じゃない", "まったく", "全然"},
        'ru': {"не", "нет", "никогда", "ничто", "никто", "ни", "никакой"}
    }
    
    # Language-specific future markers
    FUTURE_MARKERS = {
        'en': {"will", "shall", "going", "gonna"},
        'es': {"va", "voy", "vas", "vamos", "van", "iré", "irás", "irá", "iremos", "irán"},
        'fr': {"va", "vais", "vas", "allons", "allez", "vont", "aurai", "auras", "aura", "aurons", "aurez", "auront"},
        'de': {"wird", "werde", "wirst", "werden", "werdet"},
        'it': {"andrà", "andrai", "andremo", "andrete", "andranno", "sarà", "sarai", "saremo", "sarete", "saranno"},
        'pt': {"vai", "vou", "vais", "vamos", "vão", "irei", "irás", "irá", "iremos", "irão"},
        'nl': {"zal", "zult", "zullen", "ga", "gaat", "gaan"},
        'zh': {"将", "会", "要", "将要", "即将"},
        'ja': {"でしょう", "だろう", "ます", "る予定", "つもり"},
        'ru': {"будет", "буду", "будешь", "будем", "будете", "будут"}
    }
    
    def __init__(self, model_name: str = "en_core_web_sm", language: Optional[str] = None):
        """
        Initialize the linguistic analyzer with a spaCy model.
        
        Args:
            model_name: Name of the spaCy model to use for analysis
            language: Language code (e.g., 'en', 'es', 'fr') for language-specific processing
        """
        self.model_name = model_name
        self.language = language or self._detect_language_from_model(model_name)
        
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{model_name}' not found. "
                f"Please install it with: python -m spacy download {model_name}"
            )
    
    @classmethod
    def create_for_language(cls, language: str) -> 'LinguisticAnalyzer':
        """
        Create a linguistic analyzer for a specific language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            LinguisticAnalyzer: Analyzer configured for the specified language
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in cls.LANGUAGE_MODELS:
            raise ValueError(f"Language '{language}' not supported. "
                           f"Supported languages: {list(cls.LANGUAGE_MODELS.keys())}")
        
        model_name = cls.LANGUAGE_MODELS[language]
        return cls(model_name=model_name, language=language)
    
    @classmethod
    def get_supported_languages(cls) -> Set[str]:
        """
        Get the set of supported language codes.
        
        Returns:
            Set[str]: Set of supported language codes
        """
        return set(cls.LANGUAGE_MODELS.keys())
    
    def _detect_language_from_model(self, model_name: str) -> str:
        """
        Detect language code from spaCy model name.
        
        Args:
            model_name: spaCy model name
            
        Returns:
            str: Language code (defaults to 'en' if not detected)
        """
        for lang, model in self.LANGUAGE_MODELS.items():
            if model == model_name:
                return lang
        
        # Try to extract from model name prefix
        if model_name.startswith(('en_', 'es_', 'fr_', 'de_', 'it_', 'pt_', 'nl_', 'zh_', 'ja_', 'ru_')):
            return model_name[:2]
        
        return 'en'  # Default to English
    
    def analyze(self, text: str) -> LinguisticAnalysis:
        """
        Performs comprehensive linguistic analysis on input text.
        
        Args:
            text: Raw input text to analyze
            
        Returns:
            LinguisticAnalysis containing tokens, POS tags, dependencies,
            negation markers, and tense/aspect cues
        """
        if not text or not text.strip():
            return LinguisticAnalysis(
                tokens=[],
                pos_tags=[],
                dependencies=[],
                negation_markers=[],
                tense_markers={},
                aspect_markers={}
            )
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract basic linguistic features
        tokens = [token.text for token in doc]
        pos_tags = [token.pos_ for token in doc]
        dependencies = self._extract_dependencies(doc)
        
        # Extract semantic markers
        negation_markers = self._detect_negation_markers(doc)
        tense_markers = self._extract_tense_markers(doc)
        aspect_markers = self._extract_aspect_markers(doc)
        
        return LinguisticAnalysis(
            tokens=tokens,
            pos_tags=pos_tags,
            dependencies=dependencies,
            negation_markers=negation_markers,
            tense_markers=tense_markers,
            aspect_markers=aspect_markers
        )
    
    def _extract_dependencies(self, doc) -> List[Tuple[int, str, int]]:
        """
        Extract dependency relationships from spaCy doc.
        
        Returns:
            List of (head_idx, relation, dependent_idx) tuples
        """
        dependencies = []
        for token in doc:
            if token.head != token:  # Skip root token self-reference
                dependencies.append((token.head.i, token.dep_, token.i))
        return dependencies
    
    def _detect_negation_markers(self, doc) -> List[int]:
        """
        Detect negation markers using language-specific patterns and spaCy's built-in capabilities.
        
        Returns:
            List of token indices containing negation markers
        """
        negation_markers = []
        
        # Get language-specific negation words
        negation_words = self.NEGATION_MARKERS.get(self.language, self.NEGATION_MARKERS['en'])
        
        for token in doc:
            # Check for explicit negation words
            if token.lemma_.lower() in negation_words or token.text.lower() in negation_words:
                negation_markers.append(token.i)
            
            # Check for negation dependency labels
            elif token.dep_ == "neg":
                negation_markers.append(token.i)
            
            # Check for contracted negations (mainly English)
            elif self.language == 'en' and "n't" in token.text.lower():
                negation_markers.append(token.i)
            
            # Language-specific patterns
            elif self._is_language_specific_negation(token):
                negation_markers.append(token.i)
        
        return negation_markers
    
    def _is_language_specific_negation(self, token) -> bool:
        """
        Check for language-specific negation patterns.
        
        Args:
            token: spaCy token to check
            
        Returns:
            bool: True if token represents negation in the specific language
        """
        if self.language == 'fr':
            # French "ne...pas" construction
            if token.text.lower() == "ne":
                # Look for "pas" in the sentence
                for other_token in token.doc:
                    if other_token.text.lower() == "pas":
                        return True
        
        elif self.language == 'de':
            # German "nicht" and "kein" variations
            if token.text.lower().startswith(('kein', 'nicht')):
                return True
        
        elif self.language == 'zh':
            # Chinese negation particles
            if token.text in {'不', '没', '没有', '不是'}:
                return True
        
        elif self.language == 'ja':
            # Japanese negation patterns
            if token.text.endswith(('ない', 'ません')) or token.text in {'いない', 'ではない', 'じゃない'}:
                return True
        
        return False
    
    def _extract_tense_markers(self, doc) -> Dict[str, List[int]]:
        """
        Extract tense markers from grammatical features using language-specific patterns.
        
        Returns:
            Dictionary mapping tense types to token indices
        """
        tense_markers = {
            "past": [],
            "present": [],
            "future": []
        }
        
        # Get language-specific future markers
        future_words = self.FUTURE_MARKERS.get(self.language, self.FUTURE_MARKERS['en'])
        
        for token in doc:
            # Check morphological tense features
            if "Tense=Past" in token.morph:
                tense_markers["past"].append(token.i)
            elif "Tense=Pres" in token.morph:
                tense_markers["present"].append(token.i)
            
            # Check for future auxiliary verbs (language-specific)
            if token.lemma_.lower() in future_words or token.text.lower() in future_words:
                tense_markers["future"].append(token.i)
            
            # Language-specific tense detection
            self._detect_language_specific_tense(token, tense_markers)
        
        return tense_markers
    
    def _detect_language_specific_tense(self, token, tense_markers: Dict[str, List[int]]) -> None:
        """
        Detect language-specific tense patterns.
        
        Args:
            token: spaCy token to analyze
            tense_markers: Dictionary to update with detected tense markers
        """
        if self.language == 'en':
            # Check for "be going to" construction
            if (token.lemma_.lower() == "be" and 
                token.i + 1 < len(token.doc) and 
                token.doc[token.i + 1].lemma_.lower() == "go"):
                tense_markers["future"].append(token.i)
        
        elif self.language == 'es':
            # Spanish future tense endings
            if token.pos_ == "VERB" and token.text.endswith(('ré', 'rás', 'rá', 'remos', 'réis', 'rán')):
                tense_markers["future"].append(token.i)
            # Spanish "ir a" + infinitive construction
            elif token.lemma_ == "ir" and token.i + 1 < len(token.doc) and token.doc[token.i + 1].text == "a":
                tense_markers["future"].append(token.i)
        
        elif self.language == 'fr':
            # French future tense endings
            if token.pos_ == "VERB" and token.text.endswith(('rai', 'ras', 'ra', 'rons', 'rez', 'ront')):
                tense_markers["future"].append(token.i)
            # French "aller" + infinitive construction
            elif token.lemma_ == "aller":
                tense_markers["future"].append(token.i)
        
        elif self.language == 'de':
            # German future with "werden"
            if token.lemma_ == "werden":
                tense_markers["future"].append(token.i)
        
        elif self.language == 'zh':
            # Chinese aspect/tense particles
            if token.text in {'了', '过'}:
                tense_markers["past"].append(token.i)
            elif token.text in {'将', '会', '要'}:
                tense_markers["future"].append(token.i)
    
    def _extract_aspect_markers(self, doc) -> Dict[str, List[int]]:
        """
        Extract aspect markers from grammatical features.
        
        Returns:
            Dictionary mapping aspect types to token indices
        """
        aspect_markers = {
            "continuous": [],
            "completed": [],
            "habitual": []
        }
        
        # Continuous aspect markers
        continuous_words = {"be", "being"}
        
        # Perfect aspect markers
        perfect_words = {"have", "has", "had"}
        
        # Habitual aspect markers
        habitual_words = {"usually", "always", "often", "frequently", "regularly"}
        
        for token in doc:
            # Check for continuous aspect (progressive)
            if token.lemma_.lower() in continuous_words and token.pos_ == "AUX":
                # Look for following -ing verb
                for child in token.children:
                    if child.pos_ == "VERB" and child.text.endswith("ing"):
                        aspect_markers["continuous"].append(token.i)
                        break
            
            # Check for perfect aspect
            elif token.lemma_.lower() in perfect_words and token.pos_ == "AUX":
                # Look for following past participle
                for child in token.children:
                    if child.pos_ == "VERB" and "VerbForm=Part" in child.morph:
                        aspect_markers["completed"].append(token.i)
                        break
            
            # Check for habitual markers
            elif token.lemma_.lower() in habitual_words:
                aspect_markers["habitual"].append(token.i)
        
        return aspect_markers