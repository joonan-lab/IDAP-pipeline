# API Reference

## Main Pipeline

### `run_pipeline()`

```python
run_pipeline(
    maf_path,           # Path to input MAF file
    cancer_type,        # Cancer type abbreviation (e.g., "NSCLC")
    oncokb_token,       # OncoKB API token
    annotator_path,     # Path to MafAnnotator.py
    pubmed_token,       # PubMed API key
    data_folder,        # TxGNN data folder path
    txgnn_root,         # TxGNN package root path
    output_dir,         # Output directory
    patient_id=None     # Optional patient identifier
)
```

Executes the full IDAP pipeline: OncoKB annotation, PubMed mining, TxGNN graph-based prioritization, ClinicalTrials.gov query, evidence merging, and report generation.

---

## Module Functions

### OncoKB Module

```python
from oncokb_module import run_oncokb_and_extract

oncokb_df = run_oncokb_and_extract(
    maf_path,           # Path to MAF file
    cancer_type,        # OncoKB-formatted cancer name
    output_tsv_path,    # Output TSV path
    annotator_path,     # Path to MafAnnotator.py
    oncokb_api_token    # OncoKB API token
)
```

**Returns**: DataFrame with variant-level annotations including evidence levels and drug associations.

---

### PubMed Module

```python
from pubmed_module import run_pubmed

pubmed_df = run_pubmed(
    maf_path,                   # Path to MAF file
    cancer_type,                # Cancer type for query
    output_path,                # Output TSV path
    drug_list_path=None,        # Path to drug dictionary (default: data/chembl_anticancer_drugs.txt)
    max_workers=4,              # Number of parallel threads
    pubmed_token=None           # PubMed API key
)
```

**Returns**: DataFrame with columns `[variant, drug, mention_count]`.

---

### TxGNN Module

```python
from txgnn_module import run_txgnn

txgnn_df = run_txgnn(
    maf_path,                   # Path to MAF file
    cancer_type,                # Cancer type (disease name form)
    output_path,                # Output TSV path
    data_folder="./data",       # TxGNN data folder
    txgnn_root="./TxGNN",      # TxGNN package root
    top_k=50,                   # Maximum candidates to return
    mode="repurposing"          # "repurposing" or "all"
)
```

**Returns**: DataFrame with columns `[drug, txgnn_score, category, repurposing, current_use, mutation_target, fda_approved, connected_genes, num_genes]`.

---

### ClinicalTrials Module

```python
from clinicaltrials_module import run_clinical_trials, build_trial_summary_table

clinical_df = run_clinical_trials(
    drug_list,          # List of drug names to query
    cancer_type,        # Cancer type for query
    output_path         # Output TSV path
)

summary_df = build_trial_summary_table(clinical_df)
```

**Returns**: `clinical_df` with raw trial records; `summary_df` with per-drug trial summaries.

---

## Merging Function

```python
from main_pipeline import merge_all_results

merged_df = merge_all_results(
    oncokb_df,              # OncoKB output DataFrame
    pubmed_df,              # PubMed output DataFrame
    txgnn_df,               # TxGNN output DataFrame
    clinical_summary_df     # Clinical trial summary DataFrame
)
```

**Returns**: Merged DataFrame sorted by `combined_score` (descending), with percentile-normalized scores and evidence metadata.
