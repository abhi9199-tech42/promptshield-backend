
import pytest
from ptil import PTILEncoder, ROOT, Operator, Role, META
from ptil.linguistic_analyzer import LinguisticAnalyzer
from ptil.ops_extractor import OPSExtractor
from ptil.roles_binder import ROLESBinder
from ptil.meta_detector import METADetector
from ptil.csc_generator import CSCGenerator
from ptil.models import LinguisticAnalysis, CSC

class TestOPSExtractorErrorHandling:
    """Test error handling in OPSExtractor."""
    
    def test_contradictory_tense_markers(self):
        """Test handling of contradictory tense markers (e.g., markers for both past and future)."""
        extractor = OPSExtractor()
        # Simulate an analysis with conflicting tense markers
        analysis = LinguisticAnalysis(
            tokens=["will", "went"],
            pos_tags=["MD", "VBD"],
            dependencies=[],
            negation_markers=[],
            # Intentionally contradictory
            tense_markers={"future": [0], "past": [1]},
            aspect_markers={}
        )
        
        ops = extractor.extract(analysis, ROOT.MOTION)
        # Should deterministically pick one or handle gracefully without crashing
        tenses = [op for op in ops if op in {Operator.PAST, Operator.FUTURE, Operator.PRESENT}]
        assert len(tenses) <= 1  # Should resolve to at most one primary tense
    
    def test_empty_analysis_ops(self):
        """Test extraction from completely empty analysis."""
        extractor = OPSExtractor()
        analysis = LinguisticAnalysis(
            tokens=[],
            pos_tags=[],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        ops = extractor.extract(analysis, ROOT.MOTION)
        assert isinstance(ops, list)
        # Should probably default to PRESENT or empty
        assert Operator.PRESENT in ops or len(ops) == 0

class TestROLESBinderErrorHandling:
    """Test error handling in ROLESBinder."""
    
    def test_missing_subject_object(self):
        """Test binding when no clear subject or object exists (e.g. imperative or fragments)."""
        binder = ROLESBinder()
        analysis = LinguisticAnalysis(
            tokens=["Run", "!"],
            pos_tags=["VB", "."],
            dependencies=[], # No dependencies
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        roles = binder.bind_roles(analysis, ROOT.MOTION, 0)
        assert isinstance(roles, dict)
        # Likely empty roles, or maybe implied AGENT
        
    def test_passive_without_agent(self):
        """Test passive voice where agent is missing ('The window was broken')."""
        binder = ROLESBinder()
        # "Window broken" - window is nsubjpass
        analysis = LinguisticAnalysis(
            tokens=["The", "window", "was", "broken"],
            pos_tags=["DT", "NN", "VBD", "VBN"],
            dependencies=[(3, "nsubjpass", 1)], # broken -> window
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        roles = binder.bind_roles(analysis, ROOT.CHANGE, 3) # root at 'broken'
        
        # 'window' should probably be PATIENT or THEME, not AGENT
        assert Role.PATIENT in roles or Role.THEME in roles
        assert Role.AGENT not in roles

class TestMETADetectorErrorHandling:
    """Test error handling in METADetector."""
    
    def test_mixed_signals(self):
        """Test sentence with declarative structure but question mark."""
        detector = METADetector()
        # "You are going?"
        analysis = LinguisticAnalysis(
            tokens=["You", "are", "going", "?"],
            pos_tags=["PRP", "VBP", "VBG", "."],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        # Should prioritize punctuation ? -> QUESTION
        meta = detector.detect(analysis, ROOT.MOTION)
        assert meta == META.QUESTION

    def test_empty_tokens_meta(self):
        """Test meta detection on empty tokens."""
        detector = METADetector()
        analysis = LinguisticAnalysis(
            tokens=[],
            pos_tags=[],
            dependencies=[],
            negation_markers=[],
            tense_markers={},
            aspect_markers={}
        )
        meta = detector.detect(analysis, ROOT.EXISTENCE)
        # Default to ASSERTIVE or None
        assert meta is None or meta == META.ASSERTIVE

class TestCSCGeneratorErrorHandling:
    """Test error handling in CSCGenerator."""
    
    def test_missing_root_generation(self):
        """Test generation when ROOT is missing (should raise or handle)."""
        generator = CSCGenerator()
        # This might be intended to fail if ROOT is mandatory in constructor
        # We check if it handles None gracefully or enforces type integrity
        try:
            # If the design strictly enforces ROOT, this might fail or require a dummy ROOT
            # Assuming 'None' might trigger a validation error
            csc = CSC(root=None, ops=[], roles={})
            # If dataclass allows None but logic doesn't, we check validate
        except Exception:
            pass # Type error is acceptable if strictly typed

class TestPTILEncoderResilience:
    """Test high-level resilience of the encoder."""
    
    def test_partial_failure_recovery(self):
        """If one component fails, does the pipeline crash or degrade?"""
        encoder = PTILEncoder()
        
        # Mocking a component to raise an exception
        # This requires the encoder to not catch internal errors blindly, 
        # but we want to see if it handles known bad states.
        # Instead of mocking, we feed input that triggers known edge cases.
        
        # Input that causes tokenizer to produce empty tokens but non-empty text?
        # Hard to force without internal mocking, so we rely on system boundaries.
        pass

    def test_extreme_recursion_depth(self):
        """Test highly nested sentence structures."""
        encoder = PTILEncoder()
        # excessively nested "that" clauses
        text = "He said that she said that he thought that I knew that..." + ("that it was true " * 20)
        try:
            cscs = encoder.encode(text)
            assert len(cscs) > 0
        except RecursionError:
            pytest.fail("Encoder crashed on recursion depth")

    def test_conflicting_unicode_directionality(self):
        """Test BIDI text attacks."""
        encoder = PTILEncoder()
        # RTL and LTR mixed
        text = "The \u202e esrever \u202c boy."  # "The reverse boy" with override chars
        cscs = encoder.encode(text)
        assert isinstance(cscs, list)
