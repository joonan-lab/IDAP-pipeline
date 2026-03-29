# IDAP: Integrated Drug Annotation Pipeline

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://joonan-lab.github.io/IDAP-pipeline)

A modular evidence integration framework for precision oncology that combines curated knowledge, literature mining, graph-based drug prioritization, and clinical trial evidence to generate patient-level therapeutic hypothesis reports.

## Overview

IDAP takes a MAF file and cancer type as input and integrates four complementary evidence streams:

- **OncoKB** -- Curated variant-drug associations with clinical evidence levels
- **PubMed** -- Literature-derived gene-drug mention counts from abstract-level text mining
- **TxGNN Knowledge Graph** -- Graph-based drug prioritization using a biomedical knowledge graph with mutation-aware heuristic scoring
- **ClinicalTrials.gov** -- Cancer-specific clinical trial metadata

Candidate drugs are ranked using a percentile-normalized combined score that prevents cross-source scale imbalance and rewards convergent multi-source support.

![Pipeline Overview](./image.png)

## Documentation

Full documentation is available at **[joonan-lab.github.io/IDAP-pipeline](https://joonan-lab.github.io/IDAP-pipeline)**

## Quick Start

```bash
# Clone
git clone https://github.com/joonan-lab/IDAP-pipeline.git
cd IDAP-pipeline

# Install dependencies
pip install -r requirements.txt

# Clone required external modules
git clone https://github.com/oncokb/oncokb-annotator.git
git clone https://github.com/mims-harvard/TxGNN.git

# Run
python main_pipeline.py \
    --maf data/test_NSCLC.maf \
    --cancer NSCLC \
    --oncokb_token $ONCOKB_TOKEN \
    --annotator ./oncokb-annotator/MafAnnotator.py \
    --pubmed_token $PUBMED_TOKEN \
    --txgnn_data ./TxGNN/data \
    --txgnn_root ./TxGNN \
    --outdir output/test
```

## API Keys

| Service | How to obtain |
|---------|---------------|
| OncoKB | [oncokb.org/api-access](https://www.oncokb.org/api-access) (free for research) |
| PubMed | [NCBI Account Settings](https://www.ncbi.nlm.nih.gov/account/settings/) |

## Output

IDAP generates per-patient reports including:

- `final_report.xlsx` -- Excel workbook with per-module results and merged drug ranking
- `final_report.pdf` -- PDF summary with visualizations
- `top20_drugs.png` -- Bar chart of top-ranked drugs
- `txgnn_graph.png` -- Gene-drug network visualization

See [Output Format](https://joonan-lab.github.io/IDAP-pipeline/output/) for details.

## Citation

> Ryu Y, Jung H, An JY. IDAP: An integrated literature- and knowledge-graph-driven evidence prioritization pipeline for precision oncology. *Bioinformatics* (2026).

## License

This project is available for academic and research use.
