# Quick Start

## Basic Usage

Run the full IDAP pipeline on a single MAF file:

```bash
python main_pipeline.py \
    --maf path/to/sample.maf \
    --cancer NSCLC \
    --oncokb_token YOUR_ONCOKB_TOKEN \
    --annotator path/to/oncokb-annotator/MafAnnotator.py \
    --pubmed_token YOUR_PUBMED_TOKEN \
    --txgnn_data path/to/txgnn/data \
    --txgnn_root path/to/TxGNN \
    --outdir output/sample_001 \
    --patient_id sample_001
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--maf` | Yes | Path to input MAF file |
| `--cancer` | Yes | Cancer type abbreviation (e.g., `NSCLC`, `BRCA`, `COAD`, `GBM`, `PDAC`) |
| `--oncokb_token` | Yes | OncoKB API token |
| `--annotator` | Yes | Path to OncoKB `MafAnnotator.py` |
| `--pubmed_token` | Yes | NCBI PubMed API key |
| `--txgnn_data` | Yes | Path to TxGNN data folder |
| `--txgnn_root` | Yes | Path to TxGNN package root |
| `--outdir` | No | Output directory (default: `output`) |
| `--patient_id` | No | Patient identifier for the report |

## Supported Cancer Types

| Abbreviation | Full Name |
|-------------|-----------|
| `NSCLC` | Non-Small Cell Lung Cancer |
| `LUAD` | Lung Adenocarcinoma |
| `LUSC` | Lung Squamous Cell Carcinoma |
| `BRCA` | Breast Invasive Carcinoma |
| `COAD` | Colon Adenocarcinoma |
| `CRC` | Colon Adenocarcinoma |
| `GBM` | Glioblastoma Multiforme |
| `PDAC` | Pancreatic Adenocarcinoma |
| `SKCM` | Melanoma |
| `OV` | Ovarian Cancer |
| `HNSC` | Head and Neck Cancer |

## Output

After a successful run, the output directory contains:

```
output/sample_001/
├── oncokb_output.tsv          # OncoKB variant annotations
├── pubmed_output.tsv          # PubMed gene-drug mention counts
├── txgnn_output.tsv           # TxGNN graph-based drug candidates
├── clinicaltrials_output.tsv  # Clinical trial metadata
├── top20_drugs.png            # Bar plot of top 20 drugs
├── txgnn_graph.png            # Gene-drug network visualization
├── final_report.xlsx          # Full Excel report (7 sheets)
└── final_report.pdf           # PDF summary report
```

See [Output Format](output.md) for detailed descriptions of each file.
