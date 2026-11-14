# QuranKit Dataset Evaluation

> Status: Initial research and integration assessment  
> Last reviewed: 2026-11-14  
> Scope: Candidate datasets and services for the QuranKit research framework  
>
> This document is a technical due-diligence record, not legal advice. Re-check each source's current terms before every release or redistribution.

## 1. Purpose

QuranKit is intended to be a Python-first framework for reproducible Qur'anic research. Its datasets must be treated as independently governed research assets, not as interchangeable files bundled with the software.

This document evaluates candidate sources for:

- Qur'anic Arabic text and structural metadata
- Morphological and syntactic annotation
- Lexical resources and classical dictionaries
- Historical Arabic and Islamicate texts
- Tafsir, translations, hadith, and other scholarly material
- API-based content providers

The central rule is **source-first data governance**: every imported record must retain its source, edition or release, license/terms, retrieval date, attribution, and transformation history.

## 2. Executive recommendation

### Recommended initial path

1. Use **Tanzil** as the leading candidate for a baseline Qur'anic text edition and structural metadata, subject to strict preservation of the supplied text and attribution.
2. Build QuranKit's own deterministic indexing, tokenization interfaces, search, concordance, comparison, and research-run infrastructure independently of third-party annotation.
3. Treat **Quranic Arabic Corpus (QAC)** as an optional, separately licensed annotation provider. Do not modify or redistribute its annotation until its terms and the relationship between its download notice, GPL wording, and FAQ restrictions have been reviewed.
4. Treat **Quran Foundation** as an optional API integration for end-user applications, not as a source for a redistributable QuranKit dataset unless a separate written license permits it.
5. Use **OpenITI** in a later historical-text research extension. Do not assume that every text in the corpus has uniform provenance, fidelity, or reuse rights.
6. Do not bundle classical dictionary content, translations, tafsir, audio, or hadith collections until rights are verified at the individual resource/edition level.

### Dataset strategy

| Layer | Initial strategy | Bundled by default? |
|---|---|---:|
| Quranic text | Tanzil candidate; preserve source file exactly | Only after release-specific validation |
| Structural metadata | Tanzil metadata candidate | Only after terms and attribution are recorded |
| Tokenization/indexes | Generate from permitted source text using QuranKit code | Yes, if output does not unlawfully reproduce restricted source material |
| Morphology/syntax | Native schema plus optional QAC adapter | No QAC data by default |
| Lexicons | Provider adapters and user-supplied licensed packs | No |
| Tafsir/translations | Edition-specific provider packs | No |
| Historical corpus | OpenITI adapter / external corpus reference | No |
| API content | Live provider integration | No raw API data redistribution |

## 3. Evaluation criteria

Each candidate should be assessed against the following criteria before adoption:

1. **Coverage** — full Qur'an, selected surahs, selected books, or partial annotation.
2. **Edition identity** — exact text edition, script, orthography, publisher, release number, and date.
3. **Accuracy and review** — editorial process, scholarly review, known limitations, correction process.
4. **Annotation scope** — morphology, syntax, roots, lemmas, senses, semantic relations, or metadata.
5. **License and terms** — copying, modification, redistribution, commercial use, API use, caching, and derived data.
6. **Attribution** — exact credit text, source links, citation format, and notice retention.
7. **Provenance** — source chain for each record, not just the website from which it was downloaded.
8. **Technical suitability** — machine-readable formats, stable identifiers, encoding, schema, and update mechanism.
9. **Offline suitability** — whether local copies are permitted and how they must be refreshed.
10. **Research reproducibility** — whether a result can cite an exact source release and transformation.

A source being publicly viewable or downloadable does **not** automatically mean that it is open-licensed or may be redistributed.

## 4. Candidate source assessments

### 4.1 Tanzil Quran Text

**Role:** Candidate baseline Arabic text source.

Official pages:

- Text license: https://tanzil.net/docs/Text_License
- Download: https://tanzil.net/download/
- Metadata: https://tanzil.net/docs/Quran_Metadata
- Metadata updates: https://tanzil.net/docs/metadata_updates

**What it provides**

Tanzil distributes machine-readable Qur'anic text in multiple forms and formats. Its download page identifies version 1.1, published in February 2021. The metadata resource describes surah information and structural divisions including juz, hizb, hizb quarters, manzil, ruku, Medina Mushaf page numbers, and sajdah locations/types. It also includes revelation order and other surah-level fields.

**License and use conditions observed**

