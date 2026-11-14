"""
Lexicon module for QuranKit.

Provides dictionary adapter interface, built-in providers, and
Qur'anic vocabulary integration for root/lemma lookup and
lexical analysis.
"""

from qurankit.lexicon.adapter import (
    AdapterCapabilities,
    DictionaryAdapter,
    DictionaryAdapterRegistry,
    LexicalLookupResult,
    get_lexicon_registry,
    register_adapter,
)
from qurankit.lexicon.providers import (
    FileBasedDictionaryAdapter,
    create_adapter_from_jsonl,
)
from qurankit.lexicon.vocabulary import (
    QuranicOccurrence,
    QuranicVocabulary,
    VocabularyStats,
    create_vocabulary_analyzer,
)

__all__ = [
    # Adapter interface
    "DictionaryAdapter",
    "DictionaryAdapterRegistry",
    "LexicalLookupResult",
    "AdapterCapabilities",
    "get_lexicon_registry",
    "register_adapter",
    # Built-in providers
    "FileBasedDictionaryAdapter",
    "create_adapter_from_jsonl",
    # Vocabulary integration
    "QuranicVocabulary",
    "QuranicOccurrence",
    "VocabularyStats",
    "create_vocabulary_analyzer",
]
