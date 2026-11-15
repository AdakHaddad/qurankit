"""
Main CLI entry point for QuranKit.

Provides commands for dataset management, search, and textual analysis.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from qurankit import Quran
from qurankit.analysis import (
    CollocationAnalyzer,
    CooccurrenceMeasure,
    CrossReferenceAnalyzer,
    MutashabihatEngine,
    ReportGenerator,
    SemanticRelationExtractor,
    SemanticRelationType,
    WujuhWaNazairAnalyzer,
)
from qurankit.datasets.manifest import ManifestManager
from qurankit.datasets.registry import DatasetRegistry
from qurankit.providers.tanzil import TanzilProvider
from qurankit.search.engine import SearchResult
from qurankit.storage.access import DataAccess, Database

console = Console()

MAX_DISPLAY_LENGTH = 80


@click.group()
@click.version_option(version="0.3.0", prog_name="qurankit")
def main() -> None:
    """QuranKit - Computational Qur'anic research framework."""
    pass


@main.group()
def data() -> None:
    """Dataset management commands."""
    pass


@data.command("list")
@click.option("--installed-only", is_flag=True, help="Show only installed datasets")
def data_list(installed_only: bool) -> None:
    """List available datasets."""
    registry = DatasetRegistry()

    if installed_only:
        datasets = [m.dataset for m in registry.list_manifests()]
    else:
        datasets = registry.list_datasets()

    if not datasets:
        console.print("[yellow]No datasets found[/yellow]")
        return

    table = Table(title="Available Datasets")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Description")

    for ds in datasets:
        status = "Installed" if registry.is_installed(ds.dataset_id) else "Available"
        table.add_row(
            ds.dataset_id,
            ds.name,
            ds.version,
            status,
            ds.description or "",
        )

    console.print(table)


@data.command("install")
@click.argument("dataset_id")
@click.option("--version", default=None, help="Dataset version to install")
@click.option("--force", is_flag=True, help="Force reinstall if already installed")
def data_install(dataset_id: str, version: str | None, force: bool) -> None:
    """Install a dataset."""
    registry = DatasetRegistry()

    if registry.is_installed(dataset_id) and not force:
        console.print(f"[yellow]Dataset {dataset_id} already installed. Use --force to reinstall.[/yellow]")
        return

    console.print(f"[cyan]Installing dataset: {dataset_id}[/cyan]")

    if dataset_id == "tanzil":
        # Use fixture data for testing - in production would download from tanzil.net
        provider = TanzilProvider()

        # Initialize database
        db = Database()
        data_access = DataAccess(db)

        # Use test fixture
        fixture_path = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "tanzil"
        quran_xml = fixture_path / "quran.xml"
        metadata_xml = fixture_path / "metadata.xml"

        if quran_xml.exists():
            manifest = provider.import_into_database(
                quran_xml,
                metadata_xml if metadata_xml.exists() else None,
                edition_id="tanzil-uthmani-v1",
                data_access=data_access,
            )
            # Register the manifest
            registry.register(manifest)
            console.print(f"[green]Installed Tanzil {manifest.dataset.version}[/green]")
        else:
            console.print("[red]Tanzil fixture not found. Use test fixtures for now.[/red]")
            console.print("For production, download quran.xml and metadata.xml from tanzil.net")
    elif dataset_id == "qac":
        console.print("[yellow]QAC installation requires manual download due to licensing restrictions.[/yellow]")
        console.print("See docs/datasets.md for instructions.")
    else:
        console.print(f"[red]Unknown dataset: {dataset_id}[/red]")
        sys.exit(1)


