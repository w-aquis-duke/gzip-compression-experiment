from math import ceil
from statsmodels.stats.power import TTestPower
import numpy as np
from scipy.stats import wilcoxon

# Planning assumptions for a two-sided paired t-test.
# Effect size is standardized, not the percentage of space saved.
effect_size = 0.5
alpha = 0.05
power = 0.80

analysis = TTestPower()
sample_size = analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    alternative="two-sided",
)

# Round up because we need whole books.
print(f"Required books: {ceil(sample_size)}")
print("Each book will be compressed at both levels.")

# Hypothetical Wilcoxon power, not power based on our observed results.
# Assume independent normal differences with mean 0.5 and SD 1.
num_books = 50
simulations = 10000
rng = np.random.default_rng(511)
differences = rng.normal(effect_size, 1, size=(simulations, num_books))
p_values = wilcoxon(differences, axis=1, alternative="two-sided", method="exact").pvalue
estimated_power = np.mean(p_values < alpha)
print(f"Wilcoxon power with {num_books} books: {estimated_power:.1%}")
print("Assumes symmetric normal differences; does not resolve the observed skew.")
