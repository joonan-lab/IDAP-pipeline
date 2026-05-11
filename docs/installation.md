# Installation

## Requirements

- Python 3.8-3.11 (recommended for TxGNN/DGL compatibility)
- [OncoKB API token](https://www.oncokb.org/api-access) (free for research use)
- [NCBI PubMed API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/) (recommended)

## Install from GitHub

```bash
git clone https://github.com/joonan-lab/IDAP-pipeline.git
cd IDAP-pipeline
pip install -r requirements.txt
```

## Dependencies

The main dependencies are listed in `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation |
| `requests` | API queries (PubMed, ClinicalTrials.gov) |
| `numpy` | Numerical operations |
| `torch` | TxGNN knowledge graph loading |
| `dgl` | Graph neural network framework |
| `networkx` | Network visualization |
| `matplotlib` | Plotting |
| `reportlab` | PDF report generation |
| `xlsxwriter` | Excel report generation |
| `txgnn` | Biomedical knowledge graph |

## TxGNN Setup

The TxGNN module requires the TxGNN package and its associated data:

```bash
# Installed by requirements.txt from the official GitHub repository
pip install -r requirements.txt

# Or clone from source
git clone https://github.com/mims-harvard/TxGNN.git
```

The knowledge graph data will be automatically downloaded on first run.

## API Tokens

IDAP requires API tokens passed as command-line arguments. **Do not hardcode tokens in source files.**

```bash
# OncoKB: Request at https://www.oncokb.org/api-access
# PubMed: Request at https://www.ncbi.nlm.nih.gov/account/settings/

python main_pipeline.py \
    --oncokb_token YOUR_ONCOKB_TOKEN \
    --pubmed_token YOUR_PUBMED_TOKEN \
    ...
```

!!! tip
    Store tokens in environment variables for convenience:
    ```bash
    export ONCOKB_TOKEN="your_token_here"
    export PUBMED_TOKEN="your_token_here"
    ```
