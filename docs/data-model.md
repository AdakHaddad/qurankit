# QuranKit --- Data Model

**Document status:** Initial design proposal\
**Version:** 0.1.0\
**Applies to:** QuranKit core text-first research framework

This document defines the initial logical data model for Qur'anic text,
word-level records, linguistic annotations, lexical resources, dataset
provenance, and computational research results.

It is a design specification, not a claim that these tables or APIs have
already been implemented. The schema should evolve through reviewed
migrations as real datasets are evaluated.

## 1. Design goals

The data model must:

1.  Preserve every imported source representation without destructive
    modification.
2.  Give surahs, ayat, and word tokens stable, unambiguous references.
3.  Support multiple text editions, orthographies, tokenizations, and
    readings without conflating them.
4.  Represent lexical and linguistic analyses as sourced annotations,
    not unquestionable facts.
5.  Preserve multiple competing analyses where the data supports them.
6.  Make dataset provenance and licensing traceable down to individual
    records or annotation batches.
7.  Support deterministic search and computational analysis.
8.  Remain usable in a local SQLite installation, with a path to
    PostgreSQL later.
9.  Avoid requiring an LLM, vector database, graph database, or hosted
    service.

## 2. Core modeling principles

### 2.1 Separate canonical structure from text editions

The Qur'anic reference `2:255` identifies surah 2, ayah 255. It does
not, by itself, identify a particular digital text representation.

A text edition identifies the source and representation of the text.
Different editions may differ in orthography, symbols, metadata, or
tokenization. Store them separately.

### 2.2 Preserve original data

For each imported text or annotation, retain:

-   The original value as received.
-   The source and dataset version.
-   The source record identifier, if available.
-   The transformation applied during import.
-   The transformed value used internally, if any.

Never replace original Arabic text with normalized text.

### 2.3 Distinguish a word token from a linguistic word analysis

A token is a specific occurrence in a specific text edition and
tokenization. Its root, lemma, part of speech, and grammatical role are
analyses attached to that occurrence.

One token may have multiple analyses. A root may be unknown, disputed,
or absent from a source. Do not force every token to have one.

### 2.4 Distinguish lexical meaning from contextual interpretation

A dictionary entry is not the same thing as the meaning of a word in a
particular ayah. Model dictionary definitions, occurrence-level notes,
semantic relations, and scholarly interpretations separately.

### 2.5 Make provenance first-class

A result should be traceable to the dataset, edition, source, method,
and software version that produced it.

## 3. Entity relationship overview

The central relationships are:

``` text
Source ──< Dataset ──< DatasetRecord
                    │
                    ├── TextEdition ──< AyahText ──< WordToken
                    │                                  │
                    │                                  └──< TokenAnalysis
                    │
                    ├── LexicalResource ──< LexicalEntry
                    │                            │
                    │                            └──< LexicalSense
                    │
                    └── AnnotationSet ──< Annotation

Surah ──< Ayah
Ayah ──< AyahMetadata
WordToken ──< TokenLexicalLink >── LexicalEntry
ResearchRun ──< ResearchResult
ResearchRun ──< ResearchInput
```

The diagram is conceptual. A first SQLite implementation may use fewer
physical tables, provided it preserves these distinctions and can
migrate cleanly.

## 4. Core identifiers

Use explicit, documented identifiers.

  -------------------------------------------------------------------------------------------
  Object                  Suggested identifier                        Example
  ----------------------- ------------------------------------------- -----------------------
  Surah                   `surah_number`                              `2`

  Ayah                    `(surah_number, ayah_number)`               `2:255`

  Text edition            `edition_id`                                `uthmani-example-v1`

  Ayah text               `(edition_id, surah_number, ayah_number)`   Edition-specific
                                                                      `2:255`

  Word token              `token_id`                                  `uuid` or stable
                                                                      composite key

  Dataset                 `dataset_id` + `version`                    `corpus-name@1.0.0`

  Lexical entry           `lexical_entry_id`                          Source-preserving
                                                                      identifier

  Annotation              `annotation_id`                             `uuid`

  Research run            `run_id`                                    `uuid`
  -------------------------------------------------------------------------------------------

