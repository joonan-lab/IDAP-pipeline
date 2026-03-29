# Output Format

## Directory Structure

```
output/<patient_id>/
├── oncokb_output.tsv
├── pubmed_output.tsv
├── txgnn_output.tsv
├── clinicaltrials_output.tsv
├── top20_drugs.png
├── txgnn_graph.png
├── final_report.xlsx
└── final_report.pdf
```

## Excel Report Sheets

The `final_report.xlsx` contains seven sheets:

| Sheet | Description |
|-------|-------------|
| `Summary` | Cancer type, variant count, and top 20 ranked drugs |
| `Performance` | Runtime, API calls, and memory usage per module |
| `OncoKB` | Full OncoKB annotation output |
| `PubMed` | Gene-drug mention counts from PubMed |
| `TxGNN` | Graph-based drug candidates with category labels |
| `ClinicalTrials` | Raw clinical trial records |
| `Merged_Drugs` | Final merged and ranked drug table |

## Merged Drug Table Columns

The `Merged_Drugs` sheet contains the final ranked output:

| Column | Description |
|--------|-------------|
| `drug` | Drug name (uppercase) |
| `combined_score` | Percentile-normalized combined score |
| `tx_pct` | TxGNN percentile |
| `pm_pct` | PubMed percentile |
| `ok_pct` | OncoKB percentile |
| `support_count` | Number of evidence layers (0--3) |
| `clinical_flag` | Has matched clinical trials (0/1) |
| `source` | Evidence source labels (e.g., `TxGNN\|PubMed`) |
| `txgnn_score` | Raw TxGNN score |
| `mention_count` | Raw PubMed mention count |
| `oncokb_score` | Raw OncoKB score |
| `n_clinical_trials` | Number of matched trials |
| `top_nct_id` | NCT ID of highest-phase trial |
| `top_phase` | Highest trial phase |

## PDF Report

The PDF report includes:

1. **Summary page** -- Cancer type, variant count, top drugs
2. **Top 20 drugs bar plot** -- Ranked by combined score
3. **TxGNN network graph** -- Cancer type, mutated genes, and recommended drugs
4. **Clinical trials table** -- Top 30 drugs with trial metadata

## Visualizations

### Top 20 Drugs (`top20_drugs.png`)

Horizontal bar chart of the 20 highest-scoring drugs by combined score.

### TxGNN Network Graph (`txgnn_graph.png`)

Network visualization with:

- **Red nodes**: Cancer type
- **Blue nodes**: Mutated genes
- **Green nodes**: Recommended drugs
- **Edges**: Gene-drug associations from the knowledge graph
