# Single Sample Analysis

## Example: NSCLC Patient

```bash
python main_pipeline.py \
    --maf data/test_NSCLC.maf \
    --cancer NSCLC \
    --oncokb_token $ONCOKB_TOKEN \
    --annotator /path/to/oncokb-annotator/MafAnnotator.py \
    --pubmed_token $PUBMED_TOKEN \
    --txgnn_data /path/to/txgnn/data \
    --txgnn_root /path/to/TxGNN \
    --outdir output/NSCLC_001 \
    --patient_id NSCLC_001
```

## Expected Output

```
🧬 Input cancer type = NSCLC
🔧 TxGNN friendly disease name = lung cancer

==========================
1) Running OncoKB annotator
==========================
...
==========================
2) Running PubMed analysis
==========================
...
==========================
3) Running TxGNN
==========================
...
==========================
4) Searching ClinicalTrials.gov
==========================
...
==========================
5) Merging all results
==========================
...

📊 PERFORMANCE SUMMARY
============================================================
Total Runtime: 162.45 sec
Total API Calls: 234
Peak Memory: 918.00 MB
Total Drugs: 87
============================================================
```

## Interpreting Results

1. Open `final_report.xlsx` and go to the `Merged_Drugs` sheet
2. Drugs are sorted by `combined_score` (highest first)
3. Check `support_count` -- drugs with 2+ sources have stronger convergent evidence
4. Check `source` column to see which evidence layers contribute
5. Use `top_nct_id` to look up relevant clinical trials on ClinicalTrials.gov

!!! tip
    Focus on the top 10--20 candidates with `support_count >= 2` as starting points for expert review.