A word token should be tied to a text edition and a tokenization
version. A simple display reference such as `2:255:3` may be offered to
users, but it must not be treated as globally stable across all editions
and tokenization schemes.

Recommended human-readable reference:

``` text
<edition_id>:<surah>:<ayah>:<tokenization_id>:<token_index>
```

Example:

``` text
uthmani-example-v1:2:255:tok-v1:3
```

The example is illustrative only.

## 5. Logical entities

### 5.1 Source

Represents the bibliographic or digital origin of a dataset.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `source_id`             string, primary key     Internal stable ID

  `title`                 string                  Source title

  `creator`               string, nullable        Author, organization,
                                                  or maintainer

  `source_type`           enum/string             Corpus, book, API,
                                                  manuscript, database,
                                                  etc.

  `url`                   string, nullable        Source location

  `persistent_id`         string, nullable        DOI or other persistent
                                                  identifier

  `publisher`             string, nullable        Publisher or issuing
                                                  body

  `publication_year`      integer, nullable       Do not infer if unknown

  `notes`                 text, nullable          Bibliographic or
                                                  evaluation notes
  -----------------------------------------------------------------------

One source may provide multiple datasets or editions.

### 5.2 Dataset

Represents an importable, versioned data release.

  -------------------------------------------------------------------------
  Field                     Type                    Notes
  ------------------------- ----------------------- -----------------------
  `dataset_id`              string, primary key     Stable dataset name

  `version`                 string                  Source release/version

  `source_id`               foreign key             Originating source

  `name`                    string                  Display name

  `description`             text                    Contents and intended
                                                    use

  `license_id`              string, nullable        SPDX identifier or
                                                    documented custom
                                                    license

  `license_url`             string, nullable        License text

  `redistribution_status`   enum                    `allowed`,
                                                    `restricted`,
                                                    `unknown`,
                                                    `not_redistributable`

  `retrieved_at`            datetime, nullable      Retrieval timestamp

  `checksum_algorithm`      string, nullable        For example `sha256`

  `checksum`                string, nullable        Checksum of source
                                                    artifact

  `schema_version`          string                  Import schema version

  `language`                string, nullable        BCP 47 or documented
                                                    language code

  `metadata_json`           JSON, nullable          Additional source
                                                    metadata
  -------------------------------------------------------------------------

Do not treat `unknown` redistribution status as permission to
redistribute.

### 5.3 DatasetRecord

Optional but recommended when individual imported records need their own
provenance.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `dataset_record_id`     string, primary key     Internal record ID

  `dataset_id`            foreign key             Dataset release

  `source_record_id`      string, nullable        Original record key

  `record_type`           string                  Text, lexical entry,
                                                  annotation, etc.

  `record_checksum`       string, nullable        Hash of original record

  `raw_payload`           text/JSON, nullable     Original payload if
                                                  storage policy permits

  `imported_at`           datetime                Import timestamp
  -----------------------------------------------------------------------

For large datasets, store raw source artifacts separately and retain a
stable path or object key plus checksum.

### 5.4 Surah

Represents the canonical surah index.

  Field                    Type                    Notes
  ------------------------ ----------------------- ---------------------------------------
  `surah_number`           integer, primary key    1--114
  `name_arabic`            text                    Name from a selected reference source
  `name_transliteration`   text, nullable          Display metadata
  `name_translation`       text, nullable          Display metadata
  `ayah_count`             integer                 Validate against selected structure
  `metadata_source_id`     foreign key, nullable   Source of metadata

Names and descriptive metadata should be source-attributed. Do not
assume that one transliteration or translation is canonical.

### 5.5 Ayah

Represents the canonical location of an ayah, independent of a specific
digital text edition.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `surah_number`          integer, primary key    Foreign key to Surah
                          part                    

  `ayah_number`           integer, primary key    Local ayah number
                          part                    

  `global_ayah_number`    integer, nullable       Common sequence number
                                                  if adopted

  `metadata_json`         JSON, nullable          Additional sourced
                                                  structural metadata
  -----------------------------------------------------------------------

