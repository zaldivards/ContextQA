from pathlib import Path

import uvicorn
from typer import Typer, Option


from contextqa import Configurables, logger


app = Typer()


@app.command()
def init(
    port: int = Option(8080, "--port", "-p", help="Port number to run the server on"),
    settings_path: Path = Option(
        Configurables.config_path,
        "--settings-json",
        "-s",
        help="Path to the json file that will held the settings",
        file_okay=True,
        dir_okay=False,
    ),
    media_home: Path = Option(
        Configurables.media_home,
        "--media-home",
        "-m",
        help="Path to the directory that will contain media files such as ingested PDFs",
        file_okay=False,
    ),
    local_vectordb_home: Path = Option(
        Configurables.local_vectordb_home,
        "--chroma-home",
        "-c",
        help="Path to the directory that will be used by ChromaDB",
        file_okay=False,
    ),
):
    """ContextQA init command"""
    Configurables.init(settings_path, media_home, local_vectordb_home)
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
