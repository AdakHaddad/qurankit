"""
Advanced research features for QuranKit.

Implements:
- Semantic relation lookup (synonyms, antonyms, related concepts from dictionary sources)
- Co-occurrence and collocation analysis (word pairs, PMI, t-test)
- Cross-reference analysis (ayah-to-ayah links with provenance)
- Wujuh wa nazair support (verses with similar wording but different meaning)
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import StrEnum
from math import log
from typing import Any

from qurankit.lexicon import get_lexicon_registry
from qurankit.lexicon.adapter import DictionaryAdapterRegistry
from qurankit.lexicon.vocabulary import QuranicVocabulary
from qurankit.models.enums import ClaimCategory
from qurankit.search.normalization import normalize
from qurankit.storage.access import DataAccess


class SemanticRelationType(StrEnum):
    """Types of semantic relations from dictionary sources."""

    SYNONYM = "synonym"
    ANTONYM = "antonym"
    HYPERNYM = "hypernym"
    HYPONYM = "hyponym"
    MERONYM = "meronym"
    HOLONYM = "holonym"
    RELATED = "related"
    SEE_ALSO = "see_also"
    CONTRAST = "contrast"
    CAUSE_EFFECT = "cause_effect"


class CooccurrenceMeasure(StrEnum):
    """Statistical measures for collocation analysis."""

    PMI = "pmi"
    T_TEST = "t_test"
    DICE = "dice"
    LOG_LIKELIHOOD = "log_likelihood"
    FREQUENCY = "frequency"


@dataclass(frozen=True)
class SemanticRelationResult:
    """A single semantic relation between lexical entries."""

    subject_entry_id: str
    subject_headword: str
    subject_root: str | None
    relation_type: SemanticRelationType
    object_entry_id: str
    object_headword: str
    object_root: str | None
    evidence: str | None = None
    confidence: float | None = None
    source_resource: str | None = None
    claim_category: ClaimCategory = ClaimCategory.SOURCE_ANNOTATION


@dataclass(frozen=True)
class CollocationResult:
    """A statistically significant word collocation."""

    word1: str
    word2: str
    word1_root: str | None
    word2_root: str | None
    cooccurrence_count: int
    word1_count: int
    word2_count: int
    total_windows: int
    measure: CooccurrenceMeasure
    score: float
    p_value: float | None = None
    window_size: int = 5
    claim_category: ClaimCategory = ClaimCategory.DETERMINISTIC_RESULT


@dataclass(frozen=True)
class CrossReference:
    """A sourced cross-reference between two ayahs."""

    source_reference: str
    target_reference: str
    relation_type: str
    evidence: str | None = None
    source_dataset: str | None = None
    confidence: float | None = None
    claim_category: ClaimCategory = ClaimCategory.SOURCE_ANNOTATION


@dataclass(frozen=True)
class WujuhWaNazairPair:
    """A pair of verses with similar wording but different meaning."""

    ayah1_reference: str
    ayah1_text: str
    ayah2_reference: str
    ayah2_text: str
    similarity_score: float
    difference_notes: str | None = None
    shared_words: list[str] = field(default_factory=list)
    claim_category: ClaimCategory = ClaimCategory.RESEARCH_HYPOTHESIS


class SemanticRelationExtractor:
    """Extracts semantic relations from dictionary sources."""

    def __init__(self, registry: DictionaryAdapterRegistry | None = None):
        self.registry = registry or get_lexicon_registry()

    def _process_lookup_results(
        self,
        results: dict[str, Any],
        relation_types: list[SemanticRelationType] | None,
    ) -> list[SemanticRelationResult]:
        """Process lookup results to extract semantic relations."""
        relations = []

        for resource_id, lookup_result in results.items():
            adapter = self.registry.get_adapter(resource_id)
            if not adapter or not adapter.capabilities.supports_semantic_relations:
                continue

            for entry in lookup_result.entries:
                try:
                    entry_relations = adapter.get_semantic_relations(entry.lexical_entry_id)
                    for rel in entry_relations:
                        rel_type_str = rel.get("relation_type", "related")
                        try:
                            rel_type = SemanticRelationType(rel_type_str)
                        except ValueError:
                            rel_type = SemanticRelationType.RELATED

                        if relation_types and rel_type not in relation_types:
                            continue

                        relations.append(SemanticRelationResult(
                            subject_entry_id=entry.lexical_entry_id,
                            subject_headword=entry.headword_original,
                            subject_root=entry.root_form,
                            relation_type=rel_type,
                            object_entry_id=rel.get("target_id", ""),
                            object_headword=rel.get("target_headword", ""),
                            object_root=rel.get("target_root"),
                            evidence=rel.get("evidence"),
                            confidence=rel.get("confidence"),
                            source_resource=resource_id,
                            claim_category=ClaimCategory.SOURCE_ANNOTATION,
                        ))
                except Exception:
                    pass

        return relations

    def find_relations_for_root(
        self,
        root_form: str,
        relation_types: list[SemanticRelationType] | None = None,
        resource_ids: list[str] | None = None,
    ) -> list[SemanticRelationResult]:
        """Find semantic relations for all entries sharing a root."""
        results = self.registry.lookup_root_across_resources(
            root_form, limit=100, resource_ids=resource_ids
        )
        return self._process_lookup_results(results, relation_types)

    def find_relations_for_lemma(
        self,
        lemma_form: str,
        relation_types: list[SemanticRelationType] | None = None,
        resource_ids: list[str] | None = None,
    ) -> list[SemanticRelationResult]:
        """Find semantic relations for entries matching a lemma."""
        results = self.registry.lookup_lemma_across_resources(
            lemma_form, limit=100, resource_ids=resource_ids
        )
        return self._process_lookup_results(results, relation_types)

    def find_synonyms(
        self,
        root_form: str | None = None,
        lemma_form: str | None = None,
        resource_ids: list[str] | None = None,
    ) -> list[SemanticRelationResult]:
        """Find synonyms for a root or lemma."""
        types = [SemanticRelationType.SYNONYM]
        if root_form:
            return self.find_relations_for_root(root_form, types, resource_ids)
        if lemma_form:
            return self.find_relations_for_lemma(lemma_form, types, resource_ids)
        return []

    def find_antonyms(
        self,
        root_form: str | None = None,
        lemma_form: str | None = None,
        resource_ids: list[str] | None = None,
    ) -> list[SemanticRelationResult]:
        """Find antonyms for a root or lemma."""
        types = [SemanticRelationType.ANTONYM]
        if root_form:
            return self.find_relations_for_root(root_form, types, resource_ids)
        if lemma_form:
            return self.find_relations_for_lemma(lemma_form, types, resource_ids)
        return []


class CollocationAnalyzer:
    """Computes word co-occurrence and collocation statistics."""

    def __init__(
        self,
        vocabulary: QuranicVocabulary | None = None,
        data_access: DataAccess | None = None,
        edition_id: str = "tanzil-uthmani-v1",
    ):
        self.vocabulary = vocabulary
        self.data_access = data_access or DataAccess()
        self.edition_id = edition_id

    def _get_all_ayah_tokens(self) -> list[dict[str, Any]]:
        """Get all tokens with surah, ayah, position, and root/lemma."""
        rows = self.data_access.db.fetchall(
            """
            SELECT
                wt.token_id,
                wt.surah_number,
                wt.ayah_number,
                wt.token_index,
                wt.surface_original,
                ta.root_id,
                ta.lemma_id
            FROM word_token wt
            LEFT JOIN token_analysis ta ON ta.token_id = wt.token_id
                AND ta.dataset_id = 'qac-morphology'
            WHERE wt.edition_id = ?
            ORDER BY wt.surah_number, wt.ayah_number, wt.token_index
            """,
            (self.edition_id,),
        )
        return [dict(r) for r in rows]

    def compute_collocations(
        self,
        window_size: int = 5,
        min_cooccurrence: int = 3,
        measure: CooccurrenceMeasure = CooccurrenceMeasure.PMI,
        top_n: int = 100,
        filter_stopwords: bool = True,
    ) -> list[CollocationResult]:
        """Compute statistically significant collocations."""
        tokens = self._get_all_ayah_tokens()
        if not tokens:
            return []

        token_data = []
        for t in tokens:
            root = t["root_id"]
            root_form = root.replace("qac-root:", "").replace("_", " ") if root else None
            token_data.append({
                "surah": t["surah_number"],
                "ayah": t["ayah_number"],
                "index": t["token_index"],
                "surface": t["surface_original"],
                "root": root_form,
            })

        word_counts = Counter()
        for td in token_data:
            word_counts[td["surface"]] += 1

        cooccur_counts = Counter()
        total_windows = 0

        ayah_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
        for td in token_data:
            ayah_groups[(td["surah"], td["ayah"])].append(td)

        for ayah_tokens in ayah_groups.values():
            n = len(ayah_tokens)
            for i in range(n):
                w1 = ayah_tokens[i]
                start = max(0, i - window_size)
                end = min(n, i + window_size + 1)
                for j in range(start, end):
                    if i == j:
                        continue
                    w2 = ayah_tokens[j]
                    pair = tuple(sorted([w1["surface"], w2["surface"]]))
                    cooccur_counts[pair] += 1
                total_windows += 1

        stopwords = {
            "و", "ف", "ب", "ل", "ك", "في", "من", "على", "إلى", "عن", "مع", "هذا", "ذلك",
            "الذي", "التي", "الذين", "اللذين", "ما", "إن", "أن", "لكن", "إذا",
            "إذ", "قد", "لا", "لم", "لن", "ليس", "كان", "يكون", "كانوا", "يكونوا"
        } if filter_stopwords else set()

        results = []
        total_tokens = len(token_data)

        for (w1, w2), cooc_count in cooccur_counts.items():
            if cooc_count < min_cooccurrence:
                continue
            if w1 in stopwords or w2 in stopwords:
                continue

            count1 = word_counts.get(w1, 0)
            count2 = word_counts.get(w2, 0)
            if count1 == 0 or count2 == 0:
                continue

            root1 = None
            root2 = None
            for td in token_data:
                if td["surface"] == w1 and td["root"]:
                    root1 = td["root"]
                    break
            for td in token_data:
                if td["surface"] == w2 and td["root"]:
                    root2 = td["root"]
                    break

            score = 0.0

            if measure == CooccurrenceMeasure.PMI:
                p_w1w2 = cooc_count / total_windows
                p_w1 = count1 / total_tokens
                p_w2 = count2 / total_tokens
                if p_w1 > 0 and p_w2 > 0:
                    score = log(p_w1w2 / (p_w1 * p_w2), 2)

            elif measure == CooccurrenceMeasure.DICE:
                score = (2 * cooc_count) / (count1 + count2)

            elif measure == CooccurrenceMeasure.FREQUENCY:
                score = float(cooc_count)

            elif measure == CooccurrenceMeasure.LOG_LIKELIHOOD:
                expected = (count1 * count2) / total_tokens
                if expected > 0:
                    score = 2 * (cooc_count * log(cooc_count / expected))

            results.append(CollocationResult(
                word1=w1,
                word2=w2,
                word1_root=root1,
                word2_root=root2,
                cooccurrence_count=cooc_count,
                word1_count=count1,
                word2_count=count2,
                total_windows=total_windows,
                measure=measure,
                score=score,
                window_size=window_size,
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_n]

    def get_collocations_for_word(
        self,
        word: str,
        window_size: int = 5,
        measure: CooccurrenceMeasure = CooccurrenceMeasure.PMI,
        top_n: int = 20,
    ) -> list[CollocationResult]:
        """Get collocations for a specific word."""
        all_collocations = self.compute_collocations(
            window_size=window_size,
            measure=measure,
            top_n=1000,
        )
        filtered = [c for c in all_collocations if word in {c.word1, c.word2}]
        return filtered[:top_n]


class CrossReferenceAnalyzer:
    """Analyzes cross-references between ayahs."""

    def __init__(self, data_access: DataAccess | None = None, edition_id: str = "tanzil-uthmani-v1"):
        self.data_access = data_access or DataAccess()
        self.edition_id = edition_id

    def get_explicit_cross_references(
        self,
        reference: str,
        dataset_id: str | None = None,
    ) -> list[CrossReference]:
        """Get explicitly annotated cross-references for an ayah."""
        surah_num, ayah_num = map(int, reference.split(":"))

        query = """
            SELECT
                target_surah,
                target_ayah,
                relation_type,
                evidence_note,
                dataset_id,
                confidence
            FROM ayah_cross_reference
            WHERE source_surah = ? AND source_ayah = ?
        """
        params = [surah_num, ayah_num]

        if dataset_id:
            query += " AND dataset_id = ?"
            params.append(dataset_id)

        rows = self.data_access.db.fetchall(query, params)

        results = []
        for row in rows:
            results.append(CrossReference(
                source_reference=reference,
                target_reference=f"{row['target_surah']}:{row['target_ayah']}",
                relation_type=row["relation_type"],
                evidence=row["evidence_note"],
                source_dataset=row["dataset_id"],
                confidence=row["confidence"],
                claim_category=ClaimCategory.SOURCE_ANNOTATION,
            ))

        return results

    def find_implicit_links(
        self,
        reference: str,
        min_shared_roots: int = 2,
        min_shared_lemmas: int = 1,
        limit: int = 20,
    ) -> list[CrossReference]:
        """Find ayahs implicitly linked by shared vocabulary."""
        surah_num, ayah_num = map(int, reference.split(":"))

        source_tokens = self.data_access.db.fetchall(
            """
            SELECT ta.root_id, ta.lemma_id
            FROM word_token wt
            JOIN token_analysis ta ON ta.token_id = wt.token_id
            WHERE wt.edition_id = ? AND wt.surah_number = ? AND wt.ayah_number = ?
              AND ta.dataset_id = 'qac-morphology'
            """,
            (self.edition_id, surah_num, ayah_num),
        )

        source_roots = {r["root_id"] for r in source_tokens if r["root_id"]}
        source_lemmas = {r["lemma_id"] for r in source_tokens if r["lemma_id"]}

        if not source_roots and not source_lemmas:
            return []

        root_placeholders = ",".join("?" * len(source_roots))
        lemma_placeholders = ",".join("?" * len(source_lemmas))

        query = f"""
            SELECT
                wt.surah_number,
                wt.ayah_number,
                COUNT(DISTINCT ta.root_id) as shared_roots,
                COUNT(DISTINCT ta.lemma_id) as shared_lemmas,
                GROUP_CONCAT(DISTINCT ta.root_id) as roots_list,
                GROUP_CONCAT(DISTINCT ta.lemma_id) as lemmas_list
            FROM word_token wt
            JOIN token_analysis ta ON ta.token_id = wt.token_id
            WHERE wt.edition_id = ?
              AND ta.dataset_id = 'qac-morphology'
              AND (ta.root_id IN ({root_placeholders}) OR ta.lemma_id IN ({lemma_placeholders}))
              AND NOT (wt.surah_number = ? AND wt.ayah_number = ?)
            GROUP BY wt.surah_number, wt.ayah_number
            HAVING shared_roots >= ? OR shared_lemmas >= ?
            ORDER BY shared_roots DESC, shared_lemmas DESC
            LIMIT ?
        """

        params = (
            [self.edition_id]
            + list(source_roots)
            + list(source_lemmas)
            + [surah_num, ayah_num, min_shared_roots, min_shared_lemmas, limit]
        )

        rows = self.data_access.db.fetchall(query, params)

        results = []
        for row in rows:
            roots_list = row["roots_list"].split(",") if row["roots_list"] else []
            lemmas_list = row["lemmas_list"].split(",") if row["lemmas_list"] else []

            root_forms = [r.replace("qac-root:", "").replace("_", " ") for r in roots_list]
            lemma_forms = [lm.replace("qac-lemma:", "") for lm in lemmas_list]

            results.append(CrossReference(
                source_reference=reference,
                target_reference=f"{row['surah_number']}:{row['ayah_number']}",
                relation_type="lexical_overlap",
                evidence=f"Shared roots: {', '.join(root_forms)}; Shared lemmas: {', '.join(lemma_forms)}",
                source_dataset="computed",
                confidence=min(1.0, (row["shared_roots"] + row["shared_lemmas"]) / 10.0),
                claim_category=ClaimCategory.COMPUTATIONAL_SUGGESTION,
            ))

        return results


class WujuhWaNazairAnalyzer:
    """Detects wujuh wa nazair pairs."""

    def __init__(self, data_access: DataAccess | None = None, edition_id: str = "tanzil-uthmani-v1"):
        self.data_access = data_access or DataAccess()
        self.edition_id = edition_id

    def find_candidates(
        self,
        min_shared_words: int = 3,
        max_candidates: int = 100,
        similarity_threshold: float = 0.4,
    ) -> list[WujuhWaNazairPair]:
        """Find candidate wujuh wa nazair pairs."""
        ayahs = self.data_access.db.fetchall(
            """
            SELECT surah_number, ayah_number, text_original
            FROM ayah_text
            WHERE edition_id = ?
            ORDER BY surah_number, ayah_number
            """,
            (self.edition_id,),
        )

        if not ayahs:
            return []

        normalized_texts = {}
        token_sets = {}

        for row in ayahs:
            ref = f"{row['surah_number']}:{row['ayah_number']}"
            norm = normalize(row["text_original"], "diacritics-insensitive-v1")
            normalized_texts[ref] = norm.normalized
            token_sets[ref] = set(norm.normalized.split())

        candidates = []
        refs = list(normalized_texts.keys())

        for i in range(len(refs)):
            for j in range(i + 1, len(refs)):
                ref1, ref2 = refs[i], refs[j]

                tokens1 = token_sets[ref1]
                tokens2 = token_sets[ref2]

                shared = tokens1 & tokens2
                if len(shared) < min_shared_words:
                    continue

                union = tokens1 | tokens2
                jaccard = len(shared) / len(union) if union else 0.0

                if jaccard < similarity_threshold:
                    continue

                text1 = next(r["text_original"] for r in ayahs if f"{r['surah_number']}:{r['ayah_number']}" == ref1)
                text2 = next(r["text_original"] for r in ayahs if f"{r['surah_number']}:{r['ayah_number']}" == ref2)

                candidates.append(WujuhWaNazairPair(
                    ayah1_reference=ref1,
                    ayah1_text=text1,
                    ayah2_reference=ref2,
                    ayah2_text=text2,
                    similarity_score=jaccard,
                    shared_words=list(shared),
                    difference_notes=f"Jaccard similarity: {jaccard:.3f}; {len(shared)} shared words",
                    claim_category=ClaimCategory.RESEARCH_HYPOTHESIS,
                ))

        candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        return candidates[:max_candidates]

    def find_for_reference(
        self,
        reference: str,
        min_shared_words: int = 2,
        max_candidates: int = 20,
    ) -> list[WujuhWaNazairPair]:
        """Find wujuh wa nazair candidates for a specific ayah."""
        surah_num, ayah_num = map(int, reference.split(":"))

        query_row = self.data_access.db.fetchone(
            """
            SELECT text_original FROM ayah_text
            WHERE edition_id = ? AND surah_number = ? AND ayah_number = ?
            """,
            (self.edition_id, surah_num, ayah_num),
        )

        if not query_row:
            return []

        query_text = query_row["text_original"]
        query_norm = normalize(query_text, "diacritics-insensitive-v1")
        query_tokens = set(query_norm.normalized.split())

        ayahs = self.data_access.db.fetchall(
            """
            SELECT surah_number, ayah_number, text_original
            FROM ayah_text
            WHERE edition_id = ?
              AND NOT (surah_number = ? AND ayah_number = ?)
            ORDER BY surah_number, ayah_number
            """,
            (self.edition_id, surah_num, ayah_num),
        )

        candidates = []
        for row in ayahs:
            ref = f"{row['surah_number']}:{row['ayah_number']}"
            norm = normalize(row["text_original"], "diacritics-insensitive-v1")
            tokens = set(norm.normalized.split())

            shared = query_tokens & tokens
            if len(shared) < min_shared_words:
                continue

            union = query_tokens | tokens
            jaccard = len(shared) / len(union) if union else 0.0

            candidates.append(WujuhWaNazairPair(
                ayah1_reference=reference,
                ayah1_text=query_text,
                ayah2_reference=ref,
                ayah2_text=row["text_original"],
                similarity_score=jaccard,
                shared_words=list(shared),
                difference_notes=f"Jaccard similarity: {jaccard:.3f}; {len(shared)} shared words",
                claim_category=ClaimCategory.RESEARCH_HYPOTHESIS,
            ))

        candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        return candidates[:max_candidates]


def create_research_tools(
    data_access: DataAccess | None = None,
    edition_id: str = "tanzil-uthmani-v1",
) -> dict[str, Any]:
    """Factory to create all research analysis tools."""
    vocab = QuranicVocabulary(data_access=data_access, edition_id=edition_id)
    return {
        "semantic_relations": SemanticRelationExtractor(),
        "collocations": CollocationAnalyzer(vocabulary=vocab, data_access=data_access, edition_id=edition_id),
        "cross_references": CrossReferenceAnalyzer(data_access=data_access, edition_id=edition_id),
        "wujuh_wa_nazair": WujuhWaNazairAnalyzer(data_access=data_access, edition_id=edition_id),
    }