Primary key: `(surah_number, ayah_number)`.

### 5.6 TextEdition

Represents a text source, orthographic representation, or reading
edition.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `edition_id`            string, primary key     Internal stable
                                                  identifier

  `dataset_id`            foreign key             Dataset providing the
                                                  text

  `name`                  string                  Edition name

  `script_type`           string                  For example Uthmani or
                                                  Imlai

  `reading_id`            string, nullable        Qira'ah/riwayah
                                                  identifier when
                                                  applicable

  `orthography`           string, nullable        Source description

  `tokenization_id`       string, nullable        Tokenization
                                                  scheme/version

  `is_default`            boolean                 Default display
                                                  edition, not a claim of
                                                  universal authority

  `notes`                 text, nullable          Differences and known
                                                  limitations
  -----------------------------------------------------------------------

Do not merge qira'at into a single text field. Represent readings and
their source-specific variants explicitly when that scope is
implemented.

### 5.7 AyahText

Stores the exact ayah string for a particular edition.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `edition_id`            foreign key, primary    Text edition
                          key part                

  `surah_number`          integer, primary key    Canonical location
                          part                    

  `ayah_number`           integer, primary key    Canonical location
                          part                    

  `text_original`         text                    Exact source string

  `text_display`          text, nullable          Display-only
                                                  transformation, if
                                                  needed

  `source_record_id`      string, nullable        Original record
                                                  identifier

  `checksum`              string, nullable        Integrity check

  `metadata_json`         JSON, nullable          Source-specific
                                                  metadata
  -----------------------------------------------------------------------

`text_original` must not be rewritten by search normalization,
typography, or display formatting.

### 5.8 WordToken

Represents a token occurrence in a particular ayah text and
tokenization.

  Field                  Type                  Notes
  ---------------------- --------------------- ----------------------------------------
  `token_id`             string, primary key   Stable internal ID
  `edition_id`           foreign key           Text edition
  `surah_number`         integer               Ayah location
  `ayah_number`          integer               Ayah location
  `tokenization_id`      string                Segmentation scheme/version
  `token_index`          integer               Position within ayah under this scheme
  `surface_original`     text                  Exact token as segmented from source
  `char_start`           integer, nullable     Offset into source ayah text
  `char_end`             integer, nullable     Exclusive end offset
  `source_record_id`     string, nullable      Source token ID
  `segmentation_notes`   text, nullable        Notes about segmentation

Constraints:

-   Unique
    `(edition_id, surah_number, ayah_number, tokenization_id, token_index)`.
-   Foreign key to the matching `AyahText`.
-   Offsets must use a documented convention, such as Unicode code-point
    offsets into `text_original`.
-   Do not assume a token is always equivalent to a morphological word.
    Clitics and segmentation conventions may differ.

### 5.9 NormalizationProfile

Defines a named and versioned text transformation.

  Field                      Type                  Notes
  -------------------------- --------------------- --------------------------------------
  `profile_id`               string, primary key   For example `search-v1`
  `name`                     string                Human-readable name
  `version`                  string                Profile version
  `description`              text                  Intended use
  `rules_json`               JSON                  Explicit transformations and options
  `implementation_version`   string                Code version
  `created_at`               datetime              Creation timestamp

A normalized token or ayah string may be cached for performance, but it
must reference the profile and source text it was derived from.

### 5.10 LexicalResource

Represents a dictionary, lexicon, or vocabulary source.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `lexical_resource_id`   string, primary key     Internal ID

  `dataset_id`            foreign key             Dataset release

  `title`                 string                  Work or resource title

  `author`                string, nullable        Author/compiler

  `edition`               string, nullable        Edition information

  `language`              string                  Entry language

  `scope`                 string, nullable        General Arabic,
                                                  Qur'anic vocabulary,
                                                  etc.

  `notes`                 text, nullable          Editorial notes
  -----------------------------------------------------------------------

### 5.11 LexicalEntry

