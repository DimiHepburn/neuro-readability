"""
neuro_readability
~~~~~~~~~~~~~~~~~
A neuroscience-informed text readability analyser.

Quick start:
    from neuro_readability import NeuroReadabilityAnalyser
    report = NeuroReadabilityAnalyser().analyse("Your text here...")
    print(report.cognitive_load)
    print(report.grade_level)
    print(report.suggestions)
"""

__version__ = "1.0.0"
__author__ = "Dimitri (DimiHepburn)"
__license__ = "MIT"

from .analyser import NeuroReadabilityAnalyser, ReadabilityReport
from .metrics import calculate_all_metrics, count_syllables, ReadabilityMetrics

__all__ = [
    "NeuroReadabilityAnalyser",
    "ReadabilityReport",
    "ReadabilityMetrics",
    "calculate_all_metrics",
    "count_syllables",
]
