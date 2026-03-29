# Scoring Method

## Combined Score

IDAP ranks candidate drugs using a **scale-aware combined score** based on within-sample percentile normalization and fixed evidence bonuses.

### Problem

The three evidence sources operate on very different numeric scales:

- `txgnn_score`: 2 -- 146 (heuristic graph score)
- `mention_count`: 1 -- 67 (PubMed abstract co-mentions)
- `oncokb_score`: -5 -- 10 (curated evidence level mapping)

A naive weighted sum would be dominated by whichever source has the widest range.

### Solution: Percentile Normalization

Each component score is first converted to a **within-sample percentile** rank, producing values in [0, 1]:

```
tx_pct  = percentile_rank(txgnn_score)
pm_pct  = percentile_rank(mention_count)
ok_pct  = percentile_rank(oncokb_score)
```

### Score Formula

The final combined score is:

```
combined_score = 0.50 * tx_pct
               + 0.40 * pm_pct
               + 0.10 * ok_pct
               + 0.20 * max(0, support_count - 1)
               + 0.30 * I(oncokb_score > 0)
               + 0.05 * clinical_flag
```

Where:

| Term | Description |
|------|-------------|
| `tx_pct` | Within-sample percentile of TxGNN graph score |
| `pm_pct` | Within-sample percentile of PubMed mention count |
| `ok_pct` | Within-sample percentile of OncoKB score |
| `support_count` | Number of evidence layers with positive signal (0--3) |
| `I(oncokb_score > 0)` | Binary indicator for any curated OncoKB support |
| `clinical_flag` | Binary indicator for matched ClinicalTrials.gov metadata |

### Weight Rationale

| Weight | Component | Rationale |
|--------|-----------|-----------|
| 0.50 | Graph (TxGNN) | Largest weight because graph captures structured biological relationships and repurposing opportunities |
| 0.40 | Literature (PubMed) | Second largest; literature provides complementary evidence not yet in curated databases |
| 0.10 | Curated (OncoKB) | Smallest percentile weight because curated evidence is sparse; its importance is captured by the fixed 0.30 bonus |
| 0.20 | Convergence bonus | Rewards drugs supported by 2+ evidence sources |
| 0.30 | Curated bonus | Ensures any OncoKB-supported drug is substantially boosted |
| 0.05 | Trial bonus | Modest bonus for drugs with registered clinical trials |

### Sensitivity Analysis

A sensitivity analysis across seven alternative weight configurations showed that the default weights achieve the best balance of multi-source convergence and trial linkage among top-ranked candidates. See the manuscript Supplementary Materials for details.

!!! warning
    The combined score is a **heuristic ranking** and was not trained on clinical outcomes. It is designed to support evidence triage, not to provide clinical recommendations.

## OncoKB Evidence Level Mapping

OncoKB evidence levels are converted to numeric scores:

| Level | Score | Meaning |
|-------|-------|---------|
| 1 | 10.0 | FDA-recognized biomarker |
| 2 | 8.0 | Standard care biomarker |
| 3A | 6.0 | Compelling clinical evidence |
| 3B | 4.0 | Standard care or investigational in another tumor type |
| 4 | 2.0 | Compelling biological evidence |
| R1 | -5.0 | Standard care resistance biomarker |
| R2 | -3.0 | Investigational resistance biomarker |

## TxGNN Heuristic Score

The TxGNN module assigns scores based on drug categories:

| Category | Base Score | Description |
|----------|-----------|-------------|
| Repurposing Priority | 20.0 | FDA-approved for other diseases + targets mutated gene |
| Investigational Targeting | 10.0 | Targets mutated gene but not FDA-approved |
| Current Indication | 5.0 -- 8.0 | Already indicated for this cancer type |
| Disease-Related | 2.0 | Connected to cancer in the knowledge graph |

Additional bonuses are given for drugs targeting multiple mutated genes.
