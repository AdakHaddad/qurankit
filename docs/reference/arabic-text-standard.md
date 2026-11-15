# QuranKit --- Arabic Text Standard

**Document status:** Initial technical standard\
**Version:** 0.1.0\
**Scope:** Arabic text ingestion, preservation, normalization,
tokenization, matching, and display

This document defines how QuranKit handles Arabic text, especially
Qur'anic text. It is intended to prevent accidental loss of orthographic
information and to ensure that search, comparison, and linguistic
analysis remain reproducible.

This is a technical data-handling standard. It does not determine which
Qur'anic orthography, reading, or scholarly position is religiously
authoritative. Those choices must be tied to identified sources and
documented editions.

## 1. Goals

QuranKit must:

1.  Preserve source text exactly as imported.
2.  Support more than one orthographic representation, including Uthmani
    and Imlai where reliable data is available.
3.  Make every normalization operation explicit and versioned.
4.  Keep exact-text comparison separate from search-oriented matching.
5.  Avoid confusing orthographic similarity with lexical, morphological,
    or semantic identity.
6.  Preserve the ability to trace a match back to its original source
    characters.
7.  Handle Arabic Unicode and combining marks correctly.
8.  Support word-level research without assuming that whitespace always
    defines a linguistic word.
9.  Make transformations reproducible across machines and software
    versions.

## 2. Non-negotiable rules

-   Never overwrite source Arabic text with normalized text.
-   Never silently remove diacritics, Quranic marks, hamza distinctions,
    or pause signs from the stored original.
-   Never describe a normalized match as an exact source-text match.
-   Never convert Uthmani text to Imlai text without identifying the
    conversion rules and version.
-   Never infer a root, lemma, reading, or grammatical analysis from
    normalization alone.
-   Never merge different qira'at or text editions into one
    undifferentiated text field.
-   Never assume that visually similar Unicode strings are
    byte-identical or code-point-identical.
-   Every derived text representation must identify its source record
    and transformation profile.

## 3. Text layers

Keep the following layers conceptually and physically separate.

  -----------------------------------------------------------------------
  Layer                   Purpose                 Example use
  ----------------------- ----------------------- -----------------------
  Source text             Exact imported          Archival fidelity and
                          representation          citation

  Display text            Optional presentation   User interface
                          adjustments             rendering

  Search-normalized text  Search-oriented         Diacritic-insensitive
                          equivalence             lookup

  Linguistic              Token, lemma,           Grammar and lexical
  representation          morphology, or          research
                          segmentation data       

  Transliteration         Romanized               Optional display or
                          representation          accessibility

  Translation             Translation in a named  Meaning exploration
                          language and edition    
  -----------------------------------------------------------------------

A display transformation must not become the archival source. A
search-normalized string must not be used as a substitute for a
linguistic analysis. A translation must never replace the Arabic source
text.

## 4. Unicode handling

### 4.1 Encoding

-   Store text as Unicode.
-   Use UTF-8 for text files and interchange formats unless a documented
    format requires otherwise.
-   Validate decoding during ingestion.
-   Reject or quarantine malformed input rather than silently replacing
    invalid bytes.
-   Record the source encoding and any decoding conversion where known.

### 4.2 Unicode normalization

Unicode normalization forms can change code-point sequences while
preserving canonical or compatibility equivalence. QuranKit should not
apply compatibility normalization indiscriminately to source text.

Recommended policy:

-   Preserve the exact decoded source string in `text_original`.
-   A derived processing representation may use NFC when justified and
    documented.
-   Do not apply NFKC or NFKD to Qur'anic source text by default.
-   Record the normalization form in the transformation profile.
-   Test behavior with combining marks and Arabic presentation forms.

Unicode normalization is not the same as Arabic orthographic
normalization. NFC does not decide whether two Arabic spellings should
be treated as equivalent for a particular research task.

### 4.3 Offsets

Character offsets must have a documented convention.

Recommended default:

-   Store offsets as zero-based Unicode code-point offsets into the
    exact `text_original` string.
-   Use an exclusive end offset: `[start, end)`.
-   Do not mix byte offsets, UTF-16 code-unit offsets, grapheme-cluster
    offsets, and code-point offsets.
-   If an external corpus uses a different offset convention, preserve
    its original offsets separately and provide a verified mapping.

