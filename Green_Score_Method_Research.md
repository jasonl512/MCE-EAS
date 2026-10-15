# Green Score Method: Initial Research Basis

## Purpose

This note documents the current basis for the first MCE-EAS Green Score prototype. The equal-weight formula is an initial baseline for testing, not the final validated model.

## Recommended first prototype

MCE-EAS currently uses four factors:

- Air quality
- Tree cover
- Heat vulnerability
- Building-energy efficiency

Because the source datasets use different units, every factor must first be converted to a common 0-100 scale. Each converted score should point in the same direction, where a higher value always means a better condition.

For an indicator where a larger raw value is better:

`score = 100 * (value - minimum) / (maximum - minimum)`

For an indicator where a smaller raw value is better:

`score = 100 * (maximum - value) / (maximum - minimum)`

The first baseline can then use:

`Green Score = 0.25(Air Quality Score) + 0.25(Tree Cover Score) + 0.25(Heat Score) + 0.25(Building-Energy Score)`

The four weights add to 1.00. Equal weights are useful for the first prototype because the team does not yet have enough evidence to claim that one factor should count more than another.

## Evidence from recent work

| Source | Method used or discussed | How it supports MCE-EAS |
|---|---|---|
| Desogus, Bompard, and Grosso (2024) | Discusses normalization, equal weighting, statistical weighting, and expert/participatory weighting for an urban energy composite index. It notes that Min-Max normalization with equal-weight additive aggregation is a common, easy-to-replicate approach. | Supports using Min-Max normalization and equal weights as a transparent baseline, followed by tests with other weights. |
| U.S. EPA EJScreen Technical Documentation v2.3 (2024) | Converts indicators to comparable statistical forms such as percentiles or z-scores and averages standardized indicators for demographic indexes. | Provides an official example of standardizing indicators before combining them and of using an unweighted average for an index. |
| Price, Mengersen, Rigby, and Fiévez (2024) | Identifies equal-weight percentile ranking and PCA as common vulnerability-index methods, then proposes health-outcome-based weights. | Supports equal weighting as a baseline and suggests a later comparison with data-driven weights. |
| Zhang et al. (2024) | Combines Analytic Hierarchy Process (expert judgment) with an entropy method (data-driven weighting) for an urban residential environment index. | Provides one possible future method if the team later wants weights based on both expert judgment and the data. |

## Recommended development plan

1. Build the equal-weight version first and clearly label it as the baseline.
2. Record the minimum, maximum, direction, year, and geographic unit used for every factor.
3. Test whether district rankings change when the weights change.
4. Compare the baseline with at least one alternative, such as PCA, entropy weighting, or documented expert weights.
5. Do not call any weighting method final until the team explains why it matches the intended use of the system.

## Important limitation

Equal weights do not prove that the four factors are equally important in the real world. They only provide a neutral and reproducible starting point. Also, Heat Vulnerability Index may already contain environmental or social variables related to the other factors, so the team should check its components to avoid counting the same information twice.

## References

[1] E. Desogus, E. Bompard, and D. Grosso, "A Composite Index for Tracking the Evolution towards Energy Transition at Urban Scale: The Turin Case Study," *Energies*, vol. 17, no. 6, art. 1281, 2024. https://doi.org/10.3390/en17061281

[2] U.S. Environmental Protection Agency, *EJScreen Technical Documentation for Version 2.3*, July 31, 2024. https://www.epa.gov/system/files/documents/2024-07/ejscreen-tech-doc-version-2-3.pdf

[3] A. Price, K. Mengersen, M. Rigby, and P. Fiévez, "Creating a Spatial Vulnerability Index for Environmental Health," arXiv:2403.14954, 2024. https://doi.org/10.48550/arXiv.2403.14954

[4] S. Zhang, Y. Xia, Z. Li, X. Li, Y. Wu, P. Liu, and S. Du, "An Assessment of Urban Residential Environment Quality Based on Multi-Source Geospatial Data: A Case Study of Beijing, China," *Land*, vol. 13, no. 6, art. 823, 2024. https://doi.org/10.3390/land13060823