Represents a dictionary headword or lexical record.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `lexical_entry_id`      string, primary key     Internal ID

  `lexical_resource_id`   foreign key             Source lexicon

  `source_entry_id`       string, nullable        Original entry key

  `headword_original`     text                    Exact source headword

  `headword_normalized`   text, nullable          Search helper only

  `root_form`             text, nullable          Only when source
                                                  explicitly supplies or
                                                  supports it

  `entry_text_original`   text, nullable          Original entry text

  `entry_location`        text, nullable          Volume/page/entry
                                                  reference

  `metadata_json`         JSON, nullable          Additional source data
  -----------------------------------------------------------------------

### 5.12 LexicalSense

Separates multiple meanings or senses within an entry.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `sense_id`              string, primary key     Internal ID

  `lexical_entry_id`      foreign key             Parent entry

  `sense_number`          integer, nullable       Source ordering

  `definition_original`   text                    Source wording

  `definition_language`   string                  Language tag

  `gloss`                 text, nullable          Short gloss; identify
                                                  if editorial

  `usage_note`            text, nullable          Source-provided note

  `source_location`       text, nullable          Page or section

  `editorial_status`      string                  Source text, edited
                                                  transcription, etc.
  -----------------------------------------------------------------------

Do not silently rewrite classical dictionary definitions. If a modern
summary is added, store it separately and identify it as an editorial or
generated gloss.

### 5.13 Root and Lemma

Root and lemma are distinct linguistic concepts and should not be
represented by one overloaded field.

**Root**

  Field               Type                  Notes
  ------------------- --------------------- ----------------------------
  `root_id`           string, primary key   Internal identifier
  `root_form`         text                  Arabic root representation
  `root_normalized`   text, nullable        Search helper
  `notes`             text, nullable        Editorial notes

**Lemma**

  Field                Type                  Notes
  -------------------- --------------------- ----------------------
  `lemma_id`           string, primary key   Internal identifier
  `lemma_form`         text                  Lemma representation
  `lemma_normalized`   text, nullable        Search helper
  `language`           string                Language tag
  `notes`              text, nullable        Editorial notes

A token's connection to a root or lemma belongs in its analysis record,
because analyses may differ.

### 5.14 TokenAnalysis

Represents one analysis of a token from a named source or method.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `analysis_id`           string, primary key     Internal ID

  `token_id`              foreign key             Analyzed token

  `dataset_id`            foreign key, nullable   Source dataset, if
                                                  imported

  `root_id`               foreign key, nullable   Root candidate

  `lemma_id`              foreign key, nullable   Lemma candidate

  `part_of_speech`        string, nullable        Source tag or mapped
                                                  tag

  `morph_features_json`   JSON                    Inflectional and
                                                  derivational features

  `segmentation_json`     JSON, nullable          Morpheme/clitic
                                                  structure if available

  `method_type`           enum/string             `source_annotation`,
                                                  `human_review`,
                                                  `algorithmic`

  `confidence`            number, nullable        Only if meaningful and
                                                  documented

  `is_preferred`          boolean                 Project curation
                                                  choice, not absolute
                                                  truth

  `notes`                 text, nullable          Ambiguity and rationale
  -----------------------------------------------------------------------

If confidence is stored, document what it means. Do not compare
confidence values from unrelated models or annotation sources as though
they were calibrated identically.

### 5.15 GrammarAnalysis

Represents syntax, i'rab, or other grammar annotations.

  ------------------------------------------------------------------------
  Field                    Type                    Notes
  ------------------------ ----------------------- -----------------------
  `grammar_analysis_id`    string, primary key     Internal ID

  `token_id`               foreign key, nullable   Token-level annotation

  `ayah_text_key`          foreign key, nullable   Ayah-level annotation

  `dataset_id`             foreign key, nullable   Source

  `analysis_type`          string                  Nahwu, i'rab,
                                                   dependency, etc.

  `role_label`             string, nullable        Source's grammatical
                                                   role

  `parent_token_id`        foreign key, nullable   Dependency relation if
                                                   applicable

  `explanation_original`   text, nullable          Source explanation

  `method_type`            string                  Source, reviewed,
                                                   algorithmic

  `metadata_json`          JSON, nullable          Source-specific details
  ------------------------------------------------------------------------

