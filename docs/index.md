# IDAP: Integrated Drug Annotation Pipeline

**A modular evidence integration framework for precision oncology**

---

IDAP combines four complementary evidence streams to prioritize therapeutic hypotheses for cancer patients based on somatic mutation data:

- **OncoKB** -- Curated variant-drug associations with defined evidence levels
- **PubMed** -- Literature-derived gene-drug mention evidence
- **TxGNN Knowledge Graph** -- Graph-based drug prioritization using a biomedical knowledge graph
- **ClinicalTrials.gov** -- Cancer-specific clinical trial metadata

Given a cancer type and a MAF file, IDAP generates patient-level reports summarizing detected variants, ranked therapeutic hypotheses, supporting evidence layers, and relevant clinical trials.

## Key Features

- **Multi-source evidence integration** across curated, literature, graph-based, and trial-linked data
- **Percentile-normalized scoring** to prevent cross-source scale imbalance
- **Automated report generation** with tabular and visual summaries (Excel + PDF)
- **Modular architecture** allowing independent use or extension of each evidence module

## Overview

![IDAP Pipeline](https://raw.githubusercontent.com/joonan-lab/IDAP-pipeline/main/image.png)

## Quick Links

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [Pipeline Overview](pipeline.md)
- [Scoring Method](scoring.md)
- [Citation](citation.md)

## Citation

If you use IDAP in your research, please cite:

> Ryu Y, Jung H, An JY. IDAP: An integrated literature- and knowledge-graph-driven evidence prioritization pipeline for precision oncology. *Bioinformatics* (2026).
