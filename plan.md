# Quran Research Engine --- Project Plan

**Status:** Initial project specification\
**Document version:** 0.1.0\
**Scope:** Text-first computational Qur'anic research framework

## 1. Vision

Build a modular, Python-first, open-source framework for systematically
retrieving, exploring, comparing, and analyzing the Qur'anic text and
its linguistic and structural features.

The framework should serve:

-   Researchers working with Qur'anic text and Arabic language data.
-   Developers building research applications.
-   Educators and students conducting structured textual exploration.
-   AI agents that need reliable, traceable research tools.

The initial product is a reusable Python library. MCP, REST APIs,
command-line tools, notebooks, and user-facing applications are
interfaces built on top of the same core functionality.

## 2. Product principles

1.  **Text-first, expandable:** Start with Qur'anic text, lexical
    resources, morphology, grammar, semantics, and textual
    relationships. Design extension points for tafsir, hadith, and other
    scholarly resources without requiring them in the MVP.
2.  **Source traceability:** Every imported annotation or dataset must
    retain source, version, license, and attribution metadata.
3.  **Preserve originals:** Never overwrite source text with normalized
    or transformed text.
4.  **Separate evidence from inference:** Distinguish source-provided
    annotations, deterministic computational results, model-generated
    suggestions, and scholarly interpretation.
5.  **Reproducibility:** Record dataset versions, algorithm versions,
    parameters, and normalization profiles used for a result.
6.  **Offline-capable:** Core research workflows should work without a
    hosted service after the required datasets are installed.
7.  **Provider-neutral:** The core library must not depend on a
    particular LLM, MCP client, cloud provider, or external API.
8.  **Modular dependencies:** Keep optional NLP, vector-search, graph,
    API, and agent dependencies out of the minimal installation.

## 3. Scope

### 3.1 MVP: included

#### Qur'anic text and structure

-   Canonical surah and ayah identifiers.
-   Source-preserving Arabic text storage.
-   Uthmani and Imlai representations where licensed and available.
-   Word-level segmentation and stable word identifiers.
-   Surah, ayah, juz, hizb, rubu', page, and other structural metadata
    when sourced.
-   Text and dataset validation.

#### Arabic text processing

-   Unicode normalization.
-   Configurable search normalization profiles.
-   Diacritic-aware and diacritic-insensitive search.
-   Explicit handling of hamza, alif variants, alif maqsurah, ta
    marbutah, Quranic annotation marks, and pause signs.
-   Exact, phrase, token, prefix, and fuzzy search.
-   Reversible or inspectable normalization mappings where practical.

#### Lexicon and Qur'anic vocabulary

-   Root and lemma lookup when supported by sourced annotations.
-   Dictionary entries from separately licensed sources.
-   Arabic definitions and source-language text.
-   Derivatives and morphological forms.
-   Synonym, antonym, and semantic relations only when attributed to a
    source or clearly marked as computational suggestions.
-   Qur'anic occurrence lists and contextual concordance.
-   Support for Qur'anic vocabulary resources such as *Al-Mufradat*
    where lawful digital data is available.

#### Morphology and grammar

-   Word-level morphological annotations.
-   Part of speech, lemma, root, and inflectional features where
    sourced.
-   Nahwu and i'rab annotations where reliable data is available.
-   Sarf and derivational relationships.
-   Annotation provenance and uncertainty.
-   No unsupported automatic assertion of a root or grammatical
    analysis.

#### Semantic and thematic exploration

-   Contextual concordance.
-   Word co-occurrence and collocation.
-   Semantic-field exploration.
-   Related-word and concept links with explicit provenance.
-   Wujuh wa nazair research support, preserving the cited scholarly
    source.
-   Optional semantic search as a discovery aid, never as a replacement
    for exact search.

#### Textual relationships and mutashabihat

-   Exact repeated phrase detection.
-   Near-duplicate phrase detection.
-   Similar ayah and passage discovery.
-   Word-order and lexical variation comparison.
-   Shared-root and shared-lemma analysis.
-   Similar openings, endings, and recurring expressions.
-   Results classified by method and confidence; similarity must not be
    presented as proof of interpretive equivalence.

#### Computational analysis

-   Letter, word, lemma, and root frequency.
-   Ayah and surah length statistics.
-   Distribution and co-occurrence analysis.
-   Reproducible statistical experiments.
-   Exportable result tables and machine-readable outputs.

#### Research interface foundations