Because Arabic letters may contain combining marks, a visible grapheme
can contain multiple code points. User-interface cursor positions may
therefore require grapheme-aware handling even when database offsets use
code points.

## 5. Arabic character and mark categories

Do not implement normalization as an undocumented list of global string
replacements. Define and test categories.

### 5.1 Base letters

Preserve base Arabic letters in source text. Search profiles may
optionally equate selected forms, but each equivalence must be named and
documented.

### 5.2 Hamza and alif forms

Potentially relevant forms include:

-   ا
-   أ
-   إ
-   آ
-   ٱ
-   ء
-   ؤ
-   ئ

These forms are not universally interchangeable. A search profile may
offer a broad hamza-insensitive mode for discovery, but exact and
linguistically careful modes must retain distinctions.

Do not remove hamza distinctions from the original. Do not assume that
hamza normalization is appropriate for morphology, qira'at, or
orthographic research.

### 5.3 Alif maqsurah and ya

The forms ى and ي may be treated as equivalent by a configurable
broad-search profile in selected use cases. They must remain distinct in
source text and in exact orthographic comparison.

### 5.4 Ta marbutah and ha

The forms ة and ه must not be globally equated. A broad user-facing
search may optionally support a candidate expansion, but results must
disclose that the match used a relaxed equivalence.

### 5.5 Diacritics and recitation marks

Arabic text can include marks for:

-   Short vowels.
-   Tanwin.
-   Shaddah.
-   Sukun.
-   Madd and other recitation-related signs.
-   Superscript or small letters.
-   Quranic annotation and pause signs.

Do not assume every combining mark is optional decoration. Some marks
encode pronunciation, reading, or textual conventions.

A profile that removes selected vowel marks must identify exactly which
Unicode characters it removes. It must not remove all combining marks
indiscriminately.

### 5.6 Quranic annotation and pause signs

Pause signs, sajdah markers, rub' markers, and other Quranic annotations
may be encoded as characters, combining marks, or separate metadata
depending on the source.

Recommended policy:

-   Preserve them in the source layer.
-   Identify their role where the source specification permits.
-   Expose separate search options for including or excluding annotation
    marks.
-   Do not remove them from the source string during import.
-   Where marks are stored as structured metadata instead of inline
    characters, retain the original source representation or a
    documented reversible mapping.

## 6. Normalization profiles

Normalization must be selected by name and version. A profile is a
documented transformation contract, not an informal label.

The following profiles are proposed starting points. Their exact
character mappings must be specified and tested before implementation.

### 6.1 `exact-source-v1`

Purpose: exact comparison with the selected source representation.

Rules:

-   No Arabic letter substitutions.
-   No diacritic removal.
-   No Quranic mark removal.
-   No whitespace collapsing unless the comparison mode explicitly
    excludes surrounding transport whitespace.
-   Preserve the exact source string.

Use for source fidelity and exact edition-specific comparison.

### 6.2 `canonical-unicode-v1`

Purpose: a limited Unicode canonical normalization for processing.

Rules:

-   Apply NFC to a derived copy only.
-   Do not apply Arabic letter equivalences.
-   Do not remove diacritics or Quranic marks.
-   Preserve the original source string independently.

Use only when canonical Unicode equivalence is needed.

### 6.3 `diacritics-insensitive-v1`

Purpose: discover text matches regardless of a defined set of
vocalization marks.

Rules:

-   Start from a derived copy.
-   Remove only an explicit allowlist of marks designated by the
    profile.
-   Retain base letters and hamza distinctions.
-   Retain Quranic annotation marks unless the profile explicitly
    defines their handling.
-   Return the original source text and indicate that
    diacritic-insensitive matching was used.

Do not call this profile "unvocalized exact text"; it is a relaxed
match.

### 6.4 `search-broad-v1`

Purpose: broad discovery for user-entered Arabic queries.

May include configurable options for:

-   Selected alif/hamza equivalences.
-   Selected alif maqsurah/ya equivalence.
-   Removal of a specified set of vowel marks.
-   Optional handling of tatweel.
-   Optional whitespace and punctuation normalization.

Rules:

-   Every enabled transformation must be visible in the profile
    configuration.
-   Return match type and applied transformations.
-   Do not use this profile for claims about exact spelling, qira'at, or
    morphology.
-   Do not make ta marbutah/ha equivalence a default.

