"""
neuro_readability/report.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Report formatting: terminal (rich box-drawing), JSON, and plain text.
"""

import json
from typing import Optional


def format_terminal_report(report, source_name: str = "stdin", target_grade: Optional[float] = None) -> str:
    """
    Render a ReadabilityReport as a pretty terminal box-drawing report.
    Uses only ASCII box-drawing chars for maximum compatibility.
    """
    W = 60  # report width

    def box_top():    return "+" + "=" * (W - 2) + "+"
    def box_bottom(): return "+" + "=" * (W - 2) + "+"
    def row_div():    return "+" + "-" * (W - 2) + "+"
    def row(left, right="", w=W):
        left_w = w // 2 - 2
        right_w = w - left_w - 5
        return f"| {left:<{left_w}} | {right:<{right_w}} |"
    def full_row(text, w=W):
        inner = w - 4
        return f"| {text:<{inner}} |"
    def centre(text, w=W):
        inner = w - 2
        return "|" + text.center(inner) + "|"

    lines = []
    lines.append(box_top())
    lines.append(centre("  neuro-readability Analysis Report  "))
    lines.append(box_bottom())
    lines.append("")

    # Input summary
    lines.append(full_row(f"  Input: {source_name}  ({report.word_count} words, "
                          f"{report.sentence_count} sentences, {report.paragraph_count} paragraphs)"))
    lines.append("")

    # Readability scores
    lines.append(row_div())
    lines.append(full_row("  READABILITY SCORES"))
    lines.append(row_div())
    lines.append(row("  Flesch Reading Ease", f"{report.flesch_ease:.1f}  ({report.flesch_ease_label})"))
    lines.append(row("  Flesch-Kincaid Grade", f"{report.grade_level:.1f}"))
    lines.append(row("  Gunning Fog Index", f"{report.gunning_fog:.1f}"))
    lines.append(row("  SMOG Index", f"{report.smog_index:.1f}"))
    lines.append(row_div())
    lines.append("")

    # Cognitive load
    cog_warn = " (!)" if report.cognitive_load in ("High", "Very High") else " (OK)"
    lines.append(row_div())
    lines.append(full_row("  COGNITIVE LOAD INDICATORS"))
    lines.append(row_div())
    lines.append(row("  Avg sentence length", f"{report.avg_sentence_length:.1f} words"))
    lines.append(row("  Avg word length", f"{report.avg_word_length:.1f} chars"))

    passive_warn = " (!)" if report.passive_voice_pct > 15 else " (ok)"
    lines.append(row("  Passive voice", f"{report.passive_voice_pct:.0f}%{passive_warn}"))

    complex_warn = " (!)" if report.complex_word_pct > 25 else " (ok)"
    lines.append(row("  Complex words (3+ syl.)", f"{report.complex_word_pct:.0f}%{complex_warn}"))

    variety = "Good" if report.sentence_variety_score >= 0.5 else "Low"
    lines.append(row("  Sentence variety", variety))

    if report.long_sentence_count > 0:
        lines.append(row("  Sentences > 35 words", str(report.long_sentence_count) + " (!)"))

    lines.append(row("  Overall Cognitive Load", report.cognitive_load + cog_warn))
    lines.append(row_div())
    lines.append("")

    # Suggestions
    if report.suggestions:
        lines.append(row_div())
        lines.append(full_row("  SUGGESTIONS"))
        lines.append(row_div())
        for sug in report.suggestions:
            # Word-wrap at ~54 chars
            words = sug.split()
            cur_line = "  * "
            for word in words:
                if len(cur_line) + len(word) + 1 > W - 4:
                    lines.append(full_row(cur_line))
                    cur_line = "    " + word + " "
                else:
                    cur_line += word + " "
            if cur_line.strip():
                lines.append(full_row(cur_line))
            lines.append(full_row(""))
        lines.append(row_div())
        lines.append("")

    # Footer
    if target_grade is not None and report.grade_gap is not None:
        gap_str = f"+{report.grade_gap}" if report.grade_gap > 0 else str(report.grade_gap)
        lines.append(full_row(
            f"  Target grade: {target_grade:.0f}  |  "
            f"Current grade: {report.grade_level:.1f}  |  "
            f"Gap: {gap_str} grades"
        ))

    return "\n".join(lines)


def format_json_report(report) -> str:
    """Render report as compact, readable JSON."""
    return json.dumps(report.to_dict(), indent=2, default=str)


def format_text_report(report, source_name: str = "stdin", target_grade: Optional[float] = None) -> str:
    """Render a plain-text report (no box drawing — suitable for file output)."""
    lines = [
        "neuro-readability Analysis Report",
        "=" * 40,
        f"Input: {source_name}",
        f"Words: {report.word_count}  |  Sentences: {report.sentence_count}  |  Paragraphs: {report.paragraph_count}",
        "",
        "READABILITY SCORES",
        f"  Flesch Reading Ease:    {report.flesch_ease:.1f} ({report.flesch_ease_label})",
        f"  Flesch-Kincaid Grade:   {report.grade_level:.1f}",
        f"  Gunning Fog Index:      {report.gunning_fog:.1f}",
        f"  SMOG Index:             {report.smog_index:.1f}",
        "",
        "COGNITIVE LOAD",
        f"  Avg sentence length:    {report.avg_sentence_length:.1f} words",
        f"  Avg word length:        {report.avg_word_length:.1f} chars",
        f"  Passive voice:          {report.passive_voice_pct:.0f}%",
        f"  Complex words:          {report.complex_word_pct:.0f}%",
        f"  Sentence variety:       {'Good' if report.sentence_variety_score >= 0.5 else 'Low'}",
        f"  Overall:                {report.cognitive_load}",
        "",
        "SUGGESTIONS",
    ]
    for i, sug in enumerate(report.suggestions, 1):
        lines.append(f"  {i}. {sug}")

    if target_grade is not None and report.grade_gap is not None:
        lines.append("")
        lines.append(f"Target grade: {target_grade:.0f}  |  Current: {report.grade_level:.1f}  |  Gap: {report.grade_gap:+.1f}")

    return "\n".join(lines)