-   Stable Python API.
-   CLI for common retrieval and dataset-management tasks.
-   Jupyter-friendly result objects and examples.
-   Optional MCP server exposing selected read-only research tools.

### 3.2 Designed for later extensions

These are not MVP requirements, but the data model and package
boundaries should permit them:

-   Tafsir corpora and comparative tafsir research.
-   Hadith collections, takhrij, isnad, narrator data, and grading
    opinions.
-   Scholar biographies, works, and attributed scholarly positions.
-   Ulum al-Qur'an resources, asbab al-nuzul, Makki/Madani studies, and
    nasikh-mansukh research.
-   Qira'at and their textual/phonetic annotations.
-   Tajwid, waqf, and ibtida'.
-   Fiqh and usul al-fiqh research.
-   Seerah and historical source integration.
-   Memorization, muraja'ah, and Hifz applications.
-   Web-based research explorer and hosted API.

### 3.3 Non-goals for the MVP

-   Producing autonomous religious rulings or fatwas.
-   Replacing tafsir, qualified scholarship, or human review.
-   Treating numerical patterns as proof of theological claims.
-   Generating unsourced interpretations.
-   Bundling copyrighted dictionaries, translations, or corpora without
    redistribution rights.
-   Requiring cloud access or an LLM for core functionality.

## 4. Research result categories

Every result should identify what kind of claim it represents.

  -----------------------------------------------------------------------
  Category                Meaning                 Example
  ----------------------- ----------------------- -----------------------
  Source text             Text reproduced from an An ayah in a named text
                          identified source       edition

  Source annotation       Annotation supplied by  A morphology tag from a
                          a corpus or scholar     cited corpus

  Deterministic result    Reproducible output     Exact phrase match
                          from a defined          
                          algorithm               

  Computational           Candidate requiring     Fuzzy semantic
  suggestion              validation              similarity

  Scholarly               A position attributed   A dictionary or tafsir
  interpretation          to a named work or      explanation
                          scholar                 

  Research hypothesis     A proposed pattern or   A possible structural
                          relationship            correspondence
  -----------------------------------------------------------------------

Do not collapse these categories into one unqualified answer.

## 5. Data architecture

### 5.1 Core entities

Initial logical entities:

-   `TextEdition`
-   `Surah`
-   `Ayah`
-   `WordToken`
-   `WordSegment` (optional, for sub-word segmentation)
-   `Dataset`
-   `Source`
-   `SourceEdition`
-   `Annotation`
-   `LexicalEntry`
-   `Root`
-   `Lemma`
-   `MorphologicalAnalysis`
-   `GrammarAnalysis`
-   `SemanticRelation`
-   `Occurrence`
-   `ResearchResult`
-   `AlgorithmVersion`

### 5.2 Identifier strategy

-   Use stable Qur'anic references such as `2:255` for surah:ayah.
-   Give each word token a stable identifier tied to the text edition
    and tokenization version.
-   Do not assume token indices are interchangeable across editions or
    tokenization schemes.
-   Preserve source identifiers when importing external corpora.
-   Record mappings between identifiers rather than silently replacing
    them.

### 5.3 Provenance fields

Imported data should, where available, include:

-   Source title and creator/author.
-   Source URL or persistent identifier.
-   Edition, publisher, publication year, volume, page, or entry.
-   Dataset release and retrieval date.
-   License and permitted uses.
-   Original source identifier.
-   Importer and transformation version.
-   Verification status and reviewer notes.

Missing bibliographic fields must remain explicitly unknown; do not
invent them.

### 5.4 Suggested storage strategy

Start simple:

-   SQLite for local structured data and metadata.
-   SQLite FTS5 for initial full-text search.
-   JSONL or Parquet for portable dataset exports where appropriate.
-   NetworkX for early graph exploration.
-   Optional vector index for semantic discovery.

Add PostgreSQL, a dedicated graph database, or external search
infrastructure only when demonstrated scale or collaboration needs
justify them.

## 6. Arabic text and normalization policy

Store original source text unchanged. Derived forms must be separate
fields or generated views.

Provide named normalization profiles, for example:

-   `exact_source`: exact comparison against the selected source
    representation.
-   `diacritics_insensitive`: removes specified diacritics while
    retaining other distinctions.
-   `search`: applies a documented set of search-oriented equivalences.
-   `uthmani_to_search`: maps selected Uthmani signs for search while
    preserving the original.
-   `custom`: user-specified normalization rules.

Normalization must be explicit in every search and comparison result. Do
not use one universal normalized form for every research task.