A grammar annotation may apply to a phrase or ayah rather than one
token. A later implementation may introduce a general annotation-target
table to handle spans and groups.

### 5.16 SemanticRelation

Represents a sourced or explicitly computed relationship between lexical
or conceptual objects.

  ------------------------------------------------------------------------
  Field                    Type                    Notes
  ------------------------ ----------------------- -----------------------
  `semantic_relation_id`   string, primary key     Internal ID

  `subject_type`           string                  Lexical entry, lemma,
                                                   concept, etc.

  `subject_id`             string                  Subject identifier

  `relation_type`          string                  Synonym, antonym,
                                                   related concept, etc.

  `object_type`            string                  Target entity type

  `object_id`              string                  Target identifier

  `dataset_id`             foreign key, nullable   Source

  `method_type`            string                  Source annotation,
                                                   human review,
                                                   algorithmic

  `evidence_note`          text, nullable          Supporting evidence

  `confidence`             number, nullable        Documented if used
  ------------------------------------------------------------------------

Do not encode a relationship as a scholarly fact when it is only a model
suggestion or vector-neighbor result.

### 5.17 AyahMetadata

Stores sourced structural or descriptive metadata separately from the
canonical ayah location.

Examples include juz, hizb, rubu', page, ruku', Makki/Madani
classification, revelation order, and other study metadata.

  Field                Type                  Notes
  -------------------- --------------------- -----------------------------------------
  `ayah_metadata_id`   string, primary key   Internal ID
  `surah_number`       integer               Ayah location
  `ayah_number`        integer               Ayah location
  `metadata_type`      string                `juz`, `page`, `revelation_order`, etc.
  `value_text`         text                  Flexible value representation
  `dataset_id`         foreign key           Source
  `source_reference`   text, nullable        Page, section, or record
  `notes`              text, nullable        Disagreement or caveat

Some metadata applies to ranges of ayat rather than individual ayat. A
future `AyahRange` entity may be preferable for range-based structure.
Do not duplicate range metadata onto every ayah without recording the
original range semantics.

### 5.18 Annotation

A general-purpose annotation entity for data that does not fit a
specialized table.

  Field                       Type                    Notes
  --------------------------- ----------------------- ----------------------------------------
  `annotation_id`             string, primary key     Internal ID
  `target_type`               string                  Ayah, token, span, lexical entry, etc.
  `target_id`                 string                  Target identifier
  `annotation_type`           string                  Topic, rhetoric, note, variant, etc.
  `content_original`          text, nullable          Source wording
  `content_structured_json`   JSON, nullable          Structured annotation
  `dataset_id`                foreign key, nullable   Source dataset
  `method_type`               string                  Source, human review, algorithmic
  `review_status`             string                  Unreviewed, reviewed, disputed, etc.

A general annotation should not replace specialized, queryable entities
such as `TokenAnalysis` or `LexicalSense`.

## 6. Research execution and reproducibility

### 6.1 ResearchRun

Records an executed research operation.

  ----------------------------------------------------------------------------
  Field                        Type                    Notes
  ---------------------------- ----------------------- -----------------------
  `run_id`                     string, primary key     Unique run

  `operation`                  string                  Search, comparison,
                                                       frequency, similarity,
                                                       etc.

  `algorithm_name`             string                  Method identifier

  `algorithm_version`          string                  Version

  `parameters_json`            JSON                    Exact parameters

  `normalization_profile_id`   string, nullable        Profile used

  `software_version`           string                  QuranKit version

  `started_at`                 datetime                Run timestamp

  `completed_at`               datetime, nullable      Completion timestamp

  `status`                     string                  Completed, failed,
                                                       partial

  `environment_json`           JSON, nullable          Relevant runtime
                                                       details
  ----------------------------------------------------------------------------

### 6.2 ResearchInput