The Tanzil text license page states CC BY 3.0 and separately sets out specific terms:

- Verbatim copies may be copied and distributed.
- Changing the text is not allowed.
- Use in websites and applications is permitted with clear source attribution and a link to Tanzil.
- The copyright notice must accompany verbatim copies and be reproduced appropriately in files derived from or containing a substantial portion of the text.
- Users should check updates and link to Tanzil so users can track changes.

The explicit no-change condition is important. QuranKit must not silently normalize, rewrite, strip marks from, or otherwise alter the canonical stored source text and then describe that altered copy as the original Tanzil text.

**Assessment**

- Coverage: full Qur'an.
- Technical suitability: high; machine-readable downloads and separate metadata.
- Structural metadata: useful for navigation and research segmentation.
- Accuracy: Tanzil describes the text as carefully produced, verified, and monitored. QuranKit should still perform independent integrity checks and retain source checksums.
- Offline use: potentially suitable for a bundled source pack, subject to exact terms and preservation.
- Main risk: confusing an analytical/search representation with a permitted modified copy of the source text.

**Recommendation: ADOPT AS A CANDIDATE BASELINE, WITH STRICT SOURCE PRESERVATION.**

Implementation requirements:

1. Store the downloaded original bytes as an immutable source artifact.
2. Record exact release/version, download URL, retrieval timestamp, SHA-256, and attribution notice.
3. Preserve original ayah strings exactly in the source layer.
4. Put normalized search strings in separately generated fields, never overwrite source text.
5. Link visibly to Tanzil in documentation and any user-facing application using the data.
6. Re-check the source's update page and terms before each dataset release.
7. Keep the text and metadata as separately registered assets, each with its own provenance and license record.

### 4.2 Tanzil Quran Metadata

**Role:** Candidate structural metadata provider.

Official pages:

- Metadata description: https://tanzil.net/docs/Quran_Metadata
- Metadata change history: https://tanzil.net/docs/metadata_updates

The metadata page lists:

- Surah number, ayah count, revelation order, start line, ruku count, and names
- Juz
- Hizb and hizb quarters
- Manzil
- Ruku
- Medina Mushaf page
- Sajdah location and type

The metadata change history identifies version 1.0 and a release date of 28 February 2008, with historical updates including revelation order, sajdah, ruku, and hizb-quarter information.

**Assessment**

This is highly useful for QuranKit's structural model. However, metadata should not be treated as timeless or universally edition-independent. Page numbers, for example, are tied to a particular Mushaf layout. Revelation order and other historical metadata may have scholarly conventions or disagreements.

**Recommendation: ADOPT AS A VERSIONED METADATA PROVIDER, NOT AS UNQUALIFIED UNIVERSAL TRUTH.**

Implementation requirements:

- Store the provider's original field values and identifiers.
- Label page numbers with the Mushaf/layout convention.
- Preserve source/version and retrieval information.
- Do not infer missing metadata.
- Allow multiple providers or scholarly views for fields where disagreement exists.
- Cite Tanzil as the source in generated metadata documentation.

### 4.3 Quranic Arabic Corpus (QAC)

**Role:** Optional morphology, syntax, and linguistic annotation provider.

Official pages:

- Download: https://corpus.quran.com/download/
- FAQ: https://corpus.quran.com/faq.jsp
- License: https://corpus.quran.com/license.jsp

**What it provides**

The download page identifies version 0.4 of the morphological data and describes syntactic and morphological annotation of the Qur'an. It states that the corpus builds on verified Arabic text distributed by Tanzil. The site also provides word-by-word, dictionary, syntactic treebank, ontology, and grammar resources.

**Terms requiring special care**

The download page labels the data GNU General Public License and says:

- Verbatim copies may be copied and distributed.
- Changing the file is not allowed.
- Use in websites or applications requires clear source attribution and a link to the corpus.
- Copyright notices must be retained in verbatim copies and substantial derived works.

The FAQ separately says research data is made available for research purposes, should not be used commercially, and requires citation in research publications. It also notes that annotation is still undergoing correction.

These statements should not be collapsed into a simplistic claim that all QAC material is freely modifiable for all commercial purposes. The exact version, asset, license text, and any additional conditions need review. If commercial use is planned, obtain written clarification from the maintainers or legal review before integrating the data into a commercial distribution.

**Assessment**

