"""
CS394R Mini Project
Title: Analyzing the Relationship Between Screen Time and GPA
       using Conditional Probability and Bayes' Theorem
Group: Luke Malcom, Judi Cavender, Reyna Salvador, Michelle Aguilera
Date:  April 2026

Pipeline matches the slide deck exactly:

  1. Data Collection -- read the Google Forms responses (n = 20)
  2. Convert raw screen-time strings into decimal hours
  3. Categorise each respondent into one of four sets using the deck's
     thresholds:
         High GPA  (G_H): GPA >= 3.5
         Low  GPA  (G_L): GPA <  3.5
         High ST   (S_H): screen time >= 6 hours
         Low  ST   (S_L): screen time <  6 hours
  4. Build a 2x2 contingency table
  5. Compute conditional probabilities
  6. Apply Bayes' theorem to obtain  P(G_H | S_H)
"""

import re
import openpyxl
import pandas as pd

GPA_THRESH = 3.5
ST_THRESH  = 6.0
SOURCE_XLSX = "Assessment (Responses).xlsx"


# ------------------------------------------------------------------
# 1. Load and convert raw survey responses
# ------------------------------------------------------------------
def parse_screen_time(value):
    """Convert messy screen-time text/number into decimal hours."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).lower().strip()
    # Range like "9-10 hours" or "2-3 hours" -> midpoint
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
        st  = parse_screen_time(r[3])
        if gpa is not None and st is not None:
            records.append({
                "gpa": float(gpa),
                "screen_time_hours": round(st, 3),
            })
    return pd.DataFrame(records)


df = load_responses(SOURCE_XLSX)
df.insert(0, "student_id", [f"S{i+1:02d}" for i in range(len(df))])
df.to_csv("screen_time_gpa_data.csv", index=False)
df.to_excel("screen_time_gpa_data.xlsx", index=False)

print(f"Loaded n = {len(df)} responses\n")
print(df.to_string(index=False))

# ------------------------------------------------------------------
# 2. Categorise into four sets and build the 2x2 contingency table
# ------------------------------------------------------------------
high_gpa = df["gpa"]               >= GPA_THRESH
high_st  = df["screen_time_hours"] >= ST_THRESH

n_GH_SH = int((  high_gpa &  high_st ).sum())
n_GH_SL = int((  high_gpa & ~high_st ).sum())
n_GL_SH = int(( ~high_gpa &  high_st ).sum())
n_GL_SL = int(( ~high_gpa & ~high_st ).sum())
N       = len(df)

print("\n========== CONTINGENCY TABLE ==========")
print(f"  G_H  =  GPA >= {GPA_THRESH}")
print(f"  S_H  =  screen time >= {ST_THRESH} h\n")
print(f"               S_H    S_L    Row")
print(f"   G_H        {n_GH_SH:3d}    {n_GH_SL:3d}    {n_GH_SH + n_GH_SL:3d}")
print(f"   G_L        {n_GL_SH:3d}    {n_GL_SL:3d}    {n_GL_SH + n_GL_SL:3d}")
print(f"   Col total  {n_GH_SH + n_GL_SH:3d}    {n_GH_SL + n_GL_SL:3d}    {N:3d}")

# ------------------------------------------------------------------
# 3. Conditional probabilities
# ------------------------------------------------------------------
P_GH          = (n_GH_SH + n_GH_SL) / N
P_GL          = 1 - P_GH
P_SH          = (n_GH_SH + n_GL_SH) / N
P_SL          = 1 - P_SH
P_SH_given_GH = n_GH_SH / (n_GH_SH + n_GH_SL)
P_SH_given_GL = n_GL_SH / (n_GL_SH + n_GL_SL)

print("\n========== CONDITIONAL PROBABILITIES ==========")
print(f"  P(G_H)        = {P_GH:.3f}")
print(f"  P(G_L)        = {P_GL:.3f}")
print(f"  P(S_H)        = {P_SH:.3f}")
print(f"  P(S_L)        = {P_SL:.3f}")
print(f"  P(S_H | G_H)  = {P_SH_given_GH:.3f}")
print(f"  P(S_H | G_L)  = {P_SH_given_GL:.3f}")

# ------------------------------------------------------------------
# 4. Bayes' theorem:  P(G_H | S_H) = P(S_H | G_H) * P(G_H) / P(S_H)
# ------------------------------------------------------------------
P_GH_given_SH = (P_SH_given_GH * P_GH) / P_SH

print("\n========== BAYES' THEOREM ==========")
print(f"  P(G_H | S_H)  =  P(S_H | G_H) * P(G_H) / P(S_H)")
print(f"                =  ({P_SH_given_GH:.3f} * {P_GH:.3f}) / {P_SH:.3f}")
print(f"                =  {P_GH_given_SH:.3f}")
print("\nDONE.")
