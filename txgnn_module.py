import sys
import os
import torch
import numpy as np
import pandas as pd
from typing import List
from collections import defaultdict

# TxGNN path is added dynamically via add_txgnn_to_path()

# === TxGNN 패키지 경로를 동적으로 추가할 수 있게 변경 ===
def add_txgnn_to_path(txgnn_root: str):
    """
    txgnn 패키지가 있는 루트 경로를 sys.path에 추가
    예: /home/yebin/DrugAnno_Pipeline/TxGNN
    """
    if txgnn_root not in sys.path:
        sys.path.append(txgnn_root)

# TxData import는 함수 안에서 수행 (경로 세팅 이후)
from txgnn import TxData


class LightweightMutationTxGNN:
    """
    Drug Repurposing 중심 약물 추천 시스템
    - 다른 질병에 승인됐지만 현재 암종에는 미승인인 약물 강조
    - 변이 유전자 타겟팅 약물 우선
    """
    
    def __init__(self, data_folder: str = './data'):
        """
        Args:
            data_folder: 지식 그래프 데이터 폴더 경로
        """
        print("TxData 로딩 중 (모델 로딩 없음)...")
        
        # TxData만 로드 (모델은 로드하지 않음)
        self.TxData = TxData(data_folder_path=data_folder)
        self.TxData.prepare_split(split='full_graph', seed=42)
        self.G = self.TxData.G
        
        # 노드 매핑 구축
        self._build_mappings()
        
        # 그래프 연결 정보 캐싱 (메모리 효율적)
        self._build_connection_cache()
        
        # FDA 승인 약물 전체 목록 구축
        self._build_fda_approved_drugs()
        
        print("초기화 완료! (GPU 메모리 사용 없음)\n")
    
    def _build_mappings(self):
        """노드 매핑 구축"""
        print("노드 매핑 구축 중...")
        
        id_mapping = self.TxData.retrieve_id_mapping()
        
        self.disease_to_idx = {}
        self.gene_to_idx = {}
        self.drug_to_idx = {}
        self.idx_to_drug = {}
        self.idx_to_disease = {}
        self.idx_to_gene = {}
        
        # Disease 매핑
        if 'id2name_disease' in id_mapping and 'idx2id_disease' in id_mapping:
            id2name = id_mapping['id2name_disease']
            idx2id = id_mapping['idx2id_disease']
            for idx, node_id in idx2id.items():
                if node_id in id2name:
                    name = id2name[node_id]
                    self.disease_to_idx[name.lower()] = int(idx)
                    self.idx_to_disease[int(idx)] = name
        
        # Drug 매핑
        if 'id2name_drug' in id_mapping and 'idx2id_drug' in id_mapping:
            id2name = id_mapping['id2name_drug']
            idx2id = id_mapping['idx2id_drug']
            for idx, node_id in idx2id.items():
                if node_id in id2name:
                    name = id2name[node_id]
                    self.drug_to_idx[name.lower()] = int(idx)
                    self.idx_to_drug[int(idx)] = name
        
        # Gene/Protein 매핑
        self._build_gene_mapping()
        
        print(f"✓ 질병: {len(self.disease_to_idx)}개")
        print(f"✓ 약물: {len(self.drug_to_idx)}개")
        print(f"✓ 유전자: {len(self.gene_to_idx)}개\n")
    
    def _build_gene_mapping(self):
        """유전자 매핑 구축"""
        try:
            kg_path = os.path.join(self.TxData.data_folder, 'kg.csv')
            df_kg = pd.read_csv(kg_path)
            
            gene_types = ['gene', 'protein', 'gene/protein']
            gene_x = df_kg[df_kg.x_type.isin(gene_types)][['x_id', 'x_name']].drop_duplicates()
            gene_y = df_kg[df_kg.y_type.isin(gene_types)][['y_id', 'y_name']].drop_duplicates()
            gene_y.columns = ['x_id', 'x_name']
            all_genes = pd.concat([gene_x, gene_y]).drop_duplicates()
            
            all_genes['x_id'] = all_genes['x_id'].apply(lambda x: str(int(float(x))) if pd.notna(x) else None)
            id2name_gene = dict(all_genes.values)
            
            df = self.TxData.df
            gene_idx_x = df[df.x_type.isin(gene_types)][['x_idx', 'x_id']].drop_duplicates()
            gene_idx_y = df[df.y_type.isin(gene_types)][['y_idx', 'y_id']].drop_duplicates()
            gene_idx_y.columns = ['x_idx', 'x_id']
            gene_idx_mapping = pd.concat([gene_idx_x, gene_idx_y]).drop_duplicates()
            
            gene_idx_mapping['x_id'] = gene_idx_mapping['x_id'].apply(lambda x: str(int(float(x))) if pd.notna(x) else None)
            idx2id_gene = dict(gene_idx_mapping.values)
            
            for idx, gene_id in idx2id_gene.items():
                if gene_id in id2name_gene:
                    gene_name = id2name_gene[gene_id]
                    gene_name_upper = str(gene_name).strip().upper()
                    if gene_name_upper:
                        self.gene_to_idx[gene_name_upper] = int(idx)
                        self.idx_to_gene[int(idx)] = gene_name_upper
            
        except Exception as e:
            print(f"⚠️ 유전자 매핑 오류: {e}")
    
    def _build_connection_cache(self):
        """그래프 연결 정보 캐싱"""
        print("그래프 연결 정보 캐싱 중...")
        
        # Disease-Drug 연결 (relation 타입별)
        self.disease_to_drugs_indication = defaultdict(set)  # FDA 승인 (indication)
        self.disease_to_drugs_other = defaultdict(set)  # 기타 연결
        
        # Gene-Drug 연결
        self.gene_to_drugs_target = defaultdict(set)  # 약물이 유전자를 타겟팅
        self.gene_to_drugs_other = defaultdict(set)  # 기타 연결
        
        edge_types = self.G.canonical_etypes
        
        # Gene-Drug relation 확인 (디버깅용)
        print("\n그래프의 모든 edge relation 타입:")
        gene_drug_relations = []
        for etype in edge_types:
            src_type, rel_type, dst_type = etype
            if (src_type in ['gene', 'protein', 'gene/protein'] and dst_type == 'drug') or \
               (src_type == 'drug' and dst_type in ['gene', 'protein', 'gene/protein']):
                gene_drug_relations.append(rel_type)
        
        unique_relations = sorted(set(gene_drug_relations))
        print(f"Gene-Drug 관련 relation: {unique_relations[:10]}")
        print()
        
        for etype in edge_types:
            src_type, rel_type, dst_type = etype
            
            # Disease -> Drug (indication = FDA 승인)
            if src_type == 'disease' and dst_type == 'drug':
                src, dst = self.G.edges(etype=etype)
                for s, d in zip(src.tolist(), dst.tolist()):
                    if 'indication' in rel_type.lower() or 'treat' in rel_type.lower():
                        self.disease_to_drugs_indication[s].add(d)
                    else:
                        self.disease_to_drugs_other[s].add(d)
            
            # Drug -> Disease (역방향)
            elif src_type == 'drug' and dst_type == 'disease':
                src, dst = self.G.edges(etype=etype)
                for s, d in zip(src.tolist(), dst.tolist()):
                    if 'indication' in rel_type.lower() or 'treat' in rel_type.lower():
                        self.disease_to_drugs_indication[d].add(s)
                    else:
                        self.disease_to_drugs_other[d].add(s)
            
            # Gene/Protein -> Drug
            elif src_type in ['gene', 'protein', 'gene/protein'] and dst_type == 'drug':
                src, dst = self.G.edges(etype=etype)
                
                # TxGNN은 'drug_protein', 'rev_drug_protein'만 사용
                is_target = 'protein' in rel_type.lower() or 'drug' in rel_type.lower()
                
                for s, d in zip(src.tolist(), dst.tolist()):
                    if is_target:
                        self.gene_to_drugs_target[s].add(d)
                    else:
                        self.gene_to_drugs_other[s].add(d)
            
            # Drug -> Gene/Protein (역방향)
            elif src_type == 'drug' and dst_type in ['gene', 'protein', 'gene/protein']:
                src, dst = self.G.edges(etype=etype)
                
                is_target = 'protein' in rel_type.lower() or 'drug' in rel_type.lower()
                
                for s, d in zip(src.tolist(), dst.tolist()):
                    if is_target:
                        self.gene_to_drugs_target[d].add(s)
                    else:
                        self.gene_to_drugs_other[d].add(s)
        
        print(f"✓ Disease-Drug (FDA 승인): {len(self.disease_to_drugs_indication)}개 질병")
        print(f"✓ Disease-Drug (기타): {len(self.disease_to_drugs_other)}개 질병")
        print(f"✓ Gene-Drug (타겟): {len(self.gene_to_drugs_target)}개 유전자")
        print(f"✓ Gene-Drug (기타): {len(self.gene_to_drugs_other)}개 유전자\n")
    
    def _build_fda_approved_drugs(self):
        """모든 질병에 대해 FDA 승인된 약물 목록 구축"""
        print("FDA 승인 약물 전체 목록 구축 중...")
        
        # 어떤 질병이든 indication이 있으면 FDA 승인 약물로 간주
        self.all_fda_approved_drugs = set()
        
        for disease_idx, drug_set in self.disease_to_drugs_indication.items():
            self.all_fda_approved_drugs.update(drug_set)
        
        print(f"✓ 전체 FDA 승인 약물: {len(self.all_fda_approved_drugs)}개\n")
    
    def find_disease_idx(self, cancer_type: str) -> int:
        """암종 이름으로 질병 인덱스 찾기"""
        cancer_lower = cancer_type.lower()
        
        if cancer_lower in self.disease_to_idx:
            return self.disease_to_idx[cancer_lower]
        
        # 부분 매칭
        candidates = []
        for disease_name, idx in self.disease_to_idx.items():
            if cancer_lower in disease_name or disease_name in cancer_lower:
                candidates.append((disease_name, idx))
        
        if candidates:
            print(f"✓ 매칭된 질병: {candidates[0][0]}")
            return candidates[0][1]
        
        raise ValueError(f"암종 '{cancer_type}'을 찾을 수 없습니다.")
    
    def find_gene_indices(self, gene_names: List[str]) -> List[int]:
        """변이 유전자 이름들로 인덱스 찾기"""
        gene_indices = []
        found_genes = []
        not_found = []
        
        for gene in gene_names:
            gene_upper = gene.upper()
            if gene_upper in self.gene_to_idx:
                idx = self.gene_to_idx[gene_upper]
                gene_indices.append(idx)
                found_genes.append(gene_upper)
            else:
                not_found.append(gene)
        
        if found_genes:
            print(f"✓ 발견된 유전자: {', '.join(found_genes)} ({len(found_genes)}개)")
        
        if not_found:
            print(f"⚠️ 찾을 수 없는 유전자: {', '.join(not_found)}")
        
        return gene_indices
    
    def recommend_drugs(
        self,
        cancer_type: str,
        mutation_genes: List[str],
        top_k: int = 30,
        mode: str = 'repurposing'  # 'repurposing' or 'all'
    ) -> pd.DataFrame:
        """
        약물 추천 (Drug Repurposing 중심)
        """
        print(f"\n{'='*60}")
        print(f"약물 추천 분석 (모드: {mode.upper()})")
        print(f"{'='*60}")
        
        # 1. 질병 인덱스 찾기
        try:
            disease_idx = self.find_disease_idx(cancer_type)
            print(f"질병 인덱스: {disease_idx}")
        except ValueError as e:
            print(f"오류: {e}")
            return pd.DataFrame()
        
        # 2. 변이 유전자 인덱스 찾기
        gene_indices = self.find_gene_indices(mutation_genes)
        
        # 3. 그래프에서 연결된 약물 찾기
        print("\n그래프 연결 탐색 중...")
        
        # Disease와 연결된 약물 (현재 적응증)
        current_indication_drugs = self.disease_to_drugs_indication.get(disease_idx, set())
        print(f"✓ {cancer_type}의 현재 적응증 약물: {len(current_indication_drugs)}개")
        
        # Disease와 기타 연결
        disease_drugs_other = self.disease_to_drugs_other.get(disease_idx, set())
        print(f"✓ {cancer_type}와 기타 연결 약물: {len(disease_drugs_other)}개")
        
        # 변이 유전자와 연결된 약물
        mutation_drugs_target = set()
        gene_drug_map = {}
        
        for gene_idx in gene_indices:
            gene_name = self.idx_to_gene.get(gene_idx, f"Gene_{gene_idx}")
            
            # Target 약물
            target_drugs = self.gene_to_drugs_target.get(gene_idx, set())
            mutation_drugs_target.update(target_drugs)
            for drug_idx in target_drugs:
                if drug_idx not in gene_drug_map:
                    gene_drug_map[drug_idx] = []
                gene_drug_map[drug_idx].append(gene_name)
        
        print(f"✓ 변이 유전자 타겟 약물: {len(mutation_drugs_target)}개")
        
        # 4. 결과 조합
        results = []
        
        # 모든 관련 약물 수집
        all_relevant_drugs = current_indication_drugs | disease_drugs_other | mutation_drugs_target
        
        for drug_idx in all_relevant_drugs:
            if drug_idx not in self.idx_to_drug:
                continue
            
            drug_name = self.idx_to_drug[drug_idx]
            
            # 카테고리 분류
            is_current_indication = drug_idx in current_indication_drugs
            is_disease_related = drug_idx in disease_drugs_other
            is_mutation_target = drug_idx in mutation_drugs_target
            is_fda_approved_elsewhere = drug_idx in self.all_fda_approved_drugs
            
            # Repurposing 후보인지 판단
            is_repurposing = (not is_current_indication) and is_fda_approved_elsewhere and is_mutation_target
            
            # 스코어 계산 (Repurposing 모드)
            if mode == 'repurposing':
                score = 0.0
                
                # Repurposing 후보 (다른 질병 승인 + 변이 타겟)
                if is_repurposing:
                    score += 20.0  # 최고 점수!
                    num_genes = len(gene_drug_map.get(drug_idx, []))
                    score += (num_genes - 1) * 2.0  # 여러 유전자 타겟시 보너스
                
                # 변이 타겟이지만 어디서도 승인 안 됨 (신약)
                elif is_mutation_target and not is_fda_approved_elsewhere:
                    score += 10.0
                    num_genes = len(gene_drug_map.get(drug_idx, []))
                    score += (num_genes - 1) * 1.0
                
                # 현재 적응증 (이미 쓰이는 약)
                elif is_current_indication:
                    score += 5.0
                    if is_mutation_target:
                        score += 3.0  # 변이 타겟이면 추가
                
                # 기타
                elif is_disease_related:
                    score += 2.0
            
            else:  # 'all' 모드
                score = 0.0
                if is_current_indication:
                    score += 10.0
                if is_mutation_target:
                    score += 5.0
                    num_genes = len(gene_drug_map.get(drug_idx, []))
                    score += (num_genes - 1) * 1.0
                if is_disease_related:
                    score += 3.0
            
            # 카테고리 라벨
            """categories = []
            if is_repurposing:
                categories.append("🔄 Repurposing Priority")
            if is_current_indication:
                categories.append("✓ Current Indication")
            if is_mutation_target and not is_fda_approved_elsewhere:
                categories.append("🆕 Investigational Targeting")
            if is_fda_approved_elsewhere and not is_current_indication:
                categories.append("💊 Cross-Indication Approved")"""
            
            categories = []

            # 1순위: Repurposing Priority (가장 중요)
            if is_repurposing:
                categories.append("🔄 Repurposing Priority")

            # 2순위: Current Indication (이미 쓰이는 약)
            elif is_current_indication:
                categories.append("✓ Current Indication")
                if is_mutation_target:
                    categories.append("🎯 Mutation-Targeted")

            # 3순위: Investigational (신약, 아직 승인 안됨)
            elif is_mutation_target and not is_fda_approved_elsewhere:
                categories.append("🆕 Investigational Targeting")

            # 4순위: Cross-Indication (다른 질병 승인, 하지만 변이 타겟 아님)
            elif is_fda_approved_elsewhere and not is_current_indication and not is_mutation_target:
                categories.append("💊 Cross-Indication Approved")

            # 5순위: Disease-Related (질병 연관만)
            elif is_disease_related:
                categories.append("🔗 Disease-Related")

            # 기타
            else:
                categories.append("❓ Other")
            
            # 연결된 변이 유전자
            connected_genes = gene_drug_map.get(drug_idx, [])
            
            results.append({
                'drug_name': drug_name,
                'score': score,
                'category': ' | '.join(categories) if categories else '기타',
                'repurposing': '🔄' if is_repurposing else '',
                'current_use': '✓' if is_current_indication else '',
                'mutation_target': '✓' if is_mutation_target else '',
                'fda_approved': '✓' if is_fda_approved_elsewhere else '',
                'connected_genes': ', '.join(connected_genes) if connected_genes else '-',
                'num_genes': len(connected_genes)
            })
        
        # DataFrame 생성 및 정렬
        df_results = pd.DataFrame(results)
        
        if len(df_results) > 0:
            df_results = df_results.sort_values('score', ascending=False)
            
            # Repurposing 모드에서는 score > 0인 것만
            if mode == 'repurposing':
                df_results = df_results[df_results['score'] > 0]
            
            print(f"\n✓ 총 {len(df_results)}개 약물 발견")
            return df_results.head(top_k)
        else:
            print("\n⚠️ 추천할 약물을 찾을 수 없습니다.")
            return pd.DataFrame()


