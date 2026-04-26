"""
CS394R Mini Project
Title: Analyzing the Relationship Between Screen Time and GPA
       using Conditional Probability and Bayes' Theorem
Group: Luke Malcom, Judi Cavender, Reyna Salvador, Michelle Aguilera
Date:  April 2026

This script ingests the real survey responses (n = 20) from
"Assessment (Responses).xlsx", parses the free-text screen-time
strings into hours, and runs the full analysis used in the
presentation and report:
  - descriptive statistics
  - Pearson and Spearman correlation
  - 2x2 contingency table at the deck thresholds (GPA 3.5, ST 6h)
  - conditional probabilities and Bayes' theorem
  - chi-square independence test
  - Bayesian Beta-Binomial posterior comparison
  - Chebyshev's inequality on GPA

Outputs:
  screen_time_gpa_data.csv / .xlsx  -- cleaned dataset
  histograms.png, scatter.png, posteriors.png
"""

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import openpyxl

RNG_SEED = 7
np.random.seed(RNG_SEED)

# ------------------------------------------------------------------
# 1. Load and parse raw survey responses
# ------------------------------------------------------------------
SOURCE_XLSX = "Assessment (Responses).xlsx"

def parse_screen_time(value):
    """Convert messy screen-time text/number into hours (float)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).lower().strip()
    # Range like '9-10 hours' or '2-3 hours' -> midpoint
    m_range = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", s)
    if m_range:
        return (float(m_range.group(1)) + float(m_range.group(2))) / 2.0
    h, mn = 0.0, 0.0
    m_h = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b", s)
    if m_h:
        h = float(m_h.group(1))
    m_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|m)\b", s)
    if m_m:
        mn = float(m_m.group(1))
    if h == 0 and mn == 0:
        m_n = re.search(r"(\d+(?:\.\d+)?)", s)
        if m_n:
            return float(m_n.group(1))
        return None
    return h + mn / 60.0


def load_responses(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Form Responses 1"]
    rows = list(ws.iter_rows(values_only=True))
    records = []
    for r in rows[1:]:
        gpa = r[2]
        st_raw = r[3]
        st = parse_screen_time(st_raw)
        if gpa is None or st is None:
            continue
        records.append({
            "gpa": float(gpa),
            "screen_time_raw": str(st_raw),
            "screen_time_hours": round(float(st), 3),
        })
    return pd.DataFrame(records)


df_raw = load_responses(SOURCE_XLSX)
df = df_raw[["gpa", "screen_time_hours"]].copy()
df.insert(0, "student_id", [f"S{i+1:02d}" for i in range(len(df))])
df.to_csv("screen_time_gpa_data.csv", index=False)
df.to_excel("screen_time_gpa_data.xlsx", index=False)
print(f"Loaded n = {len(df)} responses")
print(df)

x = df["screen_time_hours"].values
y = df["gpa"].values
N = len(df)

# ------------------------------------------------------------------
# 2. Descriptive statistics
# ------------------------------------------------------------------
print("\n========== DESCRIPTIVE STATISTICS ==========")
desc = df[["screen_time_hours", "gpa"]].agg(["mean", "median", "var", "std", "min", "max"])
print(desc.round(3))

mean_x, mean_y = float(x.mean()), float(y.mean())
sd_x, sd_y = float(x.std(ddof=1)), float(y.std(ddof=1))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(x, bins=8, color="steelblue", edgecolor="black")
axes[0].axvline(mean_x, color="red", ls="--", label=f"mean={mean_x:.2f}")
axes[0].set_title("Daily Screen Time (hours)"); axes[0].set_xlabel("Hours/day"); axes[0].legend()
axes[1].hist(y, bins=8, color="seagreen", edgecolor="black")
axes[1].axvline(mean_y, color="red", ls="--", label=f"mean={mean_y:.2f}")
axes[1].set_title("GPA distribution"); axes[1].set_xlabel("GPA (0-4)"); axes[1].legend()
plt.tight_layout(); plt.savefig("histograms.png", dpi=140); plt.close()

# ------------------------------------------------------------------
# 3. Correlation and regression
# ------------------------------------------------------------------
print("\n========== CORRELATION & REGRESSION ==========")
cov_xy = float(np.cov(x, y, ddof=1)[0, 1])
pearson_r, pearson_p = stats.pearsonr(x, y)
spearman_r, spearman_p = stats.spearmanr(x, y)
slope, intercept, r_val, p_val, stderr = stats.linregress(x, y)
r_squared = r_val ** 2

z = np.arctanh(pearson_r)
se = 1 / np.sqrt(N - 3)
zcrit = stats.norm.ppf(0.975)
ci_low, ci_high = float(np.tanh(z - zcrit * se)), float(np.tanh(z + zcrit * se))

print(f"Cov(X,Y)        = {cov_xy:.4f}")
print(f"Pearson r       = {pearson_r:.4f}  (p = {pearson_p:.4f})  95% CI [{ci_low:.3f}, {ci_high:.3f}]")
print(f"Spearman rho    = {spearman_r:.4f}  (p = {spearman_p:.4f})")
print(f"Regression      : GPA = {intercept:.3f} + ({slope:.4f}) * screen_time")
print(f"R^2             = {r_squared:.4f}")

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(x, y, color="steelblue", edgecolor="black", s=60)
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, intercept + slope * xs, color="firebrick", lw=2,
        label=f"GPA = {intercept:.2f} + ({slope:.3f})\u00b7ST")
ax.axhline(3.5, color="grey", ls=":", lw=1)
ax.axvline(6.0, color="grey", ls=":", lw=1)
ax.set_xlabel("Daily screen time (hours)")
ax.set_ylabel("GPA")
ax.set_title(f"Screen Time vs GPA  (n={N},  r = {pearson_r:.2f})")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("scatter.png", dpi=140); plt.close()

# ------------------------------------------------------------------
# 4. Conditional probability + Bayes' theorem  (deck thresholds)
# ------------------------------------------------------------------
print("\n========== CONDITIONAL PROBABILITY (BAYES) ==========")
GPA_THRESH = 3.5
ST_THRESH  = 6.0
high_gpa = y >= GPA_THRESH
high_st  = x >= ST_THRESH

n_GH_SH = int(np.sum(high_gpa & high_st))
n_GH_SL = int(np.sum(high_gpa & ~high_st))
n_GL_SH = int(np.sum(~high_gpa & high_st))
n_GL_SL = int(np.sum(~high_gpa & ~high_st))

print(f"Categories: GH=GPA>={GPA_THRESH},  SH=ST>={ST_THRESH}h")
print(f"                  SH       SL")
print(f"  GH (high GPA):  {n_GH_SH:3d}      {n_GH_SL:3d}     row={n_GH_SH+n_GH_SL}")
print(f"  GL (low  GPA):  {n_GL_SH:3d}      {n_GL_SL:3d}     row={n_GL_SH+n_GL_SL}")
print(f"  col totals  :  {n_GH_SH+n_GL_SH:3d}      {n_GH_SL+n_GL_SL:3d}     N={N}")

P_GH = (n_GH_SH + n_GH_SL) / N
P_GL = 1 - P_GH
P_SH = (n_GH_SH + n_GL_SH) / N
P_SL = 1 - P_SH
P_SH_given_GH = n_GH_SH / max(n_GH_SH + n_GH_SL, 1)
P_SH_given_GL = n_GL_SH / max(n_GL_SH + n_GL_SL, 1)
P_GH_given_SH = (P_SH_given_GH * P_GH) / P_SH

print(f"P(GH)              = {P_GH:.3f}")
print(f"P(SH)              = {P_SH:.3f}")
print(f"P(SH | GH)         = {P_SH_given_GH:.3f}")
print(f"P(SH | GL)         = {P_SH_given_GL:.3f}")
print(f"P(GH | SH) (Bayes) = {P_GH_given_SH:.3f}")

chi2, chi_p, dof, exp = stats.chi2_contingency(
    [[n_GH_SH, n_GH_SL], [n_GL_SH, n_GL_SL]], correction=False
)
print(f"Chi-square indep.: chi2 = {chi2:.3f}, p = {chi_p:.4f}")

# ------------------------------------------------------------------
# 5. Bayesian Beta-Binomial posterior comparison
# ------------------------------------------------------------------
print("\n========== BAYESIAN BETA-BINOMIAL ==========")
alpha_prior, beta_prior = 1, 1
a_GH = alpha_prior + n_GH_SH; b_GH = beta_prior + n_GH_SL
a_GL = alpha_prior + n_GL_SH; b_GL = beta_prior + n_GL_SL
post_GH = stats.beta(a_GH, b_GH)
post_GL = stats.beta(a_GL, b_GL)
print(f"Posterior p(SH|GH) ~ Beta({a_GH},{b_GH})  mean={post_GH.mean():.3f}  95% CrI=[{post_GH.ppf(.025):.3f}, {post_GH.ppf(.975):.3f}]")
print(f"Posterior p(SH|GL) ~ Beta({a_GL},{b_GL})  mean={post_GL.mean():.3f}  95% CrI=[{post_GL.ppf(.025):.3f}, {post_GL.ppf(.975):.3f}]")

rng = np.random.default_rng(RNG_SEED)
M = 200_000
s_gh = rng.beta(a_GH, b_GH, size=M)
s_gl = rng.beta(a_GL, b_GL, size=M)
prob_gh_gt_gl = float(np.mean(s_gh > s_gl))
print(f"P(p(SH|GH) > p(SH|GL) | data) = {prob_gh_gt_gl:.4f}")


ps = np.linspace(0, 1, 400)
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(ps, post_GH.pdf(ps), label=f"p(SH | GH)  Beta({a_GH},{b_GH})", color="firebrick", lw=2)
ax.plot(ps, post_GL.pdf(ps), label=f"p(SH | GL)  Beta({a_GL},{b_GL})", color="steelblue", lw=2)
ax.set_xlabel("Probability of high screen time"); ax.set_ylabel("Posterior density")
ax.set_title(f"Beta-Binomial posteriors  \u00b7  P(p_GH > p_GL | data) = {prob_gh_gt_gl:.3f}")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("posteriors.png", dpi=140); plt.close()

# ------------------------------------------------------------------
# 6. Chebyshev's inequality on GPA
# ------------------------------------------------------------------
print("\n========== CHEBYSHEV'S INEQUALITY ==========")
for k in [1.5, 2, 2.5, 3]:
    bound = 1 / (k ** 2)
    empirical = float(np.mean(np.abs(y - mean_y) >= k * sd_y))
    print(f"  k={k}: 1/k^2 = {bound:.3f}  |  empirical = {empirical:.3f}")
print(f"(GPA mean = {mean_y:.3f}, SD = {sd_y:.3f})")
print("\nDONE.")