### 6.5 Custom profiles

Allow users to define custom profiles, but require:

-   A unique profile identifier.
-   A version.
-   Explicit rules.
-   A deterministic implementation.
-   Tests and documentation.
-   A clear statement of intended use.

A profile change that alters results must receive a new version.

## 7. Suggested normalization pipeline

A search pipeline should be ordered and inspectable.

``` text
Input query
   |
   v
Validate Unicode
   |
   v
Select explicit profile
   |
   v
Apply configured Unicode normalization
   |
   v
Apply configured Arabic mark handling
   |
   v
Apply configured letter equivalences
   |
   v
Apply whitespace/punctuation policy
   |
   v
Search matching index
   |
   v
Return original source text + match metadata
```

The pipeline should not apply a linguistic root or lemma transformation
unless the user explicitly selects a morphological search operation and
a suitable annotation dataset is available.

## 8. Uthmani and Imlai representations

Uthmani and Imlai representations should be modeled as distinct text
representations or editions, not as a single field with an implicit
conversion.

For every supported representation, record:

-   Dataset and version.
-   Source and edition details.
-   Script/orthography description.
-   Reading information where relevant.
-   Text coverage and known limitations.
-   Tokenization convention.
-   License and redistribution status.

A conversion between representations must record:

-   Input edition.
-   Output representation.
-   Conversion rules and version.
-   Characters or signs omitted, substituted, or expanded.
-   Whether the mapping is reversible.
-   Known ambiguities.

Do not claim that a conversion is fully reversible unless tested and
demonstrated. Prefer loading a separately sourced representation when
one is available and appropriately licensed.

## 9. Tokenization and word segmentation

### 9.1 Do not equate whitespace tokens with linguistic words

Whitespace splitting may be useful as an initial text segmentation
method, but Arabic orthography and morphology can involve attached
clitics, particles, and other segmentation choices.

QuranKit should distinguish:

-   Text span: a sequence of source characters.
-   Orthographic token: a unit under a specified tokenization
    convention.
-   Morphological segment: a clitic or morpheme-level component.
-   Linguistic word: a unit defined by a linguistic annotation scheme.

### 9.2 Tokenization metadata

Every tokenization scheme must document:

-   Source corpus or algorithm.
-   Version.
-   Treatment of attached conjunctions, prepositions, articles, and
    pronouns.
-   Treatment of punctuation and Quranic marks.
-   Whether token boundaries are source-provided or computed.
-   Offset convention.
-   Known limitations.

### 9.3 Stable token identity

A token identifier must include or reference:

-   Text edition.
-   Surah and ayah.
-   Tokenization scheme and version.
-   Token position or source identifier.

Do not reuse token IDs across different tokenization schemes merely
because the visible surface strings happen to match.

### 9.4 Segmentation alignment

When a source provides morphological segments, store the alignment from
segments to the parent orthographic token and source character span.
Preserve the source's segmentation labels and provide a mapping layer if
QuranKit uses a normalized tagset.

## 10. Search modes and result labeling

Every search operation should expose its matching mode.

  -------------------------------------------------------------------------------
  Mode                    What it matches         Result label
  ----------------------- ----------------------- -------------------------------
  Exact source            Same source             `exact_source_match`
                          representation          

  Canonical Unicode       Canonically normalized  `unicode_normalized_match`
                          representation          

  Diacritic-insensitive   Match after specified   `diacritic_insensitive_match`
                          mark removal            

  Broad orthographic      Match under configured  `broad_orthographic_match`
                          letter equivalences     

  Token sequence          Ordered token sequence  `token_sequence_match`

  Lemma                   Sourced lemma           `lemma_match`
                          annotation              

  Root                    Sourced root annotation `root_match`

  Fuzzy                   Approximate string      `fuzzy_candidate`
                          similarity              

  Semantic                Model or vector         `semantic_candidate`
                          similarity              
  -------------------------------------------------------------------------------

Do not combine these into one undifferentiated search score.

A result should include:

-   Original source reference.
-   Original matched text.
-   Query as supplied.
-   Normalized query.
-   Normalization profile and version.
-   Match mode.
-   Dataset and edition.
-   Character/token alignment where available.
-   Any ambiguity or limitation.

## 11. Display and rendering

