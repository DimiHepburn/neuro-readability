"""
neuro_readability/metrics.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All readability metric calculations.
Uses only the Python standard library + one optional dependency (nltk for
syllable counting; falls back to a heuristic counter if unavailable).
"""

import re
import math
import string
from dataclasses import dataclass
from typing import List

# Try to use nltk's CMU dict for accurate syllable counts; fall back to heuristic
try:
    import nltk
    from nltk.corpus import cmudict
    _cmu = cmudict.dict()
    _HAS_CMU = True
except Exception:
    _cmu = {}
    _HAS_CMU = False


@dataclass
class ReadabilityMetrics:
    """All raw measurements extracted from a text sample."""
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    char_count: int = 0
    syllable_count: int = 0
    complex_word_count: int = 0     # words with >= 3 syllables
    complex_word_pct: float = 0.0
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    avg_syllables_per_word: float = 0.0
    passive_voice_count: int = 0
    passive_voice_pct: float = 0.0
    sentence_lengths: List[int] = None
    sentence_variety_score: float = 0.0   # 0-1, higher = more varied
    long_sentence_count: int = 0

    # Standard scores
    flesch_ease: float = 0.0
    grade_level: float = 0.0
    gunning_fog: float = 0.0
    smog_index: float = 0.0

    def __post_init__(self):
        if self.sentence_lengths is None:
            self.sentence_lengths = []


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_all_metrics(text: str) -> ReadabilityMetrics:
    """
    Run all metric calculations on a text string.
    Returns a fully populated ReadabilityMetrics dataclass.
    """
    m = ReadabilityMetrics()
    text = text.strip()

    sentences = _split_sentences(text)
    words = _extract_words(text)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    m.sentence_count = max(len(sentences), 1)
    m.word_count = len(words)
    m.paragraph_count = max(len(paragraphs), 1)
    m.char_count = len(text)

    if not words:
        return m

    # Syllable counts
    syllables_per_word = [count_syllables(w) for w in words]
    m.syllable_count = sum(syllables_per_word)
    m.avg_syllables_per_word = m.syllable_count / m.word_count

    # Complex words (3+ syllables, excluding proper nouns heuristically)
    complex_words = [w for w, s in zip(words, syllables_per_word)
                     if s >= 3 and not w[0].isupper()]
    m.complex_word_count = len(complex_words)
    m.complex_word_pct = round(100 * m.complex_word_count / m.word_count, 1)

    # Word & sentence length
    m.avg_word_length = round(sum(len(w) for w in words) / m.word_count, 1)
    sentence_lengths = [len(_extract_words(s)) for s in sentences]
    m.sentence_lengths = sentence_lengths
    m.avg_sentence_length = round(m.word_count / m.sentence_count, 1)
    m.long_sentence_count = sum(1 for l in sentence_lengths if l > 35)

    # Sentence variety (coefficient of variation of sentence lengths)
    if len(sentence_lengths) > 1:
        mean = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((l - mean) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean if mean > 0 else 0
        # Normalise: CV of 0.5 or higher = good variety (score 1.0)
        m.sentence_variety_score = round(min(1.0, cv / 0.5), 2)
    else:
        m.sentence_variety_score = 0.0

    # Passive voice detection
    passive_hits = [s for s in sentences if _is_passive(s)]
    m.passive_voice_count = len(passive_hits)
    m.passive_voice_pct = round(100 * m.passive_voice_count / m.sentence_count, 1)

    # Readability formulae
    asl = m.avg_sentence_length          # avg sentence length (words)
    asw = m.avg_syllables_per_word       # avg syllables per word

    # Flesch Reading Ease: 206.835 - 1.015*ASL - 84.6*ASW
    m.flesch_ease = round(206.835 - (1.015 * asl) - (84.6 * asw), 1)
    m.flesch_ease = max(0.0, min(100.0, m.flesch_ease))

    # Flesch-Kincaid Grade Level: 0.39*ASL + 11.8*ASW - 15.59
    m.grade_level = round(0.39 * asl + 11.8 * asw - 15.59, 1)
    m.grade_level = max(0.0, m.grade_level)

    # Gunning Fog Index: 0.4 * (ASL + complex_word_pct)
    m.gunning_fog = round(0.4 * (asl + m.complex_word_pct), 1)

    # SMOG Index (requires >= 30 sentences for accuracy)
    if m.sentence_count >= 3:
        m.smog_index = round(1.0430 * math.sqrt(m.complex_word_count * (30 / m.sentence_count)) + 3.1291, 1)
    else:
        m.smog_index = m.grade_level  # fallback for very short texts

    return m


# ── Syllable counting ─────────────────────────────────────────────────────────

def count_syllables(word: str) -> int:
    """
    Count syllables in a word.
    Uses CMU Pronouncing Dictionary if available (via nltk),
    otherwise falls back to a heuristic vowel-group counter.
    """
    word_lower = word.lower().strip(string.punctuation)
    if not word_lower:
        return 1

    if _HAS_CMU and word_lower in _cmu:
        # CMU entries: each digit in the phoneme list indicates a stressed vowel
        return max(1, sum(1 for phoneme in _cmu[word_lower][0] if phoneme[-1].isdigit()))

    return _heuristic_syllable_count(word_lower)


def _heuristic_syllable_count(word: str) -> int:
    """
    Heuristic syllable counter based on vowel groups.
    Not as accurate as the CMU dict but works without nltk.
    """
    word = word.lower()
    # Remove trailing silent 'e'
    if word.endswith('e') and len(word) > 2:
        word = word[:-1]

    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    # Handle edge cases
    if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
        count += 1
    if word.endswith('ed') and len(word) > 2 and word[-3] not in 'aeiouy':
        count = max(count - 1, 1)

    return max(1, count)


# ── Sentence splitting ────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    """
    Split text into sentences using a regex approach.
    Handles common abbreviations to avoid false splits (Mr., Dr., etc.).
    """
    # Protect common abbreviations
    abbrevs = r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|i\.e|e\.g|cf|al|Fig|Eq)\.(?=\s)'
    text_protected = re.sub(abbrevs, lambda m: m.group(0).replace('.', '<DOT>'), text)

    # Split on sentence-ending punctuation
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text_protected)

    sentences = [s.replace('<DOT>', '.').strip() for s in raw if s.strip()]
    return sentences if sentences else [text]


# ── Word extraction ───────────────────────────────────────────────────────────

def _extract_words(text: str) -> List[str]:
    """Extract alphabetic words from text (no numbers, no punctuation)."""
    return re.findall(r"[a-zA-Z']+", text)


# ── Passive voice detection ───────────────────────────────────────────────────

# Regex patterns for common passive voice constructions
_PASSIVE_PATTERNS = [
    r'\b(am|is|are|was|were|be|been|being)\s+(\w+ed|\w+en)\b',
    r'\b(has|have|had)\s+been\s+(\w+ed|\w+en)\b',
    r'\b(will|shall|should|could|would|may|might|must)\s+be\s+(\w+ed|\w+en)\b',
]
_PASSIVE_RE = re.compile('|'.join(_PASSIVE_PATTERNS), re.IGNORECASE)


def _is_passive(sentence: str) -> bool:
    """Return True if the sentence appears to contain a passive construction."""
    return bool(_PASSIVE_RE.search(sentence))