- Linguistic value: high.
- Annotation scope: useful for morphology and syntax.
- Maturity: valuable but the FAQ explicitly notes ongoing correction.
- Technical suitability: promising, subject to schema mapping and stable token alignment.
- Redistribution/modification: constrained and requires legal review.
- Research quality: must preserve annotation as a sourced scholarly/computational layer, not an unquestionable ground truth.

**Recommendation: SUPPORT THROUGH AN OPTIONAL ADAPTER; DO NOT MAKE IT A REQUIRED OR DEFAULT REDISTRIBUTED DATASET.**

Implementation requirements:

1. Preserve original downloaded files unchanged if local storage is permitted.
2. Record version, checksum, citation, exact license text, and retrieval date.
3. Map QAC records to QuranKit identifiers without rewriting the source annotation.
4. Keep QuranKit's internal schema separate from the provider's schema.
5. Do not publish modified QAC files as though they were official QAC data.
6. Record annotation uncertainty and source corrections.
7. Obtain written clarification before commercial distribution or transformation.

### 4.4 Quran Foundation APIs

**Role:** Optional live API integration for applications.

Official pages:

- Developer terms: https://api-docs.quran.com/legal/developer-terms/
- FAQ: https://api-docs.quran.foundation/docs/tutorials/faq/

**What it provides**

Quran Foundation's APIs cover Quran text, translations, metadata, audio, reflections, and other content. This can be useful for application developers who need provider-managed access and content synchronization.

**Terms observed**

The developer terms, last updated 11 October 2026 on the page reviewed, distinguish between displaying content to end users and redistributing raw content as data.

The terms permit qualifying applications to charge for subscriptions, in-app purchases, advertising, donations, or freemium access, provided the content is displayed within the application experience and the other terms are followed.

They restrict selling, sublicensing, or redistributing QF content/raw API data. A separate signed commercial license is required before distributing it as a dataset, feed, API, download, or content package. The terms also specify caching limits and require Content Sync APIs as the permitted path for maintaining certain offline copies.

**Assessment**

- Application integration: useful.
- Dataset mirroring: not an assumed permitted use.
- Offline behavior: must follow the exact Content Sync rules.
- Redistribution: requires separate permission where specified.
- Long-term reproducibility: API content can change; store provider identifiers and retrieval metadata where permitted.

**Recommendation: OPTIONAL API CONNECTOR ONLY. DO NOT USE AS THE DEFAULT SOURCE FOR A REDISTRIBUTABLE DATA PACK.**

Implementation requirements:

- Make API use opt-in and provider-specific.
- Follow rate limits, caching limits, privacy requirements, and Content Sync rules.
- Never scrape or bulk-extract outside authorized API responses.
- Do not expose raw QF data through QuranKit's own dataset downloads or API unless separately licensed.
- Clearly label provider content in results.
- Keep API credentials outside source control.
- Do not assume all QF content assets share identical rights.

### 4.5 OpenITI Corpus

**Role:** Later historical Arabic and Islamicate text research extension.

Official pages:

- Corpus overview: https://openiti.org/projects/OpenITI%20Corpus.html
- Terms of use: https://openiti.org/docs/Terms%20of%20Use.html
- Documentation: https://openiti.org/documentation/
- Releases: https://github.com/OpenITI/RELEASE

**What it provides**

OpenITI is a machine-actionable collection of Arabic and Persian Islamicate texts. It can support historical language research, text reuse, source comparison, author/book metadata, and broader context around scholarly works.

**License and quality considerations**

OpenITI documentation describes corpus releases under CC BY-NC-SA 4.0. The currently surfaced terms page also describes non-commercial Creative Material under CC BY-SA wording and distinguishes third-party material. These pages and the applicable release/contributor terms must be reconciled for the exact item being used. Do not assume one license covers every text, scan, image, edition, or third-party component in the ecosystem.

OpenITI itself notes that its texts come from different sources and have varying fidelity to print editions, including manual transcription and OCR errors. Its documentation recommends citing individual file URIs and the relevant release.

**Assessment**

- Research value: high for historical context and text reuse.
- Direct Quran text authority: not appropriate as the canonical Qur'an source.
- Quality: heterogeneous; each text requires source-level evaluation.
- License: non-commercial and share-alike constraints make it unsuitable for an assumed unrestricted commercial dataset.
- Technical suitability: strong potential for a later adapter.

**Recommendation: LATER OPTIONAL HISTORICAL-CORPUS CONNECTOR; NOT PART OF THE CORE MVP.**

Implementation requirements:

