"""Console script for quantlib_server."""
import quantlib_server

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for quantlib_server."""
    console.print("Replace this message by putting your code into "
               "quantlib_server.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
