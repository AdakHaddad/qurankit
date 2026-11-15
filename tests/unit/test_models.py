"""Unit tests for QuranKit data models."""

import pytest
from pydantic import ValidationError

from qurankit.models import (
    Annotation,
    Ayah,
    AyahMetadata,
    AyahText,
    ComparisonResult,
    Dataset,
    DatasetManifest,
    GrammarAnalysis,
    Lemma,
    LexicalEntry,
    LexicalResource,
    NormalizationProfile,
    ResearchInput,
    ResearchResult,
    ResearchRun,
    Root,
    SemanticRelation,
    Source,
    Surah,
    TextEdition,
    TokenAnalysis,
    WordToken,
)
from qurankit.models.enums import (
    AnnotationMethodType,
    ClaimCategory,
    MetadataType,
    RedistributionStatus,
    ScriptType,
    SearchMode,
    SourceType,
)


class TestEnums:
    """Test enum values."""

    def test_redistribution_status(self):
        assert RedistributionStatus.ALLOWED == "allowed"
        assert RedistributionStatus.RESTRICTED == "restricted"
        assert RedistributionStatus.UNKNOWN == "unknown"
        assert RedistributionStatus.NOT_REDISTRIBUTABLE == "not_redistributable"

    def test_source_type(self):
        assert SourceType.CORPUS == "corpus"
        assert SourceType.API == "api"
        assert SourceType.BOOK == "book"

    def test_script_type(self):
        assert ScriptType.UTHMANI == "uthmani"
        assert ScriptType.IMLAI == "imlai"
        assert ScriptType.SIMPLE == "simple"

    def test_annotation_method_type(self):
        assert AnnotationMethodType.SOURCE_ANNOTATION == "source_annotation"
        assert AnnotationMethodType.HUMAN_REVIEW == "human_review"
        assert AnnotationMethodType.ALGORITHMIC == "algorithmic"

    def test_claim_category(self):
        assert ClaimCategory.SOURCE_TEXT == "source_text"
        assert ClaimCategory.DETERMINISTIC_RESULT == "deterministic_result"
        assert ClaimCategory.COMPUTATIONAL_SUGGESTION == "computational_suggestion"

    def test_search_mode(self):
        assert SearchMode.EXACT_SOURCE == "exact_source"
        assert SearchMode.DIACRITICS_INSENSITIVE == "diacritics_insensitive"
        assert SearchMode.BROAD_ORTHOGRAPHIC == "broad_orthographic"

    def test_metadata_type(self):
        assert MetadataType.JUZ == "juz"
        assert MetadataType.PAGE == "page"
        assert MetadataType.REVELATION_ORDER == "revelation_order"


class TestProvenanceModels:
    """Test provenance models."""

    def test_source_creation(self):
        source = Source(
            source_id="test-source",
            title="Test Source",
            creator="Test Creator",
            source_type=SourceType.CORPUS,
            url="https://example.com",
        )
        assert source.source_id == "test-source"
        assert source.title == "Test Source"
        assert source.source_type == SourceType.CORPUS

    def test_source_optional_fields(self):
        source = Source(
            source_id="minimal",
            title="Minimal Source",
            source_type=SourceType.OTHER,
        )
        assert source.creator is None
        assert source.url is None
        assert source.persistent_id is None

    def test_dataset_creation(self):
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            license_id="MIT",
            schema_version="1.0",
        )
        assert dataset.dataset_id == "test-dataset"
        assert dataset.version == "1.0.0"
        assert dataset.redistribution_status == RedistributionStatus.UNKNOWN

    def test_dataset_with_license(self):
        dataset = Dataset(
            dataset_id="licensed-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Licensed Dataset",
            description="Dataset with license",
            license_id="CC-BY-4.0",
            license_url="https://creativecommons.org/licenses/by/4.0/",
            redistribution_status=RedistributionStatus.ALLOWED,
            schema_version="1.0",
        )
        assert dataset.redistribution_status == RedistributionStatus.ALLOWED
        assert dataset.license_id == "CC-BY-4.0"

    def test_dataset_manifest(self):
        source = Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)
        assert manifest.dataset.dataset_id == "test-dataset"
        assert manifest.source.source_id == "test-source"

    def test_dataset_record(self):

        from qurankit.models import DatasetRecord

        record = DatasetRecord(
            dataset_record_id="rec-1",
            dataset_id="test-dataset",
            source_record_id="src-1",
            record_type="text",
            record_checksum="abc123",
        )
        assert record.dataset_record_id == "rec-1"
        assert record.record_type == "text"


