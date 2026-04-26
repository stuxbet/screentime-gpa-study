# Screen Time vs GPA — CS394R Mini Project

**Course:** CS394R
**Authors:** Luke Malcom, Judi Cavender, Reyna Salvador, Michelle Aguilera

This repo contains the analysis pipeline for our class survey on the
relationship between daily screen time and GPA. The methodology mirrors the
slide deck exactly: parse the survey responses, categorise into four sets at
the thresholds GPA = 3.5 and screen time = 6 h, build a 2×2 contingency
table, compute conditional probabilities, and apply Bayes' theorem.

The report (`.docx`) and slide deck (`.pptx`) are the project deliverables
and are kept locally, outside version control.

## What's in here

| File | Purpose |
|---|---|
| `analysis.py` | Reads the raw Google Forms export, parses screen-time strings into decimal hours, builds the 2×2 contingency table, and applies Bayes' theorem |
| `Assessment (Responses).xlsx` | Raw survey export (n = 20 responses) |
| `.gitignore` | Excludes the docx, pptx, and regenerated outputs |

## Running it

```
pip install pandas openpyxl
python3 analysis.py
```

## Headline result (n = 20)

With the deck's thresholds (GPA ≥ 3.5 = high, screen time ≥ 6 h = high):

- P(G_H) = 0.500, P(S_H) = 0.550
- P(S_H | G_H) = 0.600 — probability of high screen time given a high GPA
- P(S_H | G_L) = 0.500 — probability of high screen time given a low GPA
- Bayes' theorem: P(G_H | S_H) = (0.600 · 0.500) / 0.550 = **0.545**

Bayes' theorem shows there is approximately a **60% probability** that a
high-GPA student also has a high screen time. Contrary to the working
hypothesis, students in the high-GPA group were slightly more likely to be
heavy screen users. Limitations: small sample (n = 20) and no breakdown of
productive vs. unproductive screen time.