Test Unicode behavior, combining marks, Quranic annotation signs, hamza
forms, alif variants, alif maqsurah, ta marbutah, and pause marks.

## 7. Dataset strategy and licensing

Use source adapters rather than hard-coding one provider.

Candidate resources to evaluate include:

-   Quranic Arabic Corpus for word-level morphology and syntactic
    annotations.
-   Quran Foundation resources and APIs for Qur'anic text and related
    data.
-   OpenITI for classical Arabic textual resources.
-   CAMeL Tools and other Arabic NLP projects for optional general
    Arabic processing.
-   Digitized classical dictionaries and Qur'anic vocabulary works,
    subject to source and edition verification.

Evaluation checklist for each candidate:

1.  Is the source authoritative and suitable for the intended task?
2.  What exact edition or dataset release is provided?
3.  Is the Arabic text complete and correctly encoded?
4.  Are annotations human-authored, automatically generated, or mixed?
5.  Is the license compatible with use, modification, and
    redistribution?
6.  Can attribution and source references be preserved?
7.  Can the data be versioned and checksummed?
8.  Is there a known quality-control or correction process?

Do not infer redistribution permission from public web availability.
When rights are unclear, provide an adapter or user-supplied import
workflow instead of bundling the data.

## 8. Package and repository architecture

Proposed initial repository:

``` text
quran-research/
├── README.md
├── LICENSE
├── pyproject.toml
├── plan.md
├── AGENTS.md
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── datasets.md
│   ├── arabic-text-standard.md
│   ├── research-methodology.md
│   └── distribution.md
├── src/
│   └── quran_research/
│       ├── core/
│       ├── text/
│       ├── lexicon/
│       ├── morphology/
│       ├── syntax/
│       ├── semantics/
│       ├── search/
│       ├── mutashabihat/
│       ├── analysis/
│       ├── datasets/
│       └── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── golden/
├── examples/
├── benchmarks/
└── .github/
    └── workflows/
```

Keep MCP and API integrations optional. They may live in optional extras
initially and be split into separate distributions only when independent
release cycles or dependencies make that worthwhile.

## 9. Public interfaces

### Python API

The Python library is the source of truth for research functionality.
Example API sketches:

``` python
from quran_research import Quran

quran = Quran()

ayah = quran.ayah("2:255")
results = quran.search.phrase("...")
occurrences = quran.lexicon.occurrences(root="...")
matches = quran.mutashabihat.find("2:48")
comparison = quran.compare("2:48", "2:123")
```

These are design examples, not a commitment to final signatures. Final
APIs must be consistent, typed, documented, and tested.

### CLI

Provide commands for dataset inspection, installation, validation, and
basic search. Example sketches:

``` bash
quran-research data list
quran-research data install core
quran-research data validate core
quran-research search phrase "..."
```

### MCP and function calling

Expose a small set of well-defined, read-only tools after the underlying
Python functions are stable. Tool descriptions must explain input
formats, normalization, dataset requirements, and result provenance.

### REST API

Defer until a real web or multi-user application requires it. Do not
make the core library depend on a running API.

## 10. Distribution and hosting

### Source hosting

-   Host the canonical repository on GitHub.
-   Use issues and pull requests for contributions and review.
-   Use tags and release notes for versioned releases.
-   Use GitHub Actions for tests, linting, package builds, and release
    workflows.

### Python distribution

-   Publish the core package to PyPI.
-   Use modern build metadata in `pyproject.toml`.
-   Prefer PyPI Trusted Publishing from GitHub Actions rather than
    long-lived publishing tokens.
-   Follow semantic versioning once the public API stabilizes.
-   Keep optional dependencies in extras, for example
    `quran-research[api]` or `quran-research[mcp]`.

### Documentation

-   Maintain versioned user and developer documentation.
-   Start with Markdown documentation in the repository.
-   Publish with Read the Docs or GitHub Pages when useful.
-   Include installation, quick start, dataset setup, API reference,
    source attribution, and reproducibility guidance.

### Dataset hosting

-   Keep small manifests and metadata in Git.
-   Store larger redistributable datasets on an appropriate versioned
    data host such as Hugging Face Hub or Zenodo, subject to license.
-   For each release, publish a manifest containing source, version,
    license, checksum, and schema.
-   Support local dataset caches and offline use.
-   Avoid making the package installation download large datasets
    implicitly.

### Future hosted services

