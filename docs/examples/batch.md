# Batch Analysis

## Running Multiple Samples

For cohort-level analysis, use a shell loop:

```bash
#!/bin/bash

CANCER="BRCA"
MAF_DIR="data/maf_files"
OUT_DIR="output/${CANCER}"

for maf_file in ${MAF_DIR}/*.maf; do
    sample_id=$(basename "$maf_file" .maf)
    echo "Processing: $sample_id"

    python main_pipeline.py \
        --maf "$maf_file" \
        --cancer "$CANCER" \
        --oncokb_token "$ONCOKB_TOKEN" \
        --annotator /path/to/MafAnnotator.py \
        --pubmed_token "$PUBMED_TOKEN" \
        --txgnn_data /path/to/txgnn/data \
        --txgnn_root /path/to/TxGNN \
        --outdir "${OUT_DIR}/${sample_id}" \
        --patient_id "$sample_id"
done
```

## Aggregating Results

After batch processing, you can aggregate the merged drug tables:

```python
import pandas as pd
import os
import glob

cancer = "BRCA"
base_dir = f"output/{cancer}"
all_data = []

for sample_dir in sorted(glob.glob(f"{base_dir}/*")):
    xlsx_path = os.path.join(sample_dir, "final_report.xlsx")
    if os.path.exists(xlsx_path):
        df = pd.read_excel(xlsx_path, sheet_name="Merged_Drugs")
        df["sample_id"] = os.path.basename(sample_dir)
        all_data.append(df)

combined = pd.concat(all_data, ignore_index=True)
print(f"Total: {combined['sample_id'].nunique()} samples, {len(combined)} drug-sample pairs")

# Top drugs across cohort
top_drugs = (
    combined.groupby("drug")["combined_score"]
    .agg(["mean", "count"])
    .sort_values("mean", ascending=False)
    .head(20)
)
print(top_drugs)
```

## Performance Considerations

| Samples | Estimated Time | Notes |
|---------|---------------|-------|
| 1 | ~3 minutes | Single run |
| 10 | ~30 minutes | Sequential |
| 50 | ~2.5 hours | Sequential |

Runtime scales linearly with mutation burden. ClinicalTrials.gov queries are the main bottleneck.

!!! tip
    For large cohorts, consider running samples in parallel using GNU `parallel` or a job scheduler.
