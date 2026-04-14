"""
cli.py
~~~~~~
Command-line interface for neuro-readability.
Installed as the 'nr' command via setup.py entry_points.

Usage examples:
    nr analyse myfile.txt
    nr analyse myfile.txt --format json
    nr analyse myfile.txt --target-grade 10
    nr analyse myfile.txt --output report.txt
    echo "Some text..." | nr analyse -
    nr analyse --url https://example.com/article
"""

import sys
import click

from neuro_readability import NeuroReadabilityAnalyser


@click.group()
@click.version_option(version="1.0.0", prog_name="neuro-readability")
def cli():
    """
    neuro-readability: Neuroscience-informed text analysis.

    Analyse any text for cognitive load, readability grade level,
    passive voice density, complex word usage, and more.
    """
    pass


@cli.command()
@click.argument("source", default="-")
@click.option("--url", default=None, help="Fetch and analyse text from a URL instead of a file.")
@click.option(
    "--format", "fmt",
    type=click.Choice(["terminal", "json", "text"], case_sensitive=False),
    default="terminal",
    show_default=True,
    help="Output format."
)
@click.option(
    "--target-grade", "target_grade",
    type=float,
    default=None,
    help="Target Flesch-Kincaid grade level. Report will include a gap analysis."
)
@click.option(
    "--output", "output_file",
    type=click.Path(),
    default=None,
    help="Save report to a file instead of printing to stdout."
)
@click.option(
    "--fail-on-exceed",
    is_flag=True,
    default=False,
    help="Exit with code 1 if grade level exceeds --target-grade. Useful for CI."
)
def analyse(source, url, fmt, target_grade, output_file, fail_on_exceed):
    """
    Analyse a text file, stdin, or URL for readability and cognitive load.

    SOURCE can be a file path or '-' to read from stdin (default).

    Examples:

    \b
        nr analyse myessay.txt
        nr analyse myessay.txt --format json --target-grade 10
        echo "Some text." | nr analyse -
        nr analyse --url https://example.com/some-article
    """
    analyser = NeuroReadabilityAnalyser(target_grade=target_grade)

    # Determine input source
    if url:
        text, source_name = _fetch_url(url)
    elif source == "-":
        if sys.stdin.isatty():
            click.echo("Reading from stdin... (paste text then press Ctrl+D)", err=True)
        text = sys.stdin.read()
        source_name = "stdin"
    else:
        try:
            with open(source, "r", encoding="utf-8") as f:
                text = f.read()
            source_name = source
        except FileNotFoundError:
            click.echo(f"Error: File not found: {source}", err=True)
            sys.exit(1)

    if not text.strip():
        click.echo("Error: Input text is empty.", err=True)
        sys.exit(1)

    try:
        report = analyser.analyse(text)
    except Exception as e:
        click.echo(f"Analysis error: {e}", err=True)
        sys.exit(1)

    output = analyser.format_report(report, fmt=fmt, source_name=source_name)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        click.echo(f"Report saved to: {output_file}", err=True)
    else:
        click.echo(output)

    # CI grade check
    if fail_on_exceed and target_grade is not None:
        if report.grade_level > target_grade:
            click.echo(
                f"FAIL: Grade level {report.grade_level:.1f} exceeds target {target_grade:.0f}",
                err=True
            )
            sys.exit(1)


def _fetch_url(url: str):
    """Fetch a URL and strip HTML tags. Returns (text, url)."""
    try:
        import urllib.request
        import html
        import re

        with urllib.request.urlopen(url, timeout=10) as response:
            raw_html = response.read().decode("utf-8", errors="replace")

        # Remove script/style blocks
        clean = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', raw_html,
                       flags=re.DOTALL | re.IGNORECASE)
        # Strip all tags
        clean = re.sub(r'<[^>]+>', ' ', clean)
        # Decode HTML entities
        clean = html.unescape(clean)
        # Collapse whitespace
        clean = re.sub(r'[ \t]+', ' ', clean)
        clean = re.sub(r'\n{3,}', '\n\n', clean)

        return clean.strip(), url

    except Exception as e:
        click.echo(f"Error fetching URL: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