-   Use a font with adequate Arabic and Quranic glyph coverage.
-   Preserve logical Unicode text order in storage.
-   Use a rendering environment that supports right-to-left layout and
    bidirectional text.
-   Do not manually reverse Arabic strings for display.
-   Test mixed Arabic, Latin, numbers, punctuation, and verse
    references.
-   Ensure copy/export operations return the intended source
    representation.
-   Do not silently replace source text with a font-specific or
    presentation-form encoding.

Display should be tested in the actual target interfaces, because
browser, terminal, PDF, and notebook rendering may differ.

## 12. Transliteration

Transliteration is a derived representation.

If supported:

-   Identify the transliteration standard or scheme.
-   Version the implementation.
-   Preserve source-to-output alignment where practical.
-   Do not present transliteration as a replacement for Arabic.
-   Distinguish scholarly transliteration from simplified pronunciation
    aids.
-   Do not infer a single pronunciation where qira'at or reading
    information is not specified.

## 13. Import and validation requirements

Every text importer must:

1.  Record source, dataset version, edition, and license metadata.
2.  Preserve exact decoded source strings.
3.  Validate Unicode.
4.  Verify surah and ayah references.
5.  Detect duplicate and missing records.
6.  Preserve source identifiers.
7.  Record tokenization source and version.
8.  Validate character offsets against the source string.
9.  Avoid implicit normalization during import.
10. Produce a report of errors, warnings, and coverage.

Do not silently "repair" malformed Arabic. Any repair process must
create a separate derived value and retain the original.

## 14. Test strategy

Build tests around reviewed examples and source fixtures.

### Unicode tests

-   NFC and NFD behavior.
-   Combining mark sequences.
-   Arabic presentation forms.
-   Invalid input handling.
-   Code-point offsets and grapheme behavior.

### Orthographic tests

-   Hamza and alif forms.
-   Alif maqsurah and ya.
-   Ta marbutah and ha.
-   Tatweel.
-   Diacritics.
-   Quranic annotation and pause marks.

### Search tests

-   Exact source matching.
-   Diacritic-insensitive matching.
-   Broad search equivalences.
-   No accidental equivalence in exact mode.
-   Result metadata and source offsets.

### Tokenization tests

-   Token boundaries.
-   Clitic segmentation.
-   Multiple tokenization versions.
-   Source alignment.
-   Empty or malformed tokens.

### Regression tests

Every discovered normalization or segmentation bug should receive a
minimal fixture and a regression test. Fixtures must be traceable to
their source and must not be fabricated Qur'anic text.

## 15. Proposed API shape

The following is illustrative and does not define final signatures:

``` python
from qurankit import QuranKit

quran = QuranKit()

# Exact source search
results = quran.search(
    "query",
    mode="exact",
    edition="selected-edition",
)

# Search with a named normalization profile
results = quran.search(
    "query",
    mode="orthographic",
    normalization="diacritics-insensitive-v1",
)

# Retrieve the unchanged source text
ayah = quran.ayah("2:255", edition="selected-edition")
original = ayah.text_original
```

The API should make it difficult to accidentally use broad normalization
when exact comparison is intended.

## 16. Open decisions

Before implementation, resolve and document:

1.  Which source text edition is the initial reference edition?
2.  Which Uthmani and Imlai sources are available and redistributable?
3.  Which Unicode characters are classified as vocalization marks versus
    Quranic annotation marks in each source?
4.  Which normalization profiles are required for the first alpha?
5.  Which tokenization corpus or convention is used initially?
6.  What offset convention does each imported corpus use?
7.  How are qira'at and orthographic variants represented in a later
    extension?
8.  Which fonts and rendering environments are included in visual
    regression testing?

Do not invent mappings to close these gaps. Keep uncertain
transformations opt-in until verified against source specifications and
reviewed examples.

## 17. Recommended implementation order

1.  Implement source-preserving text ingestion.
2.  Add Unicode validation and source checksums.
3.  Add `exact-source-v1` search.
4.  Add one explicitly specified diacritic-insensitive profile.
5.  Add a reviewed tokenization adapter.
6.  Add Uthmani/Imlai source adapters when source data and licensing are
    verified.
7.  Add broad orthographic search as an opt-in profile.
8.  Add morphological search only after reliable annotations are
    integrated.
9.  Add rendering tests for supported interfaces.

This order prioritizes textual integrity before convenience features.
