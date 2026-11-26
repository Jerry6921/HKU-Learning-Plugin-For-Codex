"""Run the local HIQS setup commands."""

import json

import typer

from .core.facade import build_port

app = typer.Typer()
apple = typer.Typer()
app.add_typer(apple, name="apple")


@app.command()
def login_moodle() -> None:
    """Open the official Moodle login and wait for the user to finish."""
    result = build_port().login_moodle()
    typer.echo(json.dumps(result, ensure_ascii=False))


@apple.command()
def connect(account_mode: str = "icloud") -> None:
    """Authorize the HIQS Calendar and Reminders connection."""
    result = build_port().apple.configure({"account_mode": account_mode, "confirmed": True})
    typer.echo(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    app()
