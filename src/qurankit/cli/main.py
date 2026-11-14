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
from qurankit.datasets.manifest import ManifestManager
from qurankit.datasets.registry import DatasetRegistry
from qurankit.providers.tanzil import TanzilProvider
from qurankit.search.engine import SearchResult
from qurankit.storage import Database, DataAccess

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="qurankit")
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
            r.matched_text[:80] + ("..." if len(r.matched_text) > 80 else ""),
        )
    else:
        # dict format
        return (
            r.get("reference", ""),
            str(r.get("surah_number", "")),
            str(r.get("ayah_number", "")),
            r.get("match_type", ""),
            r.get("matched_text", "")[:80] + ("..." if len(r.get("matched_text", "")) > 80 else ""),
        )


@main.command()
@click.argument("query")
@click.option("--edition", "-e", default="tanzil-uthmani-v1", help="Text edition to search")
@click.option("--mode", "-m", type=click.Choice(["exact", "diacritic-insensitive", "broad", "canonical"]), default="diacritic-insensitive", help="Search mode")
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
    from qurankit.analysis import MutashabihatEngine

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
    from qurankit.analysis import MutashabihatEngine

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


if __name__ == "__main__":
    main()
