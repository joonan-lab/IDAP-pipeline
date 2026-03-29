# OncoKB Annotation Module

## Overview

The OncoKB module annotates somatic variants using the [OncoKB MAF Annotator](https://github.com/oncokb/oncokb-annotator) to obtain clinically actionable variant-drug associations.

## How It Works

1. Input MAF file is processed under the GRCh38 reference genome
2. Cancer type is specified for disease-specific evidence levels
3. The annotator queries the OncoKB API for each variant
4. Output includes oncogenicity, actionability levels, and drug associations

## Key Output Fields

| Field | Description |
|-------|-------------|
| `ONCOGENIC` | Oncogenicity classification |
| `HIGHEST_LEVEL` | Highest therapeutic evidence level |
| `VARIANT_IN_ONCOKB` | Whether the variant exists in OncoKB |
| `Drugs` | Associated drug names |
| `oncokb_level` | Evidence level (1, 2, 3A, 3B, 4, R1, R2) |
| `oncokb_score` | Numeric score mapped from evidence level |

## API Token

An OncoKB API token is required. Request one at [oncokb.org/api-access](https://www.oncokb.org/api-access) (free for research use).

## Usage

```python
from oncokb_module import run_oncokb_and_extract

oncokb_df = run_oncokb_and_extract(
    maf_path="sample.maf",
    cancer_type="Non-Small Cell Lung Cancer",
    output_tsv_path="oncokb_output.tsv",
    annotator_path="/path/to/MafAnnotator.py",
    oncokb_api_token="YOUR_TOKEN"
)
```
