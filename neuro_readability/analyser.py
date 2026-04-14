"""
neuro_readability/analyser.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Core NeuroReadabilityAnalyser class.
Orchestrates metric calculation, suggestion generation, and report formatting.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .metrics import ReadabilityMetrics, calculate_all_metrics
from .suggestions import generate_suggestions
from .report import format_terminal_report, format_json_report, format_text_report


@dataclass
class ReadabilityReport:
    """
    Container for all analysis results.
    Returned by NeuroReadabilityAnalyser.analyse().
    """
    # Input info
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    char_count: int = 0

    # Standard readability scores
    flesch_ease: float = 0.0
    flesch_ease_label: str = ""
    grade_level: float = 0.0        # Flesch-Kincaid Grade Level
    gunning_fog: float = 0.0
    smog_index: float = 0.0

    # Cognitive load indicators
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    passive_voice_pct: float = 0.0
    complex_word_pct: float = 0.0   # words with 3+ syllables
    sentence_variety_score: float = 0.0
    long_sentence_count: int = 0    # sentences > 35 words

    # Composite score
    cognitive_load: str = ""        # "Low", "Moderate", "High", "Very High"
    cognitive_load_score: float = 0.0  # 0-100

    # Actionable output
    suggestions: List[str] = field(default_factory=list)
    grade_gap: Optional[float] = None  # difference from target grade

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class NeuroReadabilityAnalyser:
    """
    Analyses text for cognitive load, readability, and linguistic complexity.

    Grounded in cognitive science and reading comprehension research:
    - Working memory load (Baddeley, 2003)
    - Flesch readability (Flesch, 1948)
    - Cognitive load theory (Sweller, 1988)

    Usage:
        analyser = NeuroReadabilityAnalyser()
        report = analyser.analyse("Your text here...")
        print(report.cognitive_load)      # e.g. "High"
        print(report.grade_level)         # e.g. 13.2
        print(report.suggestions)         # List of actionable tips
    """

    def __init__(self, target_grade: Optional[float] = None):
        """
        Args:
            target_grade: Optional target Flesch-Kincaid grade level.
                          If set, report will include a gap analysis.
        """
        self.target_grade = target_grade

    def analyse(self, text: str) -> ReadabilityReport:
        """
        Run full analysis on input text.

        Args:
            text: Plain text string to analyse. Can be a single sentence,
                  a paragraph, or a full document.

        Returns:
            ReadabilityReport dataclass with all scores and suggestions.
        """
        if not text or not text.strip():
            raise ValueError("Input text is empty.")

        metrics: ReadabilityMetrics = calculate_all_metrics(text)

        report = ReadabilityReport(
            word_count=metrics.word_count,
            sentence_count=metrics.sentence_count,
            paragraph_count=metrics.paragraph_count,
            char_count=metrics.char_count,
            flesch_ease=metrics.flesch_ease,
            flesch_ease_label=_flesch_label(metrics.flesch_ease),
            grade_level=metrics.grade_level,
            gunning_fog=metrics.gunning_fog,
            smog_index=metrics.smog_index,
            avg_sentence_length=metrics.avg_sentence_length,
            avg_word_length=metrics.avg_word_length,
            passive_voice_pct=metrics.passive_voice_pct,
            complex_word_pct=metrics.complex_word_pct,
            sentence_variety_score=metrics.sentence_variety_score,
            long_sentence_count=metrics.long_sentence_count,
            cognitive_load=_cognitive_load_label(metrics),
            cognitive_load_score=_cognitive_load_score(metrics),
            suggestions=generate_suggestions(metrics, self.target_grade),
        )

        if self.target_grade is not None:
            report.grade_gap = round(metrics.grade_level - self.target_grade, 1)

        return report

    def analyse_file(self, filepath: str) -> ReadabilityReport:
        """Read a text file and analyse its contents."""
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return self.analyse(text)

    def format_report(
        self,
        report: ReadabilityReport,
        fmt: str = "terminal",
        source_name: str = "stdin"
    ) -> str:
        """
        Format a ReadabilityReport as a string.

        Args:
            report: A ReadabilityReport returned by .analyse()
            fmt: One of "terminal", "json", "text"
            source_name: Label shown in the report header

        Returns:
            Formatted string ready to print or save.
        """
        if fmt == "json":
            return format_json_report(report)
        elif fmt == "text":
            return format_text_report(report, source_name, self.target_grade)
        else:
            return format_terminal_report(report, source_name, self.target_grade)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _flesch_label(score: float) -> str:
    if score >= 90:   return "Very Easy"
    if score >= 80:   return "Easy"
    if score >= 70:   return "Fairly Easy"
    if score >= 60:   return "Standard"
    if score >= 50:   return "Fairly Difficult"
    if score >= 30:   return "Difficult"
    return "Very Confusing"


def _cognitive_load_score(m: ReadabilityMetrics) -> float:
    """
    Composite 0-100 cognitive load score.
    Higher = more demanding on working memory.
    Weights are heuristic, informed by reading research.
    """
    score = 0.0
    # Grade level contribution (0-12 maps to 0-40 pts)
    score += min(40.0, (m.grade_level / 18.0) * 40.0)
    # Passive voice (0-30% maps to 0-20 pts)
    score += min(20.0, (m.passive_voice_pct / 30.0) * 20.0)
    # Complex word density (0-50% maps to 0-25 pts)
    score += min(25.0, (m.complex_word_pct / 50.0) * 25.0)
    # Sentence length variance (low variety adds up to 15 pts)
    variety_penalty = max(0.0, 1.0 - m.sentence_variety_score) * 15.0
    score += variety_penalty
    return round(min(100.0, score), 1)


def _cognitive_load_label(m: ReadabilityMetrics) -> str:
    s = _cognitive_load_score(m)
    if s < 30:  return "Low"
    if s < 55:  return "Moderate"
    if s < 75:  return "High"
    return "Very High"
