"""
neuro_readability/suggestions.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Rule-based suggestion engine.
Turns raw metrics into plain-English, actionable improvement advice.
"""

from typing import List, Optional
from .metrics import ReadabilityMetrics


def generate_suggestions(m: ReadabilityMetrics, target_grade: Optional[float] = None) -> List[str]:
    """
    Generate a list of plain-English suggestions based on the metrics.

    Args:
        m: A ReadabilityMetrics dataclass from calculate_all_metrics()
        target_grade: Optional target Flesch-Kincaid grade level

    Returns:
        List of suggestion strings, ordered by priority (most impactful first)
    """
    suggestions = []

    # 1. Sentence length
    if m.avg_sentence_length > 25:
        suggestions.append(
            f"Your average sentence is {m.avg_sentence_length:.0f} words — aim for under 20. "
            "Long sentences exhaust working memory before the reader reaches the end."
        )
    elif m.avg_sentence_length > 20:
        suggestions.append(
            f"Average sentence length ({m.avg_sentence_length:.0f} words) is a little high. "
            "Occasionally break complex sentences in two to ease cognitive load."
        )

    # 2. Very long individual sentences
    if m.long_sentence_count > 0:
        suggestions.append(
            f"{m.long_sentence_count} sentence{'s' if m.long_sentence_count > 1 else ''} "
            f"exceed 35 words. These are the most likely to cause re-reads — consider splitting them."
        )

    # 3. Passive voice
    if m.passive_voice_pct > 25:
        suggestions.append(
            f"Passive voice is high at {m.passive_voice_pct:.0f}% of sentences. "
            "Passive constructions require extra syntactic decoding. "
            "Target below 15% for general audiences."
        )
    elif m.passive_voice_pct > 15:
        suggestions.append(
            f"Passive voice at {m.passive_voice_pct:.0f}% — slightly above the recommended 15%. "
            "Try converting some passive constructions to active voice."
        )

    # 4. Complex word density
    if m.complex_word_pct > 35:
        suggestions.append(
            f"{m.complex_word_pct:.0f}% of words have 3+ syllables (complex words). "
            "This is quite high — consider plain alternatives where possible. "
            "Readers spend significantly more time fixating on polysyllabic words (eye-tracking research)."
        )
    elif m.complex_word_pct > 20:
        suggestions.append(
            f"Complex word density is {m.complex_word_pct:.0f}%. "
            "This is fine for academic writing, but consider your audience: "
            "plain-language equivalents can reduce cognitive load substantially."
        )

    # 5. Word length
    if m.avg_word_length > 6.5:
        suggestions.append(
            f"Average word length is {m.avg_word_length:.1f} characters, which is high. "
            "Shorter words are processed faster. Where precision allows, prefer shorter synonyms."
        )

    # 6. Sentence variety
    if m.sentence_variety_score < 0.3 and m.sentence_count >= 5:
        suggestions.append(
            "Your sentence lengths are quite uniform. Varied rhythm helps readers "
            "chunk and anticipate meaning — try mixing short, punchy sentences with longer ones."
        )

    # 7. Grade level vs target
    if target_grade is not None:
        gap = m.grade_level - target_grade
        if gap > 3:
            suggestions.append(
                f"Your text reads at grade {m.grade_level:.1f}, which is {gap:.1f} grades above "
                f"your target of {target_grade:.0f}. The biggest gains typically come from "
                "shortening sentences and replacing polysyllabic words."
            )
        elif gap > 1:
            suggestions.append(
                f"Grade level is {m.grade_level:.1f} vs target {target_grade:.0f} "
                f"(gap: {gap:.1f}). Small adjustments to sentence length should close this."
            )
        elif gap < -1:
            suggestions.append(
                f"Your text (grade {m.grade_level:.1f}) is below your target grade {target_grade:.0f}. "
                "This may be intentional — or you could add more precise vocabulary if appropriate."
            )

    # 8. Positive feedback
    if not suggestions:
        suggestions.append(
            "Great work! Your text scores well across all cognitive load indicators. "
            f"Grade level: {m.grade_level:.1f}, Flesch Ease: {m.flesch_ease:.0f}/100, "
            f"Passive voice: {m.passive_voice_pct:.0f}%."
        )
    elif m.sentence_variety_score >= 0.6:
        suggestions.append(
            "Good sentence variety — your rhythm is keeping readers engaged. Keep it up!"
        )

    return suggestions
