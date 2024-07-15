from pathlib import Path

import uvicorn
from rich import print as rprint
from typer import Typer, Option

from contextqa import settings, logger, contextqa_base_data_dir

app = Typer()


@app.command()
def init(
    port: int = Option(8080, "--port", "-p", help="Port number to run the server on"),
    settings_path: Path = Option(
        contextqa_base_data_dir / "settings.json",
        "--settings-json",
        "-s",
        help="Path to the json file that will held the settings",
        file_okay=True,
        dir_okay=False,
    ),
    media_home: Path = Option(
        contextqa_base_data_dir / "media",
        "--media-home",
        "-m",
        help="Path to the directory that will contain media files such as ingested PDFs",
        file_okay=False,
    ),
    local_vectordb_home: Path = Option(
        contextqa_base_data_dir / "vectordb-data",
        "--chroma-home",
        "-c",
        help="Path to the directory that will be used by ChromaDB",
        file_okay=False,
    ),
):
    """ContextQA init command"""
    if any(
        (
            settings_path != contextqa_base_data_dir / "settings.json",
            media_home != contextqa_base_data_dir / "media",
            local_vectordb_home != contextqa_base_data_dir / "vectordb-data",
        )
    ):
        rprint(
            "[bold yellow]\nBe careful when using either of the following parameters for setting custom paths: -s, -m or -c. "
            "Data might be lost if you already have initialized contextqa. If this is the first time, proceed.[/bold yellow]\n"
        )
    settings.init_from_cli(settings_path, media_home, local_vectordb_home)
    uvicorn.run("contextqa.main:app", host="localhost", port=port, loop="asyncio")


@app.callback()
def callback():
    """Force the CLI to create an independent command (init)"""


def main():
    """Main entrypoint"""
    try:
        app(prog_name="contextqa")
    except Exception as err:
        logger.exception("Unexpected error running the command. Cause %s", err)