class TestTextModels:
    """Test core text models."""

    def test_surah_creation(self):
        surah = Surah(
            surah_number=1,
            name_arabic="الفاتحة",
            name_transliteration="Al-Fatihah",
            name_translation="The Opening",
            ayah_count=7,
        )
        assert surah.surah_number == 1
        assert surah.name_arabic == "الفاتحة"
        assert surah.ayah_count == 7

    def test_surah_validation(self):
        with pytest.raises(ValidationError):
            Surah(surah_number=0, name_arabic="Test", ayah_count=1)
        with pytest.raises(ValidationError):
            Surah(surah_number=115, name_arabic="Test", ayah_count=1)
        with pytest.raises(ValidationError):
            Surah(surah_number=1, name_arabic="Test", ayah_count=0)

    def test_ayah_creation(self):
        ayah = Ayah(surah_number=2, ayah_number=255)
        assert ayah.surah_number == 2
        assert ayah.ayah_number == 255
        assert ayah.reference == "2:255"

    def test_ayah_str_repr(self):
        ayah = Ayah(surah_number=1, ayah_number=1)
        assert str(ayah) == "1:1"
        assert repr(ayah) == "Ayah(1:1)"

    def test_text_edition(self):
        edition = TextEdition(
            edition_id="test-edition",
            dataset_id="test-dataset",
            name="Test Edition",
            script_type=ScriptType.UTHMANI,
            is_default=True,
        )
        assert edition.edition_id == "test-edition"
        assert edition.script_type == ScriptType.UTHMANI
        assert edition.is_default is True

    def test_ayah_text(self):
        ayah_text = AyahText(
            edition_id="test-edition",
            surah_number=1,
            ayah_number=1,
            text_original="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            checksum="abc123",
        )
        assert ayah_text.text_original == "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
        assert ayah_text.reference == "test-edition:1:1"

    def test_word_token(self):
        token = WordToken(
            token_id="token-1",
            edition_id="test-edition",
            surah_number=1,
            ayah_number=1,
            tokenization_id="tok-v1",
            token_index=0,
            surface_original="بِسْمِ",
            char_start=0,
            char_end=5,
        )
        assert token.token_index == 0
        assert token.surface_original == "بِسْمِ"
        assert token.reference == "test-edition:1:1:tok-v1:0"

    def test_word_token_offset_validation(self):
        with pytest.raises(ValidationError):
            WordToken(
                token_id="token-1",
                edition_id="test-edition",
                surah_number=1,
                ayah_number=1,
                tokenization_id="tok-v1",
                token_index=0,
                surface_original="test",
                char_start=10,
                char_end=5,  # end < start
            )

    def test_normalization_profile(self):
        profile = NormalizationProfile(
            profile_id="test-profile",
            name="Test Profile",
            version="1.0.0",
            description="A test profile",
            rules_json={"type": "exact"},
            implementation_version="0.1.0",
        )
        assert profile.profile_id == "test-profile"
        assert profile.rules_json["type"] == "exact"


class TestLexiconModels:
    """Test lexicon models."""

    def test_lexical_resource(self):
        resource = LexicalResource(
            lexical_resource_id="test-lexicon",
            dataset_id="test-dataset",
            title="Test Lexicon",
            language="ar",
        )
        assert resource.lexical_resource_id == "test-lexicon"
        assert resource.language == "ar"

    def test_lexical_entry(self):
        entry = LexicalEntry(
            lexical_entry_id="entry-1",
            lexical_resource_id="test-lexicon",
            headword_original="كتاب",
            headword_normalized="كتاب",
            root_form="ك ت ب",
        )
        assert entry.headword_original == "كتاب"
        assert entry.root_form == "ك ت ب"

    def test_lexical_sense(self):
        from qurankit.models import LexicalSense

        sense = LexicalSense(
            sense_id="sense-1",
            lexical_entry_id="entry-1",
            sense_number=1,
            definition_original="A book or writing",
            definition_language="en",
        )
        assert sense.sense_number == 1
        assert sense.definition_language == "en"

    def test_root(self):
        root = Root(
            root_id="root-1",
            root_form="ك ت ب",
            root_normalized="كتب",
        )
        assert root.root_form == "ك ت ب"
        assert root.root_normalized == "كتب"

    def test_lemma(self):
        lemma = Lemma(
            lemma_id="lemma-1",
            lemma_form="كتاب",
            lemma_normalized="كتاب",
            language="ar",
        )
        assert lemma.lemma_form == "كتاب"
        assert lemma.language == "ar"