Links a research run to its inputs.

  Field                 Type                    Notes
  --------------------- ----------------------- -----------------------------------
  `research_input_id`   string, primary key     Internal ID
  `run_id`              foreign key             Research run
  `input_type`          string                  Ayah, token, dataset, query, etc.
  `input_reference`     text                    Stable reference
  `dataset_id`          foreign key, nullable   Dataset version used

### 6.3 ResearchResult

Stores or indexes the output of a research run.

  -----------------------------------------------------------------------
  Field                   Type                    Notes
  ----------------------- ----------------------- -----------------------
  `result_id`             string, primary key     Internal ID

  `run_id`                foreign key             Producing run

  `result_type`           string                  Exact match, similarity
                                                  candidate, statistic,
                                                  etc.

  `claim_category`        string                  Source annotation,
                                                  deterministic result,
                                                  suggestion, hypothesis

  `result_payload_json`   JSON                    Structured result

  `evidence_json`         JSON, nullable          Supporting references

  `limitations`           text, nullable          Known caveats
  -----------------------------------------------------------------------

For large outputs, store result files separately and keep a URI/path,
checksum, and schema version in the record.

## 7. Search data model

Search should operate on indexed derived fields while retaining a path
to source text.

Possible derived indexes:

-   Exact source text index.
-   Diacritic-insensitive text index.
-   Named normalization-profile index.
-   Token surface index.
-   Lemma index.
-   Root index.
-   Lexical headword index.
-   Phrase and n-gram index.

Every search request should declare:

-   Target scope: ayah, token, lexical entry, or all supported.
-   Text edition(s).
-   Search mode.
-   Normalization profile.
-   Whether diacritics matter.
-   Whether matching is exact, prefix, fuzzy, morphological, or
    semantic.

Search results should include the original source text and stable
references, not only normalized strings.

Semantic search is optional and must be labeled as candidate discovery.
Store embedding model, model version, text input, and vector-index
version if embeddings are added.

## 8. Mutashabihat and comparison model

Do not store all similarity as one generic score. Record the comparison
method and evidence.

A comparison result should be able to represent:

-   Exact phrase overlap.
-   Shared token sequence.
-   Near-duplicate sequence.
-   Shared lemma or root.
-   Word-order difference.
-   Insertion, deletion, or substitution.
-   Similar opening or ending.
-   Semantic candidate relationship.

Suggested logical record:

  ----------------------------------------------------------------------------
  Field                        Type                    Notes
  ---------------------------- ----------------------- -----------------------
  `comparison_id`              string, primary key     Comparison identifier

  `left_reference`             text                    Ayah or span reference

  `right_reference`            text                    Ayah or span reference

  `comparison_method`          string                  Exact, token edit
                                                       distance, lemma
                                                       overlap, etc.

  `method_version`             string                  Algorithm version

  `normalization_profile_id`   string, nullable        Used profile

  `score`                      number, nullable        Method-specific score

  `alignment_json`             JSON                    Matched and differing
                                                       spans/tokens

  `claim_category`             string                  Usually deterministic
                                                       result or suggestion

  `review_status`              string                  Unreviewed, reviewed,
                                                       disputed

  `run_id`                     foreign key             Reproducibility link
  ----------------------------------------------------------------------------

A similarity score must never be presented as proof that two ayat have
the same meaning or interpretation.

## 9. Suggested SQLite implementation

Start with relational tables and foreign keys. Use SQLite features
conservatively so migration to PostgreSQL remains feasible.

Recommended initial choices:

-   `INTEGER` for numeric canonical indices.
-   `TEXT` for Arabic text and identifiers.
-   ISO 8601 UTC timestamps for stored timestamps.
-   JSON stored as `TEXT` with validation in application code, or SQLite
    JSON functions where available.
-   Foreign-key enforcement enabled on every connection.
-   Explicit unique constraints and indexes.
-   FTS5 for full-text search, with separate indexes for separate
    normalization profiles.

Potential indexes:

