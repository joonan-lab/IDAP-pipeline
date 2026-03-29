# TxGNN Knowledge Graph Module

## Overview

The TxGNN module maps altered genes onto a [TxGNN](https://github.com/mims-harvard/TxGNN)-derived biomedical knowledge graph to identify drug candidates through disease-drug, drug-target, and FDA approval relationships.

## How It Works

1. The TxGNN knowledge graph is loaded (17,079 diseases, 7,957 drugs, 27,610 genes/proteins)
2. For a given cancer type, drugs are identified through:
    - **Indication edges**: current treatments for the cancer type
    - **Drug-protein edges**: drugs targeting the mutated genes
    - **FDA approval**: drugs approved for other diseases (repurposing candidates)
3. Candidates are scored using mutation-aware heuristic rules

## Drug Categories

| Category | Description | Base Score |
|----------|-------------|-----------|
| Repurposing Priority | FDA-approved for other diseases + targets mutated gene | 20.0 |
| Investigational Targeting | Targets mutated gene, not FDA-approved | 10.0 |
| Current Indication | Already indicated for this cancer type | 5.0 |
| Disease-Related | Connected to cancer in the knowledge graph | 2.0 |

Multi-gene targeting bonuses are added when a drug targets more than one mutated gene.

## Key Output Fields

| Field | Description |
|-------|-------------|
| `drug` | Drug name (uppercase) |
| `txgnn_score` | Heuristic prioritization score |
| `category` | Drug category label |
| `repurposing` | Whether it is a repurposing candidate |
| `mutation_target` | Whether drug targets a mutated gene |
| `fda_approved` | Whether drug is FDA-approved for any indication |
| `connected_genes` | Mutated genes targeted by this drug |

!!! note
    This module uses the TxGNN knowledge graph as a **structured resource** for candidate discovery, not as a variant-specific deep-learning inference engine.

## Usage

```python
from txgnn_module import run_txgnn

txgnn_df = run_txgnn(
    maf_path="sample.maf",
    cancer_type="lung cancer",
    output_path="txgnn_output.tsv",
    data_folder="./data",
    txgnn_root="./TxGNN"
)
```
