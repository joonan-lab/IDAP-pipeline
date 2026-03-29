import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

# ==========================
# 1. 약물 리스트 로드
# ==========================
def load_drug_list(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        drugs = [line.strip().lower() for line in f.readlines() if line.strip()]
    return drugs


# ==========================
# 2. PubMed 검색 (단일 gene)
# ==========================
def fetch_pubmed_abstracts(query, retmax=100, api_key=None):
    base_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    base_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "api_key": api_key
    }

    try:
        search = requests.get(base_search, params=params, timeout=10).json()
        id_list = search.get("esearchresult", {}).get("idlist", [])
    except:
        return []

    if not id_list:
        return []

    # ----- 2) Fetch -----
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
        "api_key": api_key
    }

    try:
        r = requests.get(base_fetch, params=fetch_params, timeout=10)
        xml_text = r.text
        if not xml_text.strip().startswith("<"):
            return []
        root = ET.fromstring(xml_text)
    except:
        return []

    # ----- 3) Parse -----
    abstracts = []
    for art in root.findall(".//PubmedArticle"):
        abst = art.find(".//AbstractText")
        if abst is not None and abst.text:
            abstracts.append(abst.text)

    return abstracts


# ==========================
# 3. 약물 매칭
# ==========================
def extract_drugs_from_abstract(text, drug_list):
    if not text:
        return []
    found = {drug for drug in drug_list if drug in text.lower()}
    return list(found)


# ==========================
# 4. MAF → 유전자 리스트
# ==========================
def load_genes_from_maf(maf_path):
    maf = pd.read_csv(maf_path, sep="\t", comment="#", low_memory=False)
    genes = sorted(maf["Hugo_Symbol"].dropna().unique().tolist())
    return genes


# ==========================
# 5. 병렬 처리 1 gene 작업
# ==========================
def process_gene(gene, cancer_type, drug_list, pubmed_token):
    query = f"{cancer_type} AND {gene} AND (therapy OR treatment OR inhibitor)"
    abstracts = fetch_pubmed_abstracts(query, api_key=pubmed_token)

    matched = []
    for abs_text in abstracts:
        matched.extend(extract_drugs_from_abstract(abs_text, drug_list))

    return gene, matched


# ==========================
# 6. 기존 run_pubmed() 완전 대체 (인터페이스 동일)
# ==========================
def run_pubmed(maf_path, cancer_type, output_path,
               drug_list_path=None,
               max_workers=4,
               pubmed_token=None):

    if drug_list_path is None:
        drug_list_path = os.path.join(os.path.dirname(__file__), "data", "chembl_anticancer_drugs.txt")

    print("🔍 Loading drug list ...")
    drug_list = load_drug_list(drug_list_path)

    print(f"🔍 Loading genes from MAF: {maf_path}")
    gene_list = load_genes_from_maf(maf_path)

    print(f"📡 Running PubMed search using {max_workers} threads ...")

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = {
            executor.submit(process_gene, gene, cancer_type, drug_list, pubmed_token): gene
            for gene in gene_list
        }

        for future in as_completed(futures):
            gene = futures[future]
            try:
                gene_name, drugs = future.result()
            except:
                continue

            for d in drugs:
                results.append({"variant": gene_name, "drug": d.upper()})

    if not results:
        print("⚠️ No PubMed results found.")
        df = pd.DataFrame(columns=["variant", "drug", "mention_count"])
        df.to_csv(output_path, sep="\t", index=False)
        return df

    df = pd.DataFrame(results)

    df_group = (
        df.groupby(["variant", "drug"])
          .size()
          .reset_index(name="mention_count")
          .sort_values(["variant", "mention_count"], ascending=[True, False])
    )

    df_group.to_csv(output_path, sep="\t", index=False)
    print(f"✅ PubMed saved to {output_path}")

    return df_group