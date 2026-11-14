"""
Qur'anic vocabulary integration for QuranKit.

Connects dictionary/lexicon entries to Qur'anic occurrences using
word tokens, morphological analysis (roots/lemmas), and structural
metadata. Provides concordance, frequency, and distribution analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qurankit.storage.access import DataAccess


@dataclass(frozen=True)
class QuranicOccurrence:
    """A single Qur'anic occurrence of a root, lemma, or word form."""

    surah_number: int
    ayah_number: int
    token_index: int
    surface_form: str
    root_form: str | None = None
    lemma_form: str | None = None
    part_of_speech: str | None = None
    edition_id: str = "tanzil-uthmani-v1"
    token_id: str | None = None
    ayah_text: str | None = None


@dataclass(frozen=True)
class VocabularyStats:
    """Statistics for a root, lemma, or word in the Qur'an."""

    root_form: str | None = None
    lemma_form: str | None = None
    surface_form: str | None = None
    total_occurrences: int = 0
    unique_surahs: int = 0
    unique_ayahs: int = 0
    first_occurrence: QuranicOccurrence | None = None
    last_occurrence: QuranicOccurrence | None = None
    surah_distribution: dict[int, int] | None = None  # surah -> count
    juz_distribution: dict[int, int] | None = None   # juz -> count


class QuranicVocabulary:
    """
    Qur'anic vocabulary analyzer.

    Connects dictionary/lexicon entries to actual Qur'anic occurrences
    using the word token and morphological analysis data in the database.
    Provides concordance, frequency, and distribution analysis.
    """

    def __init__(self, data_access: DataAccess | None = None, edition_id: str = "tanzil-uthmani-v1"):
        """
        Initialize vocabulary analyzer.

        Args:
            data_access: DataAccess instance (creates default if None)
            edition_id: Text edition to analyze
        """
        self.data_access = data_access or DataAccess()
        self.edition_id = edition_id

    def get_occurrences_by_root(
        self,
        root_form: str,
        limit: int = 1000,
    ) -> list[QuranicOccurrence]:
        """
        Get all Qur'anic occurrences of a root.

        Uses QAC morphology annotations (token_analysis) linked to word tokens.

        Args:
            root_form: Arabic root (e.g., "ر ح م" or "رحم")
            limit: Maximum occurrences to return

        Returns:
            List of QuranicOccurrence objects
        """
        # Normalize root for matching
        root_norm = root_form.replace(" ", "")

        # Query token_analysis joined with word_token to get occurrences
        rows = self.data_access.db.fetchall("""
            SELECT
                ta.root_id,
                ta.lemma_id,
                ta.part_of_speech,
                wt.token_id,
                wt.surah_number,
                wt.ayah_number,
                wt.token_index,
                wt.surface_original,
                at.text_original as ayah_text
            FROM token_analysis ta
            JOIN word_token wt ON wt.token_id = ta.token_id
            JOIN ayah_text at ON at.edition_id = wt.edition_id
                AND at.surah_number = wt.surah_number
                AND at.ayah_number = wt.ayah_number
            WHERE ta.dataset_id = 'qac-morphology'
              AND wt.edition_id = ?
              AND (ta.root_id LIKE ? OR ta.root_id LIKE ?)
            ORDER BY wt.surah_number, wt.ayah_number, wt.token_index
            LIMIT ?
        """, (self.edition_id, f"%{root_norm}%", f"%{root_form.replace(' ', '_')}%", limit))

        occurrences = []
        for row in rows:
            # Extract root form from root_id
            root_id = row["root_id"]
            extracted_root = root_id.replace("qac-root:", "").replace("_", " ") if root_id else None

            # Extract lemma form from lemma_id
            lemma_id = row["lemma_id"]
            extracted_lemma = lemma_id.replace("qac-lemma:", "") if lemma_id else None

            occurrences.append(QuranicOccurrence(
                surah_number=row["surah_number"],
                ayah_number=row["ayah_number"],
                token_index=row["token_index"],
                surface_form=row["surface_original"],
                root_form=extracted_root,
                lemma_form=extracted_lemma,
                part_of_speech=row["part_of_speech"],
                edition_id=self.edition_id,
                token_id=row["token_id"],
                ayah_text=row["ayah_text"],
            ))

        return occurrences

    def get_occurrences_by_lemma(
        self,
        lemma_form: str,
        limit: int = 1000,
    ) -> list[QuranicOccurrence]:
        """
        Get all Qur'anic occurrences of a lemma.

        Args:
            lemma_form: Arabic lemma (e.g., "رحمة", "رحمن")
            limit: Maximum occurrences to return

        Returns:
            List of QuranicOccurrence objects
        """
        rows = self.data_access.db.fetchall("""
            SELECT
                ta.root_id,
                ta.lemma_id,
                ta.part_of_speech,
                wt.token_id,
                wt.surah_number,
                wt.ayah_number,
                wt.token_index,
                wt.surface_original,
                at.text_original as ayah_text
            FROM token_analysis ta
            JOIN word_token wt ON wt.token_id = ta.token_id
            JOIN ayah_text at ON at.edition_id = wt.edition_id
                AND at.surah_number = wt.surah_number
                AND at.ayah_number = wt.ayah_number
            WHERE ta.dataset_id = 'qac-morphology'
              AND wt.edition_id = ?
              AND ta.lemma_id LIKE ?
            ORDER BY wt.surah_number, wt.ayah_number, wt.token_index
            LIMIT ?
        """, (self.edition_id, f"%{lemma_form}%", limit))

        occurrences = []
        for row in rows:
            root_id = row["root_id"]
            extracted_root = root_id.replace("qac-root:", "").replace("_", " ") if root_id else None

            lemma_id = row["lemma_id"]
            extracted_lemma = lemma_id.replace("qac-lemma:", "") if lemma_id else None

            occurrences.append(QuranicOccurrence(
                surah_number=row["surah_number"],
                ayah_number=row["ayah_number"],
                token_index=row["token_index"],
                surface_form=row["surface_original"],
                root_form=extracted_root,
                lemma_form=extracted_lemma,
                part_of_speech=row["part_of_speech"],
                edition_id=self.edition_id,
                token_id=row["token_id"],
                ayah_text=row["ayah_text"],
            ))

        return occurrences

    def get_occurrences_by_surface(
        self,
        surface_form: str,
        limit: int = 1000,
    ) -> list[QuranicOccurrence]:
        """
        Get all Qur'anic occurrences of a surface form (exact word).

        Args:
            surface_form: Exact Arabic word form
            limit: Maximum occurrences to return

        Returns:
            List of QuranicOccurrence objects
        """
        rows = self.data_access.db.fetchall("""
            SELECT
                wt.token_id,
                wt.surah_number,
                wt.ayah_number,
                wt.token_index,
                wt.surface_original,
                at.text_original as ayah_text,
                ta.root_id,
                ta.lemma_id,
                ta.part_of_speech
            FROM word_token wt
            JOIN ayah_text at ON at.edition_id = wt.edition_id
                AND at.surah_number = wt.surah_number
                AND at.ayah_number = wt.ayah_number
            LEFT JOIN token_analysis ta ON ta.token_id = wt.token_id
                AND ta.dataset_id = 'qac-morphology'
            WHERE wt.edition_id = ?
              AND wt.surface_original = ?
            ORDER BY wt.surah_number, wt.ayah_number, wt.token_index
            LIMIT ?
        """, (self.edition_id, surface_form, limit))

        occurrences = []
        for row in rows:
            root_id = row["root_id"]
            extracted_root = root_id.replace("qac-root:", "").replace("_", " ") if root_id else None

            lemma_id = row["lemma_id"]
            extracted_lemma = lemma_id.replace("qac-lemma:", "") if lemma_id else None

            occurrences.append(QuranicOccurrence(
                surah_number=row["surah_number"],
                ayah_number=row["ayah_number"],
                token_index=row["token_index"],
                surface_form=row["surface_original"],
                root_form=extracted_root,
                lemma_form=extracted_lemma,
                part_of_speech=row["part_of_speech"],
                edition_id=self.edition_id,
                token_id=row["token_id"],
                ayah_text=row["ayah_text"],
            ))

        return occurrences

    def get_vocabulary_stats(
        self,
        root_form: str | None = None,
        lemma_form: str | None = None,
        surface_form: str | None = None,
    ) -> VocabularyStats:
        """
        Get comprehensive statistics for a root, lemma, or surface form.

        Args:
            root_form: Arabic root
            lemma_form: Arabic lemma
            surface_form: Exact surface form

        Returns:
            VocabularyStats with frequency, distribution, etc.
        """
        occurrences = []

        if root_form:
            occurrences = self.get_occurrences_by_root(root_form)
            key_form = root_form
        elif lemma_form:
            occurrences = self.get_occurrences_by_lemma(lemma_form)
            key_form = lemma_form
        elif surface_form:
            occurrences = self.get_occurrences_by_surface(surface_form)
            key_form = surface_form
        else:
            return VocabularyStats()

        if not occurrences:
            return VocabularyStats(
                root_form=root_form,
                lemma_form=lemma_form,
                surface_form=surface_form,
            )

        # Calculate statistics
        total = len(occurrences)
        surahs = set(o.surah_number for o in occurrences)
        ayahs = set((o.surah_number, o.ayah_number) for o in occurrences)

        # Surah distribution
        surah_dist: dict[int, int] = {}
        for occ in occurrences:
            surah_dist[occ.surah_number] = surah_dist.get(occ.surah_number, 0) + 1

        # Juz distribution (requires metadata)
        juz_dist: dict[int, int] = {}
        for occ in occurrences:
            # Get juz from ayah_metadata
            juz_rows = self.data_access.db.fetchall("""
                SELECT value_text FROM ayah_metadata
                WHERE surah_number = ? AND ayah_number = ? AND metadata_type = 'juz'
                LIMIT 1
            """, (occ.surah_number, occ.ayah_number))
            if juz_rows:
                try:
                    juz = int(juz_rows[0]["value_text"])
                    juz_dist[juz] = juz_dist.get(juz, 0) + 1
                except (ValueError, TypeError):
                    pass

        first = occurrences[0]
        last = occurrences[-1]

        stats = VocabularyStats(
            root_form=root_form,
            lemma_form=lemma_form,
            surface_form=surface_form,
            total_occurrences=total,
            unique_surahs=len(surahs),
            unique_ayahs=len(ayahs),
            first_occurrence=first,
            last_occurrence=last,
            surah_distribution=surah_dist,
            juz_distribution=juz_dist if juz_dist else None,
        )

        return stats

    def get_concordance(
        self,
        root_form: str | None = None,
        lemma_form: str | None = None,
        surface_form: str | None = None,
        context_words: int = 3,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get concordance lines for a root, lemma, or surface form.

        Returns each occurrence with surrounding context words.

        Args:
            root_form: Arabic root
            lemma_form: Arabic lemma
            surface_form: Exact surface form
            context_words: Number of words before/after to include
            limit: Maximum concordance lines

        Returns:
            List of concordance line dictionaries
        """
        occurrences = []

        if root_form:
            occurrences = self.get_occurrences_by_root(root_form, limit)
        elif lemma_form:
            occurrences = self.get_occurrences_by_lemma(lemma_form, limit)
        elif surface_form:
            occurrences = self.get_occurrences_by_surface(surface_form, limit)
        else:
            return []

        concordance = []

        for occ in occurrences[:limit]:
            # Get surrounding tokens
            context_rows = self.data_access.db.fetchall("""
                SELECT token_index, surface_original
                FROM word_token
                WHERE edition_id = ? AND surah_number = ? AND ayah_number = ?
                  AND token_index BETWEEN ? AND ?
                ORDER BY token_index
            """, (
                self.edition_id,
                occ.surah_number,
                occ.ayah_number,
                max(0, occ.token_index - context_words),
                occ.token_index + context_words,
            ))

            context = [
                {"index": r["token_index"], "form": r["surface_original"]}
                for r in context_rows
            ]

            concordance.append({
                "reference": f"{occ.surah_number}:{occ.ayah_number}",
                "surah_number": occ.surah_number,
                "ayah_number": occ.ayah_number,
                "token_index": occ.token_index,
                "target_form": occ.surface_form,
                "root_form": occ.root_form,
                "lemma_form": occ.lemma_form,
                "part_of_speech": occ.part_of_speech,
                "ayah_text": occ.ayah_text,
                "context": context,
            })

        return concordance

    def get_root_frequency_list(
        self,
        min_occurrences: int = 1,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get frequency list of all roots in the Qur'an (from QAC data).

        Args:
            min_occurrences: Minimum occurrences to include
            limit: Maximum roots to return

        Returns:
            List of root frequency dictionaries sorted by frequency
        """
        rows = self.data_access.db.fetchall("""
            SELECT
                ta.root_id,
                COUNT(*) as frequency,
                COUNT(DISTINCT wt.surah_number) as surah_count,
                COUNT(DISTINCT wt.ayah_number) as ayah_count
            FROM token_analysis ta
            JOIN word_token wt ON wt.token_id = ta.token_id
            WHERE ta.dataset_id = 'qac-morphology'
              AND wt.edition_id = ?
              AND ta.root_id IS NOT NULL
            GROUP BY ta.root_id
            HAVING frequency >= ?
            ORDER BY frequency DESC
            LIMIT ?
        """, (self.edition_id, min_occurrences, limit))

        results = []
        for row in rows:
            root_id = row["root_id"]
            root_form = root_id.replace("qac-root:", "").replace("_", " ") if root_id else ""
            results.append({
                "root_id": root_id,
                "root_form": root_form,
                "frequency": row["frequency"],
                "surah_count": row["surah_count"],
                "ayah_count": row["ayah_count"],
            })

        return results

    def get_lemma_frequency_list(
        self,
        min_occurrences: int = 1,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get frequency list of all lemmas in the Qur'an (from QAC data).

        Args:
            min_occurrences: Minimum occurrences to include
            limit: Maximum lemmas to return

        Returns:
            List of lemma frequency dictionaries sorted by frequency
        """
        rows = self.data_access.db.fetchall("""
            SELECT
                ta.lemma_id,
                COUNT(*) as frequency,
                COUNT(DISTINCT wt.surah_number) as surah_count,
                COUNT(DISTINCT wt.ayah_number) as ayah_count
            FROM token_analysis ta
            JOIN word_token wt ON wt.token_id = ta.token_id
            WHERE ta.dataset_id = 'qac-morphology'
              AND wt.edition_id = ?
              AND ta.lemma_id IS NOT NULL
            GROUP BY ta.lemma_id
            HAVING frequency >= ?
            ORDER BY frequency DESC
            LIMIT ?
        """, (self.edition_id, min_occurrences, limit))

        results = []
        for row in rows:
            lemma_id = row["lemma_id"]
            lemma_form = lemma_id.replace("qac-lemma:", "") if lemma_id else ""
            results.append({
                "lemma_id": lemma_id,
                "lemma_form": lemma_form,
                "frequency": row["frequency"],
                "surah_count": row["surah_count"],
                "ayah_count": row["ayah_count"],
            })

        return results


def create_vocabulary_analyzer(
    edition_id: str = "tanzil-uthmani-v1",
    data_access: DataAccess | None = None,
) -> QuranicVocabulary:
    """
    Factory function to create a QuranicVocabulary analyzer.

    Args:
        edition_id: Text edition to analyze
        data_access: Optional DataAccess instance

    Returns:
        QuranicVocabulary instance
    """
    return QuranicVocabulary(data_access=data_access, edition_id=edition_id)