@data.command("validate")
@click.argument("dataset_id")
def data_validate(dataset_id: str) -> None:
    """Validate an installed dataset."""
    registry = DatasetRegistry()

    if not registry.is_installed(dataset_id):
        console.print(f"[red]Dataset {dataset_id} not installed[/red]")
        sys.exit(1)

    console.print(f"[cyan]Validating dataset: {dataset_id}[/cyan]")
    results = registry.verify_checksums(dataset_id)
    for path, valid in results.items():
        status = "✓" if valid else "✗"
        console.print(f"  {status} {path}")

    if all(results.values()):
        console.print("[green]All checksums valid[/green]")
    else:
        console.print("[red]Some checksums failed[/red]")


@data.command("manifest")
@click.argument("dataset_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def data_manifest(dataset_id: str, output: str | None) -> None:
    """Show or export dataset manifest."""
    registry = DatasetRegistry()

    if not registry.is_installed(dataset_id):
        console.print(f"[red]Dataset {dataset_id} not installed[/red]")
        sys.exit(1)

    manifest = registry.get(dataset_id)
    if not manifest:
        console.print(f"[red]No manifest found for {dataset_id}[/red]")
        sys.exit(1)

    manager = ManifestManager()

    if output:
        manager.save_manifest(manifest, Path(output))
        console.print(f"[green]Manifest saved to {output}[/green]")
    else:
        console.print(manager.manifest_to_json(manifest))


def _format_search_result(r: Any) -> tuple[str, str, str, str, str]:
    """Format a search result (either dict or SearchResult) for display."""
    if isinstance(r, SearchResult):
        return (
            r.reference,
            str(r.surah_number),
            str(r.ayah_number),
            r.match_type.value,
            r.matched_text[:MAX_DISPLAY_LENGTH] + ("..." if len(r.matched_text) > MAX_DISPLAY_LENGTH else ""),
        )
    else:
        # dict format
        return (
            r.get("reference", ""),
            str(r.get("surah_number", "")),
            str(r.get("ayah_number", "")),
            r.get("match_type", ""),
            r.get("matched_text", "")[:MAX_DISPLAY_LENGTH] + ("..." if len(r.get("matched_text", "")) > MAX_DISPLAY_LENGTH else ""),
        )


@main.command()
@click.argument("query")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition to search")
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["exact", "diacritic-insensitive", "broad", "canonical"]),
    default="diacritic-insensitive",
    help="Search mode",
)
@click.option("--limit", "-l", default=20, help="Maximum results")
def search(query: str, edition: str, mode: str, limit: int) -> None:
    """Search for text in the Qur'an."""
    quran = Quran.load()

    mode_map = {
        "exact": "exact_source",
        "diacritic-insensitive": "diacritics_insensitive",
        "broad": "broad_orthographic",
        "canonical": "canonical_unicode",
    }

    results = quran.search(
        query,
        mode=mode_map[mode],
        edition_id=edition,
        limit=limit,
    )

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Reference", style="cyan")
    table.add_column("Surah", style="green")
    table.add_column("Ayah", style="green")
    table.add_column("Match Type", style="yellow")
    table.add_column("Text")

    for r in results:
        ref, surah, ayah, match_type, text = _format_search_result(r)
        table.add_row(ref, surah, ayah, match_type, text)

    console.print(table)


