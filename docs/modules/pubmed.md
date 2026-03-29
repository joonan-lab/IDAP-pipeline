# PubMed Literature Mining Module

## Overview

The PubMed module retrieves abstracts from PubMed and identifies drug mentions through dictionary-based matching against a curated anticancer drug list derived from ChEMBL.

## How It Works

1. Altered genes are extracted from the input MAF file
2. For each gene, PubMed is queried: `"<cancer type> AND <gene> AND (therapy OR treatment OR inhibitor)"`
3. Retrieved abstracts are parsed for drug name mentions
4. Results are aggregated as gene-drug mention counts

## Key Output Fields

| Field | Description |
|-------|-------------|
| `variant` | Gene symbol (Hugo_Symbol) |
| `drug` | Matched drug name (uppercase) |
| `mention_count` | Number of abstract-level co-mentions |

## Drug Dictionary

The curated drug list (`data/chembl_anticancer_drugs.txt`) is derived from ChEMBL and includes drugs identified through:

- Drug indications
- Pharmacological mechanisms of action
- ATC classifications
- Approval status

## Limitations

!!! warning
    Abstract-level co-mentions do not establish therapeutic relevance. This module should be interpreted as **evidence retrieval** rather than causal inference. The current implementation does not perform relation extraction, directionality classification, or study-type filtering.

## Usage

```python
from pubmed_module import run_pubmed

pubmed_df = run_pubmed(
    maf_path="sample.maf",
    cancer_type="NSCLC",
    output_path="pubmed_output.tsv",
    pubmed_token="YOUR_PUBMED_TOKEN"
)
```
