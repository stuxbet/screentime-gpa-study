# Screen Time vs GPA — CS394R Mini Project

**Course:** CS394R
**Authors:** Luke Malcom, Judi Cavender, Reyna Salvador, Michelle Aguilera

This repo contains the analysis pipeline for our class survey on the
relationship between daily screen time and GPA. The report (`.docx`) and
slide deck (`.pptx`) are the project deliverables and are kept locally,
outside version control.

## What's in here

| File | Purpose |
|---|---|
| `analysis.py` | Reads the raw Google Forms export, parses the messy free-text screen-time strings into hours, and runs the full statistical pipeline used in the report and slides |
| `Assessment (Responses).xlsx` | Raw survey export (n = 20 responses) |
| `.gitignore` | Excludes the docx, pptx, and regenerated analysis outputs |

## What `analysis.py` computes

- Descriptive statistics (mean, median, variance, SD) for screen time and GPA
- Pearson and Spearman correlation, with Fisher-z 95% CI for r
- Simple linear regression of GPA on screen time
- 2×2 contingency table at the deck thresholds (GPA = 3.5, screen time = 6 h)
- Conditional probabilities and Bayes' theorem flip
- Chi-square test of independence
- Bayesian Beta-Binomial posterior comparison via Monte Carlo (200,000 draws)
- Chebyshev's inequality on GPA

It writes a cleaned CSV/XLSX of the data and three figures
(`scatter.png`, `histograms.png`, `posteriors.png`) into the working
directory; all of these are gitignored because they're regenerable.

## Running it

```
pip install numpy pandas scipy matplotlib openpyxl
python3 analysis.py
```

## Headline result (n = 20)

With the deck's thresholds (GPA ≥ 3.5 = high, screen time ≥ 6 h = high):

- P(S_H | G_H) = 0.60, P(S_H | G_L) = 0.50
- Bayes-flipped: P(G_H | S_H) = 0.545
- Bayesian posterior P(p(S_H | G_H) > p(S_H | G_L) | data) = 0.66
- χ² independence: χ² = 0.20, p = 0.65
- Pearson r = +0.025 (p = 0.92)

The point estimates lean slightly *against* the popular "more screens →
worse grades" hypothesis — high-GPA students were if anything marginally
heavier screen users — but at n = 20 the formal tests don't provide strong
evidence of dependence in either direction.