class TestAnnotationModels:
    """Test annotation models."""

    def test_token_analysis(self):
        analysis = TokenAnalysis(
            analysis_id="analysis-1",
            token_id="token-1",
            dataset_id="test-dataset",
            root_id="root-1",
            lemma_id="lemma-1",
            part_of_speech="noun",
            morph_features_json={"number": "singular", "gender": "masculine"},
            method_type=AnnotationMethodType.SOURCE_ANNOTATION,
            confidence=0.95,
            is_preferred=True,
        )
        assert analysis.part_of_speech == "noun"
        assert analysis.confidence == 0.95
        assert analysis.is_preferred is True

    def test_token_analysis_confidence_validation(self):
        with pytest.raises(ValidationError):
            TokenAnalysis(
                analysis_id="analysis-1",
                token_id="token-1",
                method_type=AnnotationMethodType.SOURCE_ANNOTATION,
                confidence=1.5,  # > 1.0
            )
        with pytest.raises(ValidationError):
            TokenAnalysis(
                analysis_id="analysis-1",
                token_id="token-1",
                method_type=AnnotationMethodType.SOURCE_ANNOTATION,
                confidence=-0.1,  # < 0.0
            )

    def test_grammar_analysis(self):
        grammar = GrammarAnalysis(
            grammar_analysis_id="grammar-1",
            token_id="token-1",
            dataset_id="test-dataset",
            analysis_type="i'rab",
            role_label="subject",
            method_type=AnnotationMethodType.SOURCE_ANNOTATION,
        )
        assert grammar.analysis_type == "i'rab"
        assert grammar.role_label == "subject"

    def test_semantic_relation(self):
        relation = SemanticRelation(
            semantic_relation_id="rel-1",
            subject_type="lexical_entry",
            subject_id="entry-1",
            relation_type="synonym",
            object_type="lexical_entry",
            object_id="entry-2",
            dataset_id="test-dataset",
            method_type=AnnotationMethodType.SOURCE_ANNOTATION,
        )
        assert relation.relation_type == "synonym"
        assert relation.subject_id == "entry-1"

    def test_ayah_metadata(self):
        metadata = AyahMetadata(
            ayah_metadata_id="meta-1",
            surah_number=1,
            ayah_number=1,
            metadata_type=MetadataType.JUZ,
            value_text="1",
            dataset_id="test-dataset",
        )
        assert metadata.metadata_type == MetadataType.JUZ
        assert metadata.value_text == "1"

    def test_annotation(self):
        annotation = Annotation(
            annotation_id="ann-1",
            target_type="ayah",
            target_id="1:1",
            annotation_type="note",
            content_original="This is a note",
            method_type=AnnotationMethodType.HUMAN_REVIEW,
            review_status="reviewed",
        )
        assert annotation.target_type == "ayah"
        assert annotation.review_status == "reviewed"


class TestResearchModels:
    """Test research models."""

    def test_research_run(self):
        from datetime import UTC, datetime

        run = ResearchRun(
            run_id="run-1",
            operation="search",
            algorithm_name="exact_match",
            algorithm_version="1.0.0",
            parameters_json={"query": "test", "mode": "exact"},
            software_version="0.1.0",
            started_at=datetime.now(UTC),
        )
        assert run.operation == "search"
        assert run.algorithm_name == "exact_match"
        assert run.status == "running"

    def test_research_input(self):
        input_obj = ResearchInput(
            research_input_id="input-1",
            run_id="run-1",
            input_type="query",
            input_reference="test query",
            dataset_id="test-dataset",
        )
        assert input_obj.input_type == "query"
        assert input_obj.input_reference == "test query"

    def test_research_result(self):
        result = ResearchResult(
            result_id="result-1",
            run_id="run-1",
            result_type="exact_match",
            claim_category=ClaimCategory.DETERMINISTIC_RESULT,
            result_payload_json={"matches": ["1:1", "2:255"]},
            evidence_json={"sources": ["test-edition"]},
        )
        assert result.claim_category == ClaimCategory.DETERMINISTIC_RESULT
        assert result.result_payload_json["matches"] == ["1:1", "2:255"]

    def test_comparison_result(self):
        comparison = ComparisonResult(
            comparison_id="comp-1",
            left_reference="2:255",
            right_reference="2:123",
            comparison_method="token_overlap",
            method_version="1.0.0",
            score=0.75,
            alignment_json={"matched": ["word1", "word2"], "different": []},
            claim_category=ClaimCategory.DETERMINISTIC_RESULT,
        )
        assert comparison.score == 0.75
        assert comparison.comparison_method == "token_overlap"
        assert comparison.claim_category == ClaimCategory.DETERMINISTIC_RESULT


class TestModelSerialization:
    """Test model serialization/deserialization."""

    def test_surah_json_roundtrip(self):
        surah = Surah(
            surah_number=1,
            name_arabic="الفاتحة",
            name_transliteration="Al-Fatihah",
            name_translation="The Opening",
            ayah_count=7,
        )
        json_data = surah.model_dump()
        restored = Surah.model_validate(json_data)
        assert restored.surah_number == surah.surah_number
        assert restored.name_arabic == surah.name_arabic

    def test_ayah_text_json_roundtrip(self):
        ayah_text = AyahText(
            edition_id="test-edition",
            surah_number=1,
            ayah_number=1,
            text_original="بِسْمِ اللَّهِ",
            checksum="abc123",
        )
        json_data = ayah_text.model_dump()
        restored = AyahText.model_validate(json_data)
        assert restored.text_original == ayah_text.text_original
        assert restored.checksum == ayah_text.checksum

    def test_dataset_manifest_json_roundtrip(self):
        source = Source(
            source_id="test-source",
            title="Test Source",
            source_type=SourceType.CORPUS,
        )
        dataset = Dataset(
            dataset_id="test-dataset",
            version="1.0.0",
            source_id="test-source",
            name="Test Dataset",
            description="A test dataset",
            schema_version="1.0",
        )
        manifest = DatasetManifest(dataset=dataset, source=source)
        json_data = manifest.model_dump(mode="json")
        restored = DatasetManifest.model_validate(json_data)
        assert restored.dataset.dataset_id == "test-dataset"
        assert restored.source.title == "Test Source"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
