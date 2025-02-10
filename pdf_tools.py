import fitz  # PyMuPDF
from rich import print
from rich.console import Console
from rich.traceback import install
from rich.progress import track
import tiktoken
import os

# Install rich traceback for better error display
install()

# Create a console for styled output
console = Console()


def pdf_extract_text(pdf_path, start_page=None, end_page=None):
    """
    Extracts text from specific pages of a PDF file.

    Args:
      pdf_path: The path to the PDF file.
      start_page: The starting page number (inclusive, starts from 1).
      end_page: The ending page number (inclusive).

    Returns:
      A string containing the extracted text from the specified pages.
    """
    try:
        doc = fitz.open(pdf_path)
        num_pages = doc.page_count

        # Handle cases where start_page or end_page are not provided
        if start_page is None:
            start_page = 1
        if end_page is None:
            end_page = num_pages

        # Adjust page numbers to be zero-based for indexing
        start_page_index = start_page - 1
        end_page_index = end_page - 1

        # Validate page numbers
        if (
            start_page_index < 0
            or end_page_index >= num_pages
            or start_page_index > end_page_index
        ):
            raise ValueError("Invalid page range provided.")

        console.log(f"Extracting text from [bold blue]{pdf_path}[/bold blue]...")
        text = ""
        for page_num in track(
            range(start_page_index, end_page_index + 1),
            description=f"[cyan]Processing pages {start_page} to {end_page}[/cyan]",
        ):
            page = doc[page_num]
            text += page.get_text()

        doc.close()
        console.log("[green]Text extraction completed successfully.[/green]")
        return text
    except FileNotFoundError:
        console.print(f"[red]Error: File not found at {pdf_path}[/red]")
        return None
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
        return None


def count_tokens(file_path, model="cl100k_base"):
    """
    Count the number of tokens in a file using an LLM-compatible tokenizer.

    Args:
      file_path: The path to the file containing text.
      model: The tokenizer model to use (default: "cl100k_base").

    Returns:
      The number of tokens in the file.
    """
    try:
        # Initialize the tokenizer for the specified model
        tokenizer = tiktoken.get_encoding(model)

        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Tokenize the content and count the tokens
        tokens = tokenizer.encode(content)
        return len(tokens)
    except FileNotFoundError:
        console.print(f"[red]Error: File not found at {file_path}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
        return None


def main():
    fn = "/home/michael/gitrepos/IBG/references/Bevere02 A isca de Satanas.pdf"
    start_page = 18
    end_page = 27
    text = pdf_extract_text(fn, start_page=start_page, end_page=end_page)
    if text:
        # Generate the output filename
        base, ext = os.path.splitext(fn)
        output_filename = f"{base}_{start_page:03d}-{end_page:03d}.txt"

        if os.path.exists(output_filename):
            console.print(f"[bold red]File already exists: {output_filename}[/bold red]")
            return

        # Save the extracted text to the file
        with open(output_filename, "w", encoding="utf-8") as output_file:
            output_file.write(text)

        console.print(f"[bold green]Text saved to: {output_filename}[/bold green]")

        num_tokens = count_tokens(output_filename)
        console.print(f"[bold green]Number of tokens: {num_tokens}[/bold green]")


if __name__ == "__main__":
    main()