``` sql
CREATE INDEX idx_ayah_text_location
ON ayah_text (surah_number, ayah_number);

CREATE INDEX idx_word_token_location
ON word_token (
    edition_id,
    surah_number,
    ayah_number,
    tokenization_id,
    token_index
);

CREATE INDEX idx_token_analysis_root
ON token_analysis (root_id);

CREATE INDEX idx_token_analysis_lemma
ON token_analysis (lemma_id);

CREATE INDEX idx_lexical_entry_headword
ON lexical_entry (headword_normalized);
```

These are illustrative. Final SQL must match the implemented schema and
migration system.

## 10. Data validation rules

Every dataset importer should validate:

1.  Required metadata and license status are present or explicitly
    unknown.
2.  Source and dataset identifiers are stable.
3.  Surah and ayah references are valid for the selected structure.
4.  Duplicate records are detected.
5.  Text is valid Unicode and original values are preserved.
6.  Word token indices are ordered and unique within their tokenization.
7.  Character offsets follow the documented convention and remain within
    the source string.
8.  Foreign keys resolve.
9.  Normalized fields identify the profile and implementation version.
10. Imported annotations retain source record identifiers where
    available.

Validation reports should distinguish errors, warnings, and
informational messages. An importer must not silently discard invalid
records.

## 11. Example records

The following examples are structural illustrations. They do not provide
Qur'anic quotations or assert a particular linguistic analysis.

### Ayah text record

``` json
{
  "edition_id": "example-edition-v1",
  "surah_number": 2,
  "ayah_number": 255,
  "text_original": "<exact source text stored here>",
  "source_record_id": "source-specific-record-id",
  "checksum": "sha256:..."
}
```

### Word token record

``` json
{
  "token_id": "example-token-id",
  "edition_id": "example-edition-v1",
  "surah_number": 2,
  "ayah_number": 255,
  "tokenization_id": "example-tokenization-v1",
  "token_index": 1,
  "surface_original": "<exact token from source>",
  "char_start": 0,
  "char_end": 8
}
```

### Token analysis record

``` json
{
  "analysis_id": "example-analysis-id",
  "token_id": "example-token-id",
  "dataset_id": "example-corpus",
  "root_id": null,
  "lemma_id": null,
  "part_of_speech": null,
  "morph_features_json": {},
  "method_type": "source_annotation",
  "confidence": null,
  "is_preferred": false
}
```

Null values are intentional when the source does not provide an
analysis.

## 12. Migration and versioning policy

-   Version the database schema independently from the package version.
-   Use explicit, ordered migrations.
-   Never mutate imported source artifacts as a migration side effect.
-   Make migrations testable on both empty and populated databases.
-   Preserve identifiers or provide explicit mapping tables when
    identifiers change.
-   Record the dataset and schema versions used to build a local
    database.
-   Provide a validation command after dataset import or migration.
-   Keep a rollback or recovery strategy for destructive schema changes.

## 13. Decisions to resolve before implementation

The following choices require a documented decision:

1.  Which digital Qur'anic text edition is the first supported source?
2.  Which source provides canonical surah and ayah metadata?
3.  Which tokenization convention is adopted first?
4.  Are token IDs UUIDs, deterministic hashes, or composite identifiers?
5.  Which Unicode offset convention is used?
6.  Which morphology corpus is supported first, and what is its license?
7.  Which lexical resources may be redistributed?
8.  Which metadata belongs in core tables versus source-specific JSON?
9.  Which schema migration tool will be used?
10. Which fields are required for a first alpha release?

Do not finalize the schema around hypothetical datasets. Evaluate actual
source formats and licenses, then adapt the import model while
preserving the principles in this document.

## 14. Recommended implementation order

1.  Implement `Source`, `Dataset`, and dataset manifest validation.
2.  Implement `Surah`, `Ayah`, `TextEdition`, and `AyahText`.
3.  Add a verified text importer and integrity checks.
4.  Implement `WordToken` with a documented tokenization scheme.
5.  Add normalization profiles and derived search indexes.
6.  Add lexical-resource and lexical-entry adapters.
7.  Add token morphology and grammar annotations.
8.  Add research-run and result provenance.
9.  Add mutashabihat comparison records after benchmark examples exist.

This order establishes trustworthy source text and provenance before
adding increasingly interpretive layers.