# ============================
# 🔑 MAF 기반 wrapper 함수
# ============================

def load_genes_from_maf(maf_path: str):
    """
    MAF에서 Hugo_Symbol 기반 유전자 리스트 추출
    """
    maf = pd.read_csv(maf_path, sep="\t", comment="#", low_memory=False)
    if "Hugo_Symbol" not in maf.columns:
        raise ValueError("❌ MAF 파일에 'Hugo_Symbol' 컬럼이 없습니다.")
    genes = sorted(maf["Hugo_Symbol"].dropna().unique().tolist())
    return genes


def run_txgnn(
    maf_path: str,
    cancer_type: str,
    output_path: str,
    data_folder: str = "./data",
    txgnn_root: str = "./TxGNN",
    top_k: int = 50,
    mode: str = "repurposing"
) -> pd.DataFrame:
    """
    MAF + 암종 정보 기반 TxGNN 약물 추천 실행 후 TSV로 저장
    
    출력 포맷:
        drug    txgnn_score    category    repurposing    current_use
        mutation_target    fda_approved    connected_genes    num_genes
    """
    # TxGNN 패키지 경로 세팅
    add_txgnn_to_path(txgnn_root)
    
    # 변이 유전자 추출
    print(f"🧬 MAF에서 변이 유전자(Hugo_Symbol) 추출: {maf_path}")
    mutation_genes = load_genes_from_maf(maf_path)
    print(f"✓ 변이 유전자 {len(mutation_genes)}개 발견\n")
    
    # 모델 초기화
    model = LightweightMutationTxGNN(data_folder=data_folder)
    
    # 약물 추천
    df = model.recommend_drugs(
        cancer_type=cancer_type,
        mutation_genes=mutation_genes,
        top_k=top_k,
        mode=mode
    )
    
    # 빈 결과 처리
    if df is None or df.empty:
        print("⚠️ TxGNN에서 추천 약물을 찾지 못했습니다. 빈 TSV를 저장합니다.")
        empty_cols = [
            "drug", "txgnn_score", "category", "repurposing",
            "current_use", "mutation_target", "fda_approved",
            "connected_genes", "num_genes"
        ]
        out_df = pd.DataFrame(columns=empty_cols)
        out_df.to_csv(output_path, sep="\t", index=False)
        return out_df
    
    # 병합에 쓰기 좋은 형태로 컬럼 정리
    out_df = df.copy()
    out_df["drug"] = out_df["drug_name"].str.upper()
    out_df["txgnn_score"] = out_df["score"]
    
    # 최종 컬럼 순서
    out_df = out_df[[
        "drug", "txgnn_score", "category", "repurposing",
        "current_use", "mutation_target", "fda_approved",
        "connected_genes", "num_genes"
    ]]
    
    out_df.to_csv(output_path, sep="\t", index=False)
    print(f"✅ TxGNN 결과 저장 완료: {output_path}")
    
    return out_df


# 단독 실행 테스트용
if __name__ == "__main__":
    df = run_txgnn(
        maf_path="test.maf",
        cancer_type="lung cancer",
        output_path="txgnn_output.tsv",
        data_folder="./data",
        txgnn_root="./TxGNN",
        top_k=50,
        mode="repurposing"
    )
    print(df.head())