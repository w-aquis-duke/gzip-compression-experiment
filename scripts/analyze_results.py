import csv
from pathlib import Path
from statistics import mean, median, stdev

import matplotlib.pyplot as plt
from scipy import stats

folder = Path(__file__).resolve().parents[1] / "data" / "processed"

with (folder / "compression_results.csv").open(newline="") as file:
    rows = list(csv.DictReader(file))

level_1 = [float(row["level_1_pct"]) for row in rows]
level_9 = [float(row["level_9_pct"]) for row in rows]
differences = [a - b for a, b in zip(level_1, level_9)]

# Check the differences, because this is a paired test.
normality = stats.shapiro(differences)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(differences, bins=10, edgecolor="white")
axes[0].set_xlabel("Level 1 minus level 9 (percentage points)")
axes[0].set_ylabel("Number of books")
axes[0].set_title("Distribution of paired differences")
stats.probplot(differences, dist="norm", plot=axes[1])
axes[1].set_title("Normal Q-Q plot of paired differences")
fig.tight_layout()
fig.savefig(folder / "difference_checks.png", dpi=150)
plt.close(fig)

# H0: The mean paired difference is zero.
# H1: The mean paired difference is not zero.
test = stats.ttest_rel(level_1, level_9)
interval = test.confidence_interval(confidence_level=0.95)
effect_size = mean(differences) / stdev(differences)

# Primary reported test, selected after checking the differences.
wilcoxon = stats.wilcoxon(differences, alternative="two-sided", method="exact")

summary = f"""Gzip level 1 versus level 9
Books: {len(rows)}
Significance level: 0.05 (two-sided)

Mean level 1 size: {mean(level_1):.2f}% of original
Mean level 9 size: {mean(level_9):.2f}% of original
Mean difference: {mean(differences):.2f} percentage points
Median difference: {median(differences):.2f} percentage points

Primary reported test: Wilcoxon signed-rank
W-statistic: {wilcoxon.statistic:.0f}
p-value: {wilcoxon.pvalue:.3g}
Selected after finding evidence against normality.
Its null concerns paired differences symmetric about zero.
A median-shift interpretation requires symmetry, which was not established.

Secondary analysis: originally planned paired t-test
Approximate 95% mean-difference confidence interval: [{interval.low:.2f}, {interval.high:.2f}] percentage points
t-statistic: {test.statistic:.3f}
Degrees of freedom: {test.df:.0f}
p-value: {test.pvalue:.3g}
Paired effect size (dz): {effect_size:.3f}

Shapiro-Wilk p-value for differences: {normality.pvalue:.3g}
Review difference_checks.png alongside this normality check.
A positive difference means level 9 produced smaller files.
The inference assumes the sampled books provide independent pairs.
"""

if normality.pvalue < 0.05:
    summary += "Normality check flags a departure from normality. Discuss the plots and t-test robustness in the report.\n"

print(summary)
(folder / "analysis_results.txt").write_text(summary)
