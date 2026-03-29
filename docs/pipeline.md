# Pipeline Overview

IDAP processes somatic mutation data through four independent evidence modules, merges the results, and generates a ranked report.

## Architecture

```
Input: MAF file + Cancer type
         │
         ├──→ [1] OncoKB Annotation
         │         Curated variant-drug associations
         │
         ├──→ [2] PubMed Literature Mining
         │         Gene-drug co-mention counts
         │
         ├──→ [3] TxGNN Knowledge Graph
         │         Graph-based drug prioritization
         │
         └──→ [4] ClinicalTrials.gov
                   Trial metadata for candidate drugs
         │
         ▼
    [5] Evidence Merging & Scoring
         Percentile-normalized combined score
         │
         ▼
    [6] Report Generation
         Excel + PDF patient-level reports
```

## Module Execution Order

1. **OncoKB Annotation** -- Annotates variants using the OncoKB MAF Annotator to obtain clinical evidence levels and drug associations.

2. **PubMed Literature Mining** -- Queries PubMed for abstracts matching each altered gene and the cancer type, then performs dictionary-based drug name matching against a curated ChEMBL-derived anticancer drug list.

3. **TxGNN Knowledge Graph** -- Maps altered genes onto a TxGNN-derived biomedical knowledge graph to identify drug candidates through disease-drug indication edges, drug-target relationships, and FDA-approved repurposing opportunities.

4. **ClinicalTrials.gov** -- Queries the ClinicalTrials.gov v2 REST API for each candidate drug in the specified cancer context.

5. **Evidence Merging** -- All module outputs are merged on normalized drug names. The combined score is computed using within-sample percentile normalization (see [Scoring](scoring.md)).

6. **Report Generation** -- Produces an Excel workbook with per-module sheets and a merged drug ranking, plus a PDF summary with visualizations.

## Data Flow

Each module produces a TSV file that feeds into the final merge:

| Module | Output Key Columns | Merge Key |
|--------|-------------------|-----------|
| OncoKB | `drug`, `oncokb_level`, `oncokb_score` | Normalized drug name |
| PubMed | `drug`, `mention_count` | Normalized drug name |
| TxGNN | `drug`, `txgnn_score`, `category` | Normalized drug name |
| ClinicalTrials | `drug`, `n_clinical_trials`, `top_phase` | Normalized drug name |
