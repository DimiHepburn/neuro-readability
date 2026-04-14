# 🧠 neuro-readability

> *A neuroscience-informed text analysis tool that tells you exactly how hard your writing is to read — and why.*

[![PyPI version](https://img.shields.io/badge/pip-neuro--readability-blue?style=flat-square&logo=pypi)](https://github.com/DimiHepburn/neuro-readability)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Usable-brightgreen?style=flat-square)]()

---

## What is this?

**neuro-readability** is a command-line tool and Python library that analyses any piece of text and produces a rich, actionable readability report grounded in cognitive science.

It goes beyond simple word-count metrics. It measures:

- **Flesch-Kincaid Grade Level** — US school grade needed to understand the text
- **Flesch Reading Ease** — 0–100 score (higher = easier)
- **Gunning Fog Index** — estimates years of formal education required
- **Average sentence & word length** — key drivers of cognitive load
- **Passive voice density** — passive sentences slow comprehension
- **Jargon/complexity score** — frequency of long, rare, or domain-specific words
- **Sentence variety score** — monotonous length patterns reduce engagement
- **Cognitive Load Rating** — an overall composite score with a plain-English label

All metrics are grounded in decades of reading comprehension research. The tool outputs results in a clean terminal format, as JSON, or as a plain text report — making it easy to integrate into pipelines, CI checks, or editors.

---

## 🚀 Quick Install

```bash
# Clone the repo
git clone https://github.com/DimiHepburn/neuro-readability.git
cd neuro-readability

# Install dependencies
pip install -r requirements.txt

# Install as a local package (gives you the 'nr' CLI command)
pip install -e .
```

---

## 📖 Usage

### As a CLI tool

```bash
# Analyse a text file
nr analyse myessay.txt

# Analyse text piped from stdin
echo "The quick brown fox jumps over the lazy dog." | nr analyse -

# Output as JSON (great for piping into other tools)
nr analyse myessay.txt --format json

# Save report to a file
nr analyse myessay.txt --output report.txt

# Set a target grade level and get suggestions
nr analyse myessay.txt --target-grade 8

# Analyse a URL (fetches and strips HTML automatically)
nr analyse --url https://example.com/article
```

### As a Python library

```python
from neuro_readability import NeuroReadabilityAnalyser

analyser = NeuroReadabilityAnalyser()

text = """
The hippocampus, a seahorse-shaped structure nestled within the medial temporal lobe,
plays an indispensable role in the consolidation of episodic and semantic memory traces.
Its interconnections with the entorhinal cortex and prefrontal regions underpin the
transformation of labile short-term representations into durable long-term engrams.
"""

report = analyser.analyse(text)

print(report.flesch_ease)          # e.g. 18.3
print(report.grade_level)          # e.g. 18.1
print(report.cognitive_load)       # e.g. "Very High"
print(report.passive_voice_pct)    # e.g. 33.3
print(report.suggestions)          # List of actionable improvement tips
```

---

## 📊 Sample Output

```
╔══════════════════════════════════════════════════════════╗
║           🧠 neuro-readability Analysis Report           ║
╚══════════════════════════════════════════════════════════╝

  Input: myessay.txt  (847 words, 52 sentences, 6 paragraphs)

  ┌─────────────────────────────────────────────────────┐
  │  READABILITY SCORES                                 │
  ├────────────────────────────────┬────────────────────┤
  │  Flesch Reading Ease           │  42.1  (Difficult) │
  │  Flesch-Kincaid Grade Level    │  13.4  (College)   │
  │  Gunning Fog Index             │  15.2              │
  │  SMOG Index                    │  12.8              │
  └────────────────────────────────┴────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │  COGNITIVE LOAD INDICATORS                          │
  ├────────────────────────────────┬────────────────────┤
  │  Avg. sentence length          │  16.3 words        │
  │  Avg. word length              │  5.8 chars         │
  │  Passive voice                 │  28%  ⚠            │
  │  Complex words (3+ syllables)  │  34%  ⚠            │
  │  Sentence length variety       │  Good ✓            │
  │  Overall Cognitive Load        │  HIGH              │
  └────────────────────────────────┴────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │  💡 SUGGESTIONS                                     │
  ├─────────────────────────────────────────────────────┤
  │  • Aim for avg sentence length under 20 words       │
  │  • Reduce passive constructions (target < 15%)      │
  │  • 12 sentences exceed 35 words — consider          │
  │    splitting them                                   │
  │  • High complex-word density: try plain alternatives│
  │    for terms like "indispensable", "labile"         │
  └─────────────────────────────────────────────────────┘

  Target grade: 10  |  Current grade: 13.4  |  Gap: 3.4 grades
```

---

## 🧬 The Neuroscience Behind the Metrics

### Why sentence length matters
Working memory — primarily managed by the prefrontal cortex and hippocampus — can hold roughly 4 ± 1 "chunks" of information at once. Long sentences overload this buffer before the reader reaches the end, forcing costly re-reads. Research by Rayner et al. (2006) shows comprehension drops sharply for sentences exceeding 25 words.

### Why passive voice is cognitively expensive
Passive constructions ("The report was written by...") require the reader to mentally re-map agent and patient roles. This additional syntactic processing consumes extra working memory resources compared to equivalent active sentences ("The team wrote...").

### Why complex words slow reading
Eye-tracking studies show readers spend significantly longer fixating on low-frequency and polysyllabic words. The brain's lexical lookup process is slower for unfamiliar words — a cost that accumulates rapidly in dense academic or technical writing.

### Why variety matters
Monotonous sentence structures (e.g., all short, all long) reduce reader engagement and prediction. Varied rhythm — analogous to prosody in speech — helps readers chunk and anticipate meaning, reducing cognitive effort.

---

## 📁 File Structure

```
neuro-readability/
├── neuro_readability/
│   ├── __init__.py          # Package entry point
│   ├── analyser.py          # Core NeuroReadabilityAnalyser class
│   ├── metrics.py           # All readability metric calculations
│   ├── suggestions.py       # Rule-based suggestion engine
│   ├── report.py            # Report formatting (terminal, JSON, text)
│   └── fetcher.py           # URL fetching + HTML stripping
├── cli.py                   # Command-line interface (Click)
├── tests/
│   ├── test_metrics.py
│   ├── test_suggestions.py
│   └── sample_texts/
│       ├── easy.txt
│       ├── medium.txt
│       └── hard.txt
├── requirements.txt
├── setup.py
└── README.md
```

---

## ⚙️ Integrations

### Use in a CI/CD pipeline (GitHub Actions)

Add a readability gate to your documentation pipeline:

```yaml
# .github/workflows/readability-check.yml
name: Readability Check

on: [push, pull_request]

jobs:
  check-readability:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install neuro-readability
        run: |
          git clone https://github.com/DimiHepburn/neuro-readability.git
          cd neuro-readability && pip install -e .
      - name: Check README readability
        run: nr analyse README.md --target-grade 12 --fail-on-exceed
```

### Use as a pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/DimiHepburn/neuro-readability
    rev: main
    hooks:
      - id: neuro-readability
        args: [--target-grade, "14", --format, "summary"]
```

---

## 📚 References

- Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology*
- Gunning, R. (1952). *The Technique of Clear Writing*
- Rayner, K. et al. (2006). Should there be a three-cueing system in reading instruction?
- Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*
- Baddeley, A. (2003). Working memory: Looking back and looking forward. *Nature Reviews Neuroscience*

---

## 🤝 Contributing

Contributions very welcome! Especially:
- New readability metrics
- Support for languages other than English
- A web UI / Streamlit front-end
- Integration plugins for VS Code, Obsidian, etc.

Please open an issue first to discuss what you'd like to add.

---

*Built by [Dimitri (DimiHepburn)](https://github.com/DimiHepburn) as part of a broader research programme on neuroscience and AI.*