- Identify the exact OpenITI release and file URI.
- Retain edition and source metadata.
- Check the applicable license for each asset and any third-party content.
- Preserve OCR/transcription quality warnings.
- Do not imply that corpus inclusion means scholarly verification.
- Keep this data outside the core Quran text package.

### 4.6 Classical Arabic dictionaries and lexical resources

**Role:** Root, lemma, lexical sense, definition, and historical usage research.

A relevant candidate identified in the initial survey is the Linguistic Data Consortium's **Classical Arabic Dictionary (LDC2021L01)**:

- Catalog: https://catalog.ldc.upenn.edu/LDC2021L01

The catalog describes a large collection of Arabic material from texts dating between 431 and 1104 CE, including word occurrences, source documents, and metadata. It is distributed under an LDC User Agreement, with access and fees depending on membership.

**Assessment**

This resource may be valuable for historical lexical research, but it is not a freely redistributable dictionary pack. Access is governed by the LDC agreement. It also represents a corpus-derived resource rather than a simple replacement for individual classical lexicons.

For named classical works (for example, Lisān al-ʿArab, Maqāyīs al-Lughah, al-Mufradāt, or al-Ṣiḥāḥ), QuranKit must distinguish:

- The public-domain status of an old authored work, where applicable
- Copyright in a modern edited edition, introduction, notes, and critical apparatus
- Copyright and terms of a digital transcription or database
- The source and reliability of any extracted lexical records

**Recommendation: BUILD A PROVIDER-NEUTRAL LEXICON SCHEMA FIRST. ADD ONLY RESOURCE PACKS WITH VERIFIED ITEM-LEVEL RIGHTS.**

Do not scrape online dictionary websites or copy modern editions merely because the underlying classical author died centuries ago.

### 4.7 Translations and tafsir

**Role:** Contextual interpretation, comparative translation, and scholarly commentary.

No general blanket license should be assumed for translations or tafsir. A translation is an authored work; a modern edition of a classical tafsir may include editorial material, notes, and other protected contributions. A provider's API permission may also differ from permission to redistribute a local data package.

**Recommendation: KEEP THESE AS SEPARATE EDITION-SPECIFIC PLUGINS.**

For every translation or tafsir edition, record:

- Original title and language
- Author/translator and editor
- Publisher and edition
- Publication date
- Source URL or catalog identifier
- Exact license or written permission
- Allowed use: display, research, commercial, offline, modification, redistribution
- Required attribution
- Whether excerpts or derived indexes are permitted

Do not merge translation or tafsir text into the canonical Arabic text record.

### 4.8 Hadith collections and scholarly works

**Role:** Later research linking ayahs to narrations, explanations, and scholarly discussions.

A hadith work may be old while a modern edition, translation, numbering system, grading, commentary, or database is not. Numbering can differ by edition and publisher. Online accessibility does not establish permission to download, transform, or redistribute.

**Recommendation: DEFER DATA INGESTION. DESIGN THE SOURCE AND CITATION MODEL NOW.**

Each record should identify the collection, book/chapter, hadith number as used by a named edition, edition/publisher, narrator chain where available, grading source, and exact citation locator. Do not combine variant numbering systems into one supposedly universal ID.

## 5. Source comparison matrix

| Source | Primary value | Coverage | Rights posture observed | MVP decision |
|---|---|---|---|---|
| Tanzil text | Arabic Qur'an text | Full Qur'an | Verbatim distribution; no text changes; attribution/link | Candidate baseline |
| Tanzil metadata | Surah and structural metadata | Full Qur'an structure | Source attribution; verify metadata-specific terms | Candidate baseline |
| QAC | Morphology and syntax | Qur'an annotation | GPL wording plus FAQ non-commercial research limitation; no changes stated | Optional adapter; legal review |
| Quran Foundation | API content and sync | Broad API content | Display permitted under conditions; raw redistribution requires separate license | Optional API connector |
| OpenITI | Historical Arabic/Persian corpus | Large, heterogeneous corpus | Non-commercial/share-alike terms; check item-level third-party rights | Later extension |
| LDC Classical Arabic Dictionary | Historical Arabic corpus/lexical data | Large historical corpus | LDC agreement and access terms | Optional licensed provider |
| Translation/tafsir editions | Interpretation and translation | Edition-specific | Must verify per edition | Later plugins |
| Hadith datasets | Narrations and references | Collection-specific | Must verify per edition/database | Later plugins |

## 6. QuranKit data governance requirements

Every source asset must have a manifest. Suggested fields:

