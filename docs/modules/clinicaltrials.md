# ClinicalTrials.gov Module

## Overview

The ClinicalTrials module queries the [ClinicalTrials.gov v2 REST API](https://clinicaltrials.gov/api/v2/studies) to retrieve registered clinical trials for each candidate drug in the specified cancer context.

## How It Works

1. All candidate drugs from PubMed and TxGNN modules are collected
2. For each drug, the API is queried: `"<drug name> AND <cancer type>"`
3. Up to 200 records per drug are retrieved
4. A per-drug trial summary is computed (total trials, highest-phase trial)

## Key Output Fields

### Raw output (`clinicaltrials_output.tsv`)

| Field | Description |
|-------|-------------|
| `drug` | Drug name |
| `nct_id` | National Clinical Trial identifier |
| `title` | Brief study title |
| `condition` | Reported disease conditions |
| `phase` | Trial phase (Phase 1--4) |
| `status` | Recruitment status |

### Summary (merged into final report)

| Field | Description |
|-------|-------------|
| `n_clinical_trials` | Total number of matched trials |
| `top_nct_id` | NCT ID of the highest-phase trial |
| `top_phase` | Phase of the highest-phase trial |
| `top_title` | Title of the highest-phase trial |

## Phase Priority

Trials are ranked by phase for the summary:

```
Phase 4 > Phase 3 > Phase 2 > Phase 1
```

## Usage

```python
from clinicaltrials_module import run_clinical_trials, build_trial_summary_table

clinical_df = run_clinical_trials(
    drug_list=["FOSTAMATINIB", "SORAFENIB"],
    cancer_type="lung cancer",
    output_path="clinicaltrials_output.tsv"
)

summary_df = build_trial_summary_table(clinical_df)
```
