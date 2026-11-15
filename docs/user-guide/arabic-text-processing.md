# Arabic Text Processing

QuranKit implements explicit, documented Arabic text processing following the [Arabic Text Standard](../reference/arabic-text-standard.md).

## Design Principles

1. **Source text is never modified** — Original Arabic text is preserved exactly
2. **Normalized text is separate** — Search/analysis uses derived normalized forms
3. **Normalization is explicit** — Every operation documents its profile
4. **Mappings are preserved** — Offsets between original and normalized text are tracked
5. **Unicode-aware** — All processing uses proper Unicode handling

## Normalization Profiles

QuranKit provides four built-in normalization profiles:

### 1. Exact Source (`exact`)

No normalization. Compares raw source text.

```python
results = quran.search("بِسْمِ اللَّهِ", mode="exact")
```

### 2. Canonical Unicode (`canonical`)

Applies Unicode NFC normalization only.

```python
results = quran.search("بِسْمِ اللَّهِ", mode="canonical")
```

### 3. Diacritic-Insensitive (`diacritic_insensitive`)

Removes harakat (short vowels) but keeps:
- Quranic annotation signs (verse markers, sajdah marks)
- Pause marks (waqf signs)
- Shadda (gemination)

```python
results = quran.search("بسم الله", mode="diacritic_insensitive")
# Matches: بِسْمِ اللَّهِ، بِسْمِ اللَّهِ، بِسْمِ اللّٰهِ
```

### 4. Broad Search (`broad`)

Most permissive. Applies:
- All diacritic-insensitive changes
- Hamza normalization: أ إ آ ا → ا
- Alif maqsurah: ى → ي
- Ta marbutah: ة → ه
- Removes tatweel (kashida): ـ
- Removes Quranic annotation signs
- Removes pause marks

```python
results = quran.search("بسم الله", mode="broad")
# Matches all orthographic variants
```

## Using Normalization Directly

```python
from qurankit.search import NormalizationEngine, NormalizationProfile

engine = NormalizationEngine()

# Get profile by name
profile = engine.get_profile("broad")

# Normalize text
text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
normalized = profile.normalize(text)
print(normalized)  # "بسم الله الرحمن الرحيم"

# Get character mappings
mappings = profile.normalize_with_mappings(text)
for mapping in mappings:
    print(f"Original: {mapping.original_char} -> Normalized: {mapping.normalized_char}")
    print(f"  Position: {mapping.original_pos} -> {mapping.normalized_pos}")
```

## Custom Normalization Profiles

```python
from qurankit.search.normalization import NormalizationProfile, NormalizationRule

# Create custom profile
custom = NormalizationProfile(
    name="custom",
    rules=[
        NormalizationRule.remove_diacritics(keep_shadda=True),
        NormalizationRule.normalize_hamza(),
        NormalizationRule.normalize_ya_maqsurah(),
        NormalizationRule.normalize_ta_marbutah(),
        NormalizationRule.remove_tatweel(),
        NormalizationRule.remove_quranic_marks(),
        NormalizationRule.remove_pause_marks(),
    ]
)

# Register and use
engine.register_profile(custom)
results = quran.search("الرحمن", mode="custom")
```

## Arabic-Specific Handling

### Hamza Variants

| Character | Name | Broad Normalization |
|-----------|------|---------------------|
| ا | Alif | ا |
| أ | Alif with Hamza Above | ا |
| إ | Alif with Hamza Below | ا |
| آ | Alif with Madda | ا |
| ؤ | Waw with Hamza | و |
| ئ | Ya with Hamza | ي |

### Alif Variants

| Character | Name | Broad Normalization |
|-----------|------|---------------------|
| ا | Alif | ا |
| ٱ | Alif Wasla | ا |
| آ | Alif with Madda | ا |

### Alif Maqsurah

| Character | Name | Broad Normalization |
|-----------|------|---------------------|
| ى | Alif Maqsurah | ي |
| ي | Ya | ي |

### Ta Marbutah

| Character | Name | Broad Normalization |
|-----------|------|---------------------|
| ة | Ta Marbutah | ه |
| ه | Ha | ه |

### Quranic Marks (Preserved in Diacritic-Insensitive)

| Character | Name | Diacritic-Insensitive | Broad |
|-----------|------|----------------------|-------|
| ۝ | Verse End | Kept | Removed |
| ۩ | Sajdah | Kept | Removed |
| ۞ | Ruku | Kept | Removed |
| ۝ | Quarter Hizb | Kept | Removed |

### Pause Marks (Waqf)

| Character | Name | Diacritic-Insensitive | Broad |
|-----------|------|----------------------|-------|
| ۖ | Saktah | Kept | Removed |
| ۗ | Waqf | Kept | Removed |
| ۘ | Qif | Kept | Removed |
| ۙ | Waqf Murakhkhas | Kept | Removed |
| ۚ | Waqf Mu'annaq | Kept | Removed |
| ۛ | Waqf Mutalaq | Kept | Removed |

## Search Result Metadata

Every search result includes normalization metadata:

```python
results = quran.search("الرحمن", mode="broad")

for result in results:
    print(f"Reference: {result.reference}")
    print(f"Text: {result.text}")              # Original text
    print(f"Normalized: {result.normalized}")  # Normalized text
    print(f"Mode: {result.mode}")              # Profile used
    print(f"Score: {result.score}")            # Match score
    print(f"Mappings: {result.mappings}")      # Char position mappings
```

## Offset Mapping

Track positions between original and normalized text:

```python
# Get mappings for an ayah
ayah = quran.ayah(1, 1)
mappings = quran.get_normalization_mappings(ayah.reference, "broad")

for mapping in mappings:
    print(f"Orig[{mapping.original_start}:{mapping.original_end}] = "
          f"Norm[{mapping.normalized_start}:{mapping.normalized_end}]")
```

## Best Practices

1. **Always specify normalization mode** — Don't rely on defaults
2. **Use exact search for verification** — Confirm matches with original text
3. **Preserve mappings for highlights** — Use mappings to highlight matches in original text
4. **Document your profile choice** — Record which profile was used in research
5. **Test edge cases** — Verify behavior with hamza, alif maqsurah, ta marbutah

## Next Steps

- [Search & Normalization →](search.md)
- [Arabic Text Standard Reference →](../reference/arabic-text-standard.md)
- [Vocabulary & Lexicon →](vocabulary.md)