```yaml
dataset_id: tanzil.quran_text.uthmani
provider: Tanzil Project
asset_name: Quran Text - Uthmani
version: "1.1"
release_date: "2021-02"
retrieved_at: "YYYY-MM-DD"
source_url: "https://tanzil.net/download/"
license_name: "CC BY 3.0 (with source-specific terms)"
license_url: "https://tanzil.net/docs/Text_License"
redistribution: "verbatim_only"
modification: false
commercial_use: "verify_scope_and_terms"
attribution_required: true
attribution_text: "Tanzil Quran Text — Tanzil Project — https://tanzil.net"
source_checksum_sha256: "<computed-at-ingestion>"
format: "provider-original-format"
language: "ar"
script: "uthmani"
notes:
  - "Keep original source bytes unchanged."
  - "Generated search forms are separate derived fields."
```

The example is illustrative. The ingestion pipeline must fill in actual retrieval dates, checksums, format, and exact attribution text from the downloaded source. Never ship placeholder values in a released manifest.

### Required provenance fields

At minimum, each dataset and record should be traceable to:

- `provider_id`
- `dataset_id`
- `dataset_version`
- `source_record_id`
- `source_uri`
- `license_id`
- `retrieved_at`
- `source_checksum`
- `ingestion_pipeline_version`
- `transformation_id`
- `review_status`

For scholarly annotations, add:

- annotator/author
- editor/reviewer
- edition
- method
- confidence or uncertainty, if supplied
- correction history
- disagreement/variant information

### Separation of layers

QuranKit should keep the following distinct:

1. **Source artifact** — the exact downloaded file, preserved when permitted.
2. **Canonical source record** — structured representation linked to the source artifact.
3. **Derived index** — search normalization, token lookup, FTS index, embeddings, and other generated structures.
4. **Scholarly annotation** — sourced morphology, syntax, lexical, semantic, or interpretive statements.
5. **Research result** — output of a reproducible algorithm with its inputs and method.
6. **User annotation** — a user's own notes, hypotheses, and corrections.

A derived index must never be presented as if it were the original source text or the source provider's official annotation.

## 7. Dataset ingestion and release workflow

Recommended lifecycle:

1. **Discover** — identify the provider and exact asset.
2. **Review rights** — record license, terms, attribution, redistribution, modification, commercial use, and caching conditions.
3. **Acquire** — use the official download or authorized API.
4. **Freeze source** — preserve original bytes if permitted; compute SHA-256.
5. **Validate** — check encoding, record counts, identifiers, expected coverage, and schema.
6. **Map** — map provider identifiers into QuranKit identifiers without discarding provider IDs.
7. **Transform** — produce derived indexes in a separate, versioned pipeline.
8. **Review** — run integrity tests and, for scholarly annotation, expert review where possible.
9. **Package** — include manifests, notices, citations, and checksums.
10. **Publish** — publish code and data as separate artifacts with separate licenses.
11. **Monitor** — track source updates, corrections, and license changes.

If a source prohibits modification, do not modify the source artifact. If a source prohibits redistribution, do not put its data into a downloadable package. If terms are ambiguous, pause publication and seek clarification.

## 8. Validation and quality checks

### Text integrity

- Verify surah count and expected ayah counts against the chosen edition.
- Verify stable surah/ayah identifiers.
- Compare the imported source against the original source artifact.
- Ensure Unicode normalization never overwrites the source string.
- Keep Uthmani and Imlai editions distinct.
- Detect missing, duplicated, reordered, or unexpectedly altered ayahs.
- Record all validation results in a machine-readable report.

### Metadata integrity

- Validate all surah references.
- Validate Juz/hizb/ruku/page ranges.
- Label page numbering by Mushaf convention.
- Preserve provider values and do not fill gaps by guessing.
- Allow multiple sourced values when scholarly conventions differ.

### Linguistic annotation integrity

- Validate token alignment against the exact text edition used by the annotation.
- Do not assume one provider's tokenization matches another's.
- Keep morphological segmentation separate from orthographic word tokens.
- Preserve provider labels and original annotation IDs.
- Track annotation corrections and unresolved ambiguity.
- Do not infer roots or lemmas from string similarity alone.

### Licensing integrity

- Ensure each packaged asset has a manifest and notice.
- Fail release checks if an asset has unknown rights status.
- Prevent restricted assets from entering public data packages.
- Verify all required attribution links and license copies.
- Keep third-party assets separate from QuranKit's own code license.