A hosted REST API, web explorer, or managed MCP endpoint is a later
product decision. The initial library should not require paid
infrastructure.

## 11. Testing and evaluation

### Text integrity

-   Verify expected surah and ayah counts against the selected edition's
    documented specification.
-   Validate references and ordering.
-   Detect missing, duplicate, or malformed records.
-   Compare imported text against trusted source checksums or reference
    fixtures where available.

### Arabic processing

-   Test Unicode normalization and combining marks.
-   Test diacritic-sensitive and insensitive search separately.
-   Test Uthmani/Imlai mapping without destroying original text.
-   Include edge cases for hamza, alif variants, ta marbutah, alif
    maqsurah, and Quranic marks.

### Lexicon and morphology

-   Use reviewed examples with source references.
-   Test ambiguous roots and forms.
-   Preserve multiple analyses when the source supports them.
-   Do not claim complete lexical or grammatical coverage unless
    demonstrated.

### Search and mutashabihat

-   Create gold-standard exact-match tests.
-   Evaluate fuzzy matching against reviewed examples.
-   Report the method and parameters used.
-   Measure false positives as well as recall.
-   Keep semantic similarity separate from scholarly equivalence.

### Reproducibility

-   Record dataset and algorithm versions.
-   Ensure deterministic algorithms produce stable outputs.
-   Test serialization and export.
-   Include end-to-end examples that can run offline.

## 12. Development milestones

### Phase 0 --- Repository and standards

-   Create repository and packaging skeleton.
-   Finalize identifiers and core data models.
-   Write Arabic text and normalization standard.
-   Establish provenance and licensing manifest formats.
-   Select initial source datasets after review.

**Exit criteria:** A documented schema and a minimal package that
installs and passes CI.

### Phase 1 --- Qur'anic core

-   Load a verified, licensed text edition.
-   Implement surah/ayah retrieval.
-   Implement word token records and structural metadata.
-   Implement text validation and local storage.

**Exit criteria:** Reliable retrieval and integrity tests for the chosen
edition.

### Phase 2 --- Search and lexical layer

-   Implement normalization profiles.
-   Add exact, phrase, token, and occurrence search.
-   Add dictionary adapter interface.
-   Import one suitable lexical dataset if licensing and quality permit.
-   Add root and lemma lookup from a reviewed annotation source.

**Exit criteria:** Search results preserve original text and identify
their data source.

### Phase 3 --- Linguistic analysis

-   Add morphology and grammatical annotation adapters.
-   Add word-level and ayah-level analysis.
-   Preserve ambiguity and source attribution.

**Exit criteria:** Reviewed test cases demonstrate correct handling of
supported annotations.

### Phase 4 --- Mutashabihat and computational research

-   Implement exact repeated phrase detection.
-   Add configurable similarity methods.
-   Add comparison reports and statistical tools.
-   Build benchmark and reviewed evaluation sets.

**Exit criteria:** Results are reproducible and clearly classified by
method.

### Phase 5 --- Developer and agent interfaces

-   Stabilize Python SDK.
-   Add CLI and notebook examples.
-   Add optional MCP tools.
-   Consider REST API only if needed.

**Exit criteria:** A researcher and an agent can use the same tested
core operations.

### Phase 6 --- Extensions

-   Add optional tafsir and hadith adapters.
-   Add qira'at, tajwid, waqf, and other scholarly datasets.
-   Add Hifz applications and a research explorer as separate consumers.

**Exit criteria:** Extensions do not compromise core independence or
provenance rules.

## 13. Initial release acceptance criteria

The first usable alpha should:

-   Install in a clean supported Python environment.
-   Load a documented and licensed Qur'anic text dataset.
-   Retrieve surahs, ayat, and word tokens by stable references.
-   Preserve source text and expose explicit normalization.
-   Perform exact and phrase search.
-   Expose dataset provenance and version metadata.
-   Include tests, examples, and basic documentation.
-   Work offline after data installation.
-   Avoid requiring an LLM, MCP server, or hosted database.

## 14. Open decisions

Do not silently settle these during implementation:

-   Which Qur'anic text edition(s) are included in the first release?
-   Which word segmentation convention and source identifiers are
    adopted?
-   Which lexical dataset can legally and technically be redistributed?
-   Which morphology and i'rab annotations are reliable enough to
    support?
-   Which Python versions are officially supported?
-   Which license is selected for original code?
-   Whether datasets are downloaded separately or distributed as
    optional packages.

Record the rationale for each decision in the relevant documentation.
