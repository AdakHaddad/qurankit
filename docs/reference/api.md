# API Reference

This page provides the complete API reference for QuranKit.

## Core Classes

### Quran

Main entry point for accessing Qur'anic text and analysis.

::: qurankit.core.Quran
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true
      merge_init_into_class: true

### QuranKitConfig

Configuration for QuranKit behavior.

::: qurankit.core.QuranKitConfig
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Text Models

### Surah

::: qurankit.models.text.Surah
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### Ayah

::: qurankit.models.text.Ayah
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### WordToken

::: qurankit.models.text.WordToken
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### TextEdition

::: qurankit.models.text.TextEdition
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Vocabulary & Lexicon

### QuranicVocabulary

::: qurankit.lexicon.QuranicVocabulary
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### DictionaryAdapter

::: qurankit.lexicon.DictionaryAdapter
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### FileBasedDictionaryAdapter

::: qurankit.lexicon.FileBasedDictionaryAdapter
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### DictionaryAdapterRegistry

::: qurankit.lexicon.DictionaryAdapterRegistry
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Search

### SearchEngine

::: qurankit.search.SearchEngine
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### NormalizationEngine

::: qurankit.search.NormalizationEngine
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### NormalizationProfile

::: qurankit.search.NormalizationProfile
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Mutashabihat

### MutashabihatEngine

::: qurankit.analysis.MutashabihatEngine
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Reports

### ComparisonReport

::: qurankit.analysis.ComparisonReport
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Dataset Management

### DatasetRegistry

::: qurankit.datasets.DatasetRegistry
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### ManifestManager

::: qurankit.datasets.ManifestManager
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### DatasetValidator

::: qurankit.datasets.DatasetValidator
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Provenance Models

### DatasetManifest

::: qurankit.models.provenance.DatasetManifest
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### Dataset

::: qurankit.models.provenance.Dataset
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### Source

::: qurankit.models.provenance.Source
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Providers

### TanzilProvider

::: qurankit.providers.TanzilProvider
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### QACProvider

::: qurankit.providers.qac.QACProvider
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

## Exceptions

### QuranKitError

::: qurankit.core.exceptions.QuranKitError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### DatasetNotFoundError

::: qurankit.core.exceptions.DatasetNotFoundError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### InvalidReferenceError

::: qurankit.core.exceptions.InvalidReferenceError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### UnsupportedEditionError

::: qurankit.core.exceptions.UnsupportedEditionError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### MissingAnnotationError

::: qurankit.core.exceptions.MissingAnnotationError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### ValidationError

::: qurankit.core.exceptions.ValidationError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### ProvenanceError

::: qurankit.core.exceptions.ProvenanceError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### ChecksumMismatchError

::: qurankit.core.exceptions.ChecksumMismatchError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true

### StorageError

::: qurankit.core.exceptions.StorageError
    options:
      show_root_heading: true
      show_root_full_path: false
      members_order: source
      separate_signature: true
      show_if_no_docstring: true