@main.command()
@click.argument("reference")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option("--min-length", default=2, help="Minimum phrase length in words")
def mutashabihat(reference: str, edition: str, min_length: int) -> None:
    """Find repeated phrases (mutashabihat) for an ayah."""

    engine = MutashabihatEngine(DataAccess())

    result = engine.find_exact_phrase(reference, edition_id=edition, min_length=min_length)

    if not result.matches:
        console.print(f"[yellow]No repeated phrases found for {reference}[/yellow]")
        return

    table = Table(title=f"Mutashabihat for {reference} (Method: {result.method.value})")
    table.add_column("Left", style="cyan")
    table.add_column("Right", style="cyan")
    table.add_column("Method", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Score", style="magenta")

    for m in result.matches[:30]:
        table.add_row(
            m.left_reference,
            m.right_reference,
            m.match_method.value,
            m.match_category.value,
            f"{m.score:.3f}" if m.score else "N/A",
        )

    console.print(table)
    console.print(f"\nTotal matches: {result.total_matches}")


@main.command()
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option("--n", default=3, help="N-gram size")
@click.option("--min-occurrences", default=2, help="Minimum occurrences")
def ngrams(edition: str, n: int, min_occurrences: int) -> None:
    """Find recurring n-grams across the corpus."""

    engine = MutashabihatEngine(DataAccess())

    matches = engine.find_exact_ngrams(edition_id=edition, n=n, min_occurrences=min_occurrences)

    if not matches:
        console.print("[yellow]No recurring n-grams found[/yellow]")
        return

    table = Table(title=f"Recurring {n}-grams (≥{min_occurrences} occurrences)")
    table.add_column("Left", style="cyan")
    table.add_column("Right", style="cyan")
    table.add_column("N-gram", style="green")

    for m in matches[:50]:
        ngram = m.alignment.get("ngram", "") if m.alignment else ""
        table.add_row(m.left_reference, m.right_reference, ngram)

    console.print(table)


@main.command()
@click.argument("reference")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
def ayah(reference: str, edition: str) -> None:
    """Get ayah text and metadata."""
    quran = Quran.load()

    try:
        parts = reference.split(":")
        surah_num = int(parts[0])
        ayah_num = int(parts[1])
        ayah_obj = quran.ayah(surah_num, ayah_num)
    except Exception:
        console.print(f"[red]Ayah not found: {reference}[/red]")
        sys.exit(1)

    if not ayah_obj:
        console.print(f"[red]Ayah not found: {reference}[/red]")
        sys.exit(1)

    ayah_text = quran.ayah_text(surah_num, ayah_num, edition_id=edition)

    console.print(f"[cyan]{ayah_obj.reference}[/cyan]")
    console.print(f"[green]{ayah_text.text_original}[/green]")

    # Show word tokens
    tokens = quran.word_tokens(surah_num, ayah_num)
    if tokens:
        table = Table(title="Word Tokens")
        table.add_column("Index", style="cyan")
        table.add_column("Token", style="green")
        table.add_column("Start", style="yellow")
        table.add_column("End", style="yellow")

        for t in tokens:
            table.add_row(str(t.token_index), t.surface_original, str(t.char_start), str(t.char_end))

        console.print(table)


@main.command()
@click.option("--surah", "-s", type=int, help="Surah number (1-114)")
def surah(surah: int | None) -> None:
    """List surahs or get surah details."""
    quran = Quran.load()

    if surah:
        s = quran.surah(surah)
        if not s:
            console.print(f"[red]Surah not found: {surah}[/red]")
            sys.exit(1)

        console.print(f"[cyan]Surah {s.surah_number}: {s.name_arabic}[/cyan]")
        console.print(f"[green]{s.name_transliteration} ({s.name_translation})[/green]")
        console.print(f"Ayahs: {s.ayah_count}")
    else:
        surahs = quran.surahs()
        table = Table(title="Surahs")
        table.add_column("#", style="cyan")
        table.add_column("Arabic", style="green")
        table.add_column("Transliteration", style="yellow")
        table.add_column("Translation", style="magenta")
        table.add_column("Ayahs", style="blue")

        for s in surahs:
            table.add_row(str(s.surah_number), s.name_arabic, s.name_transliteration or "", s.name_translation or "", str(s.ayah_count))

        console.print(table)


@main.command()
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
def editions(edition: str) -> None:
    """List available text editions."""
    quran = Quran.load()

    available = quran.available_editions

    table = Table(title="Available Text Editions")
    table.add_column("Edition ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Script", style="yellow")
    table.add_column("Default", style="magenta")

    for e in available:
        is_default = "✓" if e.edition_id == edition else ""
        table.add_row(e.edition_id, e.name, e.script_type, is_default)

    console.print(table)


@main.command()
def profiles() -> None:
    """List available normalization profiles."""
    from qurankit.search.normalization import get_engine

    engine = get_engine()
    profiles = engine.list_profiles()

    table = Table(title="Normalization Profiles")
    table.add_column("Profile ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Description")

    for p in profiles:
        table.add_row(p.profile_id, p.name, p.version, p.description)

    console.print(table)


@main.group()
def research() -> None:
    """Advanced research commands."""
    pass


@research.command("semantic-relations")
@click.argument("root", required=False)
@click.option("--lemma", "-l", default=None, help="Lemma to look up")
@click.option("--type", "-t", "rel_type", type=click.Choice(["synonym", "antonym", "related", "all"]), default="all", help="Relation type")
@click.option("--resource", "-r", default=None, help="Specific resource ID")
def semantic_relations(root: str | None, lemma: str | None, rel_type: str, resource: str | None) -> None:
    """Find semantic relations (synonyms, antonyms) from dictionary sources."""

    extractor = SemanticRelationExtractor()
    resource_ids = [resource] if resource else None

    if rel_type == "synonym":
        types = [SemanticRelationType.SYNONYM]
    elif rel_type == "antonym":
        types = [SemanticRelationType.ANTONYM]
    elif rel_type == "related":
        types = [SemanticRelationType.RELATED]
    else:
        types = None  # All

    if root:
        relations = extractor.find_relations_for_root(root, relation_types=types, resource_ids=resource_ids)
    elif lemma:
        relations = extractor.find_relations_for_lemma(lemma, relation_types=types, resource_ids=resource_ids)
    else:
        console.print("[red]Either --root or --lemma must be provided[/red]")
        sys.exit(1)

    if not relations:
        console.print("[yellow]No semantic relations found[/yellow]")
        return

    table = Table(title=f"Semantic Relations for {root or lemma}")
    table.add_column("Subject", style="cyan")
    table.add_column("Root", style="green")
    table.add_column("Relation", style="yellow")
    table.add_column("Object", style="magenta")
    table.add_column("Object Root", style="blue")
    table.add_column("Source", style="white")

    for rel in relations[:50]:
        table.add_row(
            rel.subject_headword,
            rel.subject_root or "",
            rel.relation_type.value,
            rel.object_headword,
            rel.object_root or "",
            rel.source_resource or "",
        )

    console.print(table)
    console.print(f"\nTotal relations: {len(relations)}")


@research.command("collocations")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option("--window", "-w", default=5, help="Window size")
@click.option("--min-cooc", default=3, help="Minimum co-occurrence")
@click.option("--measure", "-m", type=click.Choice(["pmi", "t_test", "dice", "log_likelihood", "frequency"]), default="pmi", help="Statistical measure")
@click.option("--top", "-n", default=50, help="Top N results")
@click.option("--no-stopwords", is_flag=True, help="Don't filter stopwords")
def collocations(edition: str, window: int, min_cooc: int, measure: str, top: int, no_stopwords: bool) -> None:
    """Compute statistically significant word collocations."""

    analyzer = CollocationAnalyzer(edition_id=edition)

    measure_map = {
        "pmi": CooccurrenceMeasure.PMI,
        "t_test": CooccurrenceMeasure.T_TEST,
        "dice": CooccurrenceMeasure.DICE,
        "log_likelihood": CooccurrenceMeasure.LOG_LIKELIHOOD,
        "frequency": CooccurrenceMeasure.FREQUENCY,
    }

    results = analyzer.compute_collocations(
        window_size=window,
        min_cooccurrence=min_cooc,
        measure=measure_map[measure],
        top_n=top,
        filter_stopwords=not no_stopwords,
    )

    if not results:
        console.print("[yellow]No collocations found[/yellow]")
        return

    table = Table(title=f"Collocations ({measure.upper()})")
    table.add_column("Word 1", style="cyan")
    table.add_column("Root 1", style="green")
    table.add_column("Word 2", style="cyan")
    table.add_column("Root 2", style="green")
    table.add_column("Co-occur", style="yellow")
    table.add_column("Score", style="magenta")

    for r in results:
        table.add_row(
            r.word1,
            r.word1_root or "",
            r.word2,
            r.word2_root or "",
            str(r.cooccurrence_count),
            f"{r.score:.4f}",
        )

    console.print(table)


@research.command("collocations-for")
@click.argument("word")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option("--window", "-w", default=5, help="Window size")
@click.option("--measure", "-m", type=click.Choice(["pmi", "t_test", "dice", "log_likelihood", "frequency"]), default="pmi", help="Statistical measure")
@click.option("--top", "-n", default=20, help="Top N results")
def collocations_for(word: str, edition: str, window: int, measure: str, top: int) -> None:
    """Get collocations for a specific word."""

    analyzer = CollocationAnalyzer(edition_id=edition)

    measure_map = {
        "pmi": CooccurrenceMeasure.PMI,
        "t_test": CooccurrenceMeasure.T_TEST,
        "dice": CooccurrenceMeasure.DICE,
        "log_likelihood": CooccurrenceMeasure.LOG_LIKELIHOOD,
        "frequency": CooccurrenceMeasure.FREQUENCY,
    }

    results = analyzer.get_collocations_for_word(
        word,
        window_size=window,
        measure=measure_map[measure],
        top_n=top,
    )

    if not results:
        console.print(f"[yellow]No collocations found for '{word}'[/yellow]")
        return

    table = Table(title=f"Collocations for '{word}' ({measure.upper()})")
    table.add_column("Word 1", style="cyan")
    table.add_column("Root 1", style="green")
    table.add_column("Word 2", style="cyan")
    table.add_column("Root 2", style="green")
    table.add_column("Co-occur", style="yellow")
    table.add_column("Score", style="magenta")

    for r in results:
        table.add_row(
            r.word1,
            r.word1_root or "",
            r.word2,
            r.word2_root or "",
            str(r.cooccurrence_count),
            f"{r.score:.4f}",
        )

    console.print(table)


@research.command("cross-refs")
@click.argument("reference")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option("--explicit/--implicit", default=True, help="Explicit (dataset) or implicit (computed) links")
@click.option("--min-roots", default=2, help="Minimum shared roots (implicit)")
@click.option("--min-lemmas", default=1, help="Minimum shared lemmas (implicit)")
@click.option("--limit", "-l", default=20, help="Maximum results")
def cross_refs(reference: str, edition: str, explicit: bool, min_roots: int, min_lemmas: int, limit: int) -> None:
    """Find cross-references for an ayah."""

    analyzer = CrossReferenceAnalyzer(edition_id=edition)

    if explicit:
        results = analyzer.get_explicit_cross_references(reference)
        title = f"Explicit Cross-References for {reference}"
    else:
        results = analyzer.find_implicit_links(reference, min_shared_roots=min_roots, min_shared_lemmas=min_lemmas, limit=limit)
        title = f"Implicit Cross-References for {reference}"

    if not results:
        console.print("[yellow]No cross-references found[/yellow]")
        return

    table = Table(title=title)
    table.add_column("Source", style="cyan")
    table.add_column("Target", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Evidence", style="yellow")
    table.add_column("Dataset", style="magenta")
    table.add_column("Confidence", style="blue")

    for r in results:
        table.add_row(
            r.source_reference,
            r.target_reference,
            r.relation_type,
            r.evidence or "",
            r.source_dataset or "",
            f"{r.confidence:.2f}" if r.confidence else "N/A",
        )

    console.print(table)


@research.command("wujuh-wa-nazair")
@click.argument("reference", required=False)
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option("--min-shared", default=3, help="Minimum shared words")
@click.option("--threshold", default=0.4, help="Similarity threshold")
@click.option("--limit", "-l", default=50, help="Maximum results")
def wujuh_wa_nazair(reference: str | None, edition: str, min_shared: int, threshold: float, limit: int) -> None:
    """Find wujuh wa nazair candidates (similar wording, different meaning)."""

    analyzer = WujuhWaNazairAnalyzer(edition_id=edition)

    if reference:
        results = analyzer.find_for_reference(reference, min_shared_words=min_shared, max_candidates=limit)
        title = f"Wujuh wa Nazair Candidates for {reference}"
    else:
        results = analyzer.find_candidates(min_shared_words=min_shared, max_candidates=limit, similarity_threshold=threshold)
        title = "Wujuh wa Nazair Candidates (Corpus-wide)"

    if not results:
        console.print("[yellow]No wujuh wa nazair candidates found[/yellow]")
        return

    table = Table(title=title)
    table.add_column("Ayah 1", style="cyan")
    table.add_column("Ayah 2", style="cyan")
    table.add_column("Similarity", style="green")
    table.add_column("Shared Words", style="yellow")

    for r in results:
        shared = ", ".join(r.shared_words[:8]) + ("..." if len(r.shared_words) > 8 else "")
        table.add_row(
            r.ayah1_reference,
            r.ayah2_reference,
            f"{r.similarity_score:.3f}",
            shared,
        )

    console.print(table)
    console.print(f"\nTotal candidates: {len(results)}")
    console.print("[dim]Note: These are computational candidates requiring scholarly review.[/dim]")


@main.command()
@click.argument("reference")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
@click.option(
    "--method",
    "-m",
    type=click.Choice(["exact", "normalized", "near-duplicate"]),
    default="exact",
    help="Analysis method",
)
@click.option("--threshold", default=0.7, help="Similarity threshold for near-duplicate")
@click.option("--profile", default="diacritics-insensitive-v1", help="Normalization profile")
@click.option("--min-length", default=2, help="Minimum phrase length")
def report(
    reference: str,
    edition: str,
    method: str,
    threshold: float,
    profile: str,
    min_length: int,
) -> None:
    """Generate mutashabihat comparison report for an ayah."""
    from qurankit.analysis import MatchMethod
    from qurankit.storage.access import DataAccess

    engine = MutashabihatEngine(DataAccess())
    reporter = ReportGenerator(DataAccess())

    method_map = {
        "exact": MatchMethod.EXACT_PHRASE,
        "normalized": MatchMethod.NORMALIZED_EXACT,
        "near-duplicate": MatchMethod.NEAR_DUPLICATE,
    }

    match_method = method_map[method]

    if match_method == MatchMethod.EXACT_PHRASE:
        result = engine.find_exact_phrase(reference, edition_id=edition, min_length=min_length)
    elif match_method == MatchMethod.NORMALIZED_EXACT:
        result = engine.find_normalized_matches(
        reference, edition_id=edition, normalization_profile=profile, min_words=min_length
    )
    elif match_method == MatchMethod.NEAR_DUPLICATE:
        result = engine.find_near_duplicates(
        reference, edition_id=edition, threshold=threshold, normalization_profile=profile
    )
    else:
        console.print(f"[red]Unknown method: {method}[/red]")
        return

    report_obj = reporter.generate_report(result, edition, reference)
    console.print(reporter.format_report_text(report_obj))


@main.command()
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition")
def corpus_stats(edition: str) -> None:
    """Generate corpus-level mutashabihat statistics."""
    from qurankit.storage.access import DataAccess

    reporter = ReportGenerator(DataAccess())
    stats = reporter.generate_corpus_statistics(edition)

    table = Table(title=f"Corpus Statistics for {edition}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Ayahs", str(stats.get("total_ayahs", 0)))
    table.add_row("Total Surahs", str(stats.get("total_surahs", 0)))

    for ngram_type, data in stats.get("ngram_statistics", {}).items():
        table.add_row(f"{ngram_type} - Total Matches", str(data.get("total_matches", 0)))
        table.add_row(f"{ngram_type} - Unique N-grams", str(data.get("unique_ngrams", 0)))

    console.print(table)


if __name__ == "__main__":
    main()