## 9. Proposed package layout

```text
qurankit/
├── src/
│   └── qurankit/
│       ├── datasets/
│       │   ├── manifest.py
│       │   ├── registry.py
│       │   ├── provenance.py
│       │   └── validation.py
│       ├── providers/
│       │   ├── tanzil/
│       │   ├── qac/
│       │   ├── quran_foundation/
│       │   ├── openiti/
│       │   └── lexicons/
│       └── ...
├── data/
│   └── manifests/
│       ├── tanzil-quran-text.yaml
│       └── tanzil-quran-metadata.yaml
├── licenses/
│   └── third_party/
├── docs/
│   ├── data-model.md
│   ├── arabic-text-standard.md
│   └── datasets.md
└── tests/
    └── datasets/
```

The actual third-party data files should be stored separately from source code wherever licensing, repository size, or release cadence makes that preferable.

## 10. Prioritized implementation plan

### Phase A — source governance (first)

- Implement `DatasetManifest`.
- Implement a dataset registry.
- Implement SHA-256 and source artifact metadata.
- Implement license/rights status values: `approved`, `restricted`, `permission_required`, `unknown`, `rejected`.
- Make release packaging fail for `unknown` or `permission_required` assets.

### Phase B — text and metadata baseline

- Evaluate and ingest Tanzil text under its exact terms.
- Evaluate and ingest Tanzil metadata.
- Preserve original source artifacts.
- Generate independent QuranKit indexes and structural records.
- Add ayah count, ordering, and checksum tests.

### Phase C — linguistic adapters

- Define provider-neutral morphology and syntax schemas.
- Prototype QAC mapping in a local, non-redistributed development environment if permitted.
- Resolve the QAC license/FAQ ambiguity before publishing any integrated data.
- Add adapter conformance tests.

### Phase D — research extensions

- Add lexicon provider interfaces.
- Add edition-specific translation and tafsir providers.
- Add OpenITI historical-text adapter.
- Add hadith and scholarly-reference models.
- Review every source independently.

## 11. Open questions before the first public data release

1. Which exact Tanzil text form should be the default: Uthmani, simple, or another offered form?
2. Will QuranKit distribute a Tanzil-derived data pack, or require users to download it directly?
3. Does the intended distribution include commercial use?
4. Can QAC maintainers clarify in writing the scope of the GPL statement, no-change clause, and non-commercial FAQ?
5. Which lexicon edition(s) can be legally redistributed in structured form?
6. Which translation/tafsir editions have explicit licenses?
7. Which Mushaf convention should be used for page metadata?
8. How should QuranKit represent disagreements in revelation-order, Makki/Madani, and other scholarly metadata?

## 12. Source references

Primary sources reviewed for this initial assessment:

- Tanzil Text License — https://tanzil.net/docs/Text_License
- Tanzil Download — https://tanzil.net/download/
- Tanzil Quran Metadata — https://tanzil.net/docs/Quran_Metadata
- Tanzil Metadata Updates — https://tanzil.net/docs/metadata_updates
- Quranic Arabic Corpus Download — https://corpus.quran.com/download/
- Quranic Arabic Corpus FAQ — https://corpus.quran.com/faq.jsp
- Quranic Arabic Corpus License — https://corpus.quran.com/license.jsp
- Quran Foundation Developer Terms — https://api-docs.quran.com/legal/developer-terms/
- Quran Foundation FAQ — https://api-docs.quran.foundation/docs/tutorials/faq/
- OpenITI Corpus — https://openiti.org/projects/OpenITI%20Corpus.html
- OpenITI Terms of Use — https://openiti.org/docs/Terms%20of%20Use.html
- OpenITI Documentation — https://openiti.org/documentation/
- OpenITI Releases — https://github.com/OpenITI/RELEASE
- LDC Classical Arabic Dictionary — https://catalog.ldc.upenn.edu/LDC2021L01

## 13. Final position

QuranKit should not aim to own or repackage every available Islamic text resource. It should provide a trustworthy framework for connecting, validating, indexing, comparing, and citing sources under their actual terms.

The strongest initial architecture is:

- a carefully sourced Qur'anic text layer;
- a versioned structural metadata layer;
- a provider-neutral linguistic annotation layer;
- a provenance and licensing registry;
- deterministic Python research tools;
- optional adapters for external scholarly resources.

This approach keeps QuranKit useful to researchers and AI agents without confusing computational convenience with textual authority, scholarly consensus, or permission to redistribute data.
