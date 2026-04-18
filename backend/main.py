import asyncio

import click
import uvicorn

from crawl_eval.pipeline import crawl_and_evaluate
from crawl_eval.urls import get_available_urls


AVAILABLE_URLS = get_available_urls()


def run_async(url: str) -> None:
    result = asyncio.run(crawl_and_evaluate(url=url))

    click.echo(f"URL: {result.url}")
    click.echo(f"Parser: {result.parser_name}")
    click.echo(f"Sample file: {result.sample_path}")
    click.echo(f"Extracted unique tokens: {result.metrics.extracted_count}")
    click.echo(f"Sample unique tokens: {result.metrics.sample_count}")
    click.echo(f"Intersection size: {result.metrics.intersection_count}")
    click.echo(f"Recall: {result.metrics.recall:.6f}")
    click.echo(f"Precision: {result.metrics.precision:.6f}")
    click.echo(f"F1 score: {result.metrics.f1:.6f}")


@click.group()
def cli() -> None:
    pass


@cli.command("run")
@click.option(
    "--url",
    type=click.Choice(AVAILABLE_URLS, case_sensitive=True),
    required=True,
)
def run_command(url: str) -> None:
    run_async(url)


@cli.command("list-urls")
def list_urls_command() -> None:
    for url in AVAILABLE_URLS:
        click.echo(url)


@cli.command("serve")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8003, show_default=True)
def serve_command(host: str, port: int) -> None:
    uvicorn.run("crawl_eval.api:app", host=host, port=port)


if __name__ == "__main__":
    cli()
