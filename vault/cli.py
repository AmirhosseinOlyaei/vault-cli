import typer
import sys
import logging
from pathlib import Path
from vault.crypto import encrypt_file, decrypt_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = typer.Typer(help="Secure file encryption tool")


@app.command()
def encrypt(
    filepath: str = typer.Argument(..., help="File to encrypt"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Encryption password"),
):
    """Encrypt a file with a password."""
    try:
        path = Path(filepath)
        if not path.exists():
            typer.echo(f"❌ File not found: {filepath}", err=True)
            raise typer.Exit(1)

        encrypted_path = encrypt_file(str(path), password)
        typer.echo(f"✓ Encrypted: {encrypted_path}")

    except Exception as e:
        typer.echo(f"❌ Encryption failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def decrypt(
    encrypted_path: str = typer.Argument(..., help="Encrypted file"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Decryption password"),
    output: str = typer.Option(None, "--output", "-o", help="Output file (default: remove .encrypted)"),
):
    """Decrypt a file with a password."""
    try:
        path = Path(encrypted_path)
        if not path.exists():
            typer.echo(f"❌ File not found: {encrypted_path}", err=True)
            raise typer.Exit(1)

        plaintext = decrypt_file(str(path), password)

        if output is None:
            output = str(path).replace(".encrypted", "")

        with open(output, "wb") as f:
            f.write(plaintext)

        typer.echo(f"✓ Decrypted: {output}")

    except ValueError as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Decryption failed: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
