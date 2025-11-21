
# sec-sum

A command-line tool for fetching, parsing, and summarizing SEC filings using LLMs.



## Overview

`sec-sum` is a simple CLI that:

1. **Fetches** recent 10-K/10-Q filings for a given ticker/CIK from EDGAR  
2. **Parses** the primary HTML filing to extract key sections (Item 1, 1A, 2, 3, 4, 7, 7A, 9A)  
3. **Summarizes** those sections using an OpenAI model into a Markdown summary

## Features

- ✅ Ticker → CIK resolution using the official SEC ticker map  
- ✅ Fetches the latest 10-K/10-Q filings and stores them on disk  
- ✅ Parses key sections:
  | Item No. | 10-K Meaning                                  | 10-Q Meaning                                      |
  |----------|-----------------------------------------------|----------------------------------------------------|
  | Item 1   | Business                                      | Financial Statements                               |
  | Item 1A  | Risk Factors                                  | Risk Factor Updates (appears in Part II, Item 1A)  |
  | Item 2   | Properties                                    | MD&A (Management’s Discussion & Analysis)          |
  | Item 3   | Legal Proceedings                             | Market Risk (Quantitative & Qualitative)           |
  | Item 4   | Mine Safety Disclosures / Other Information*  | Controls and Procedures                            |
  | Item 7   | MD&A (Management’s Discussion & Analysis)     | **Does not exist** (10-Q MD&A is Item 2)           |
  | Item 7A  | Market Risk                                   | **Does not exist** (10-Q Market Risk is Item 3)    |
  | Item 9A  | Controls and Procedures                       | **Does not exist** (10-Q Controls are Item 4)      |
- ✅ Writes a structured JSON file with `meta` + `sections`  
- ✅ Summarizes with an OpenAI model (default: `gpt-5-mini`) into Markdown  
- ✅ Works on macOS, Linux, and (with Python/uv) Windows



## Requirements

- Python **3.13+**  
- [uv](https://github.com/astral-sh/uv) for dependency and virtualenv management  
- An OpenAI API key with access to `gpt-5-mini` 
- `git` if cloning from GitHub

Tested on macOS; the instructions for Linux/Windows are the same except for environment variable.


## Installation

### 1. Clone the repository

```bash
git clone https://github.com/cmorais17/sec-sum
cd sec-sum
```

### 2. Install dependencies with `uv`

```bash
uv sync
```

This will:

- create a virtual environment (e.g. `.venv/`)
- install all runtime and dev dependencies from `pyproject.toml` / `uv.lock`



## Configuring your OpenAI API key

`sec-sum` looks for the API key in the `OPENAI_API_KEY` environment variable.

There are **two ways** to set it up; use whichever you prefer.



### Option A — Project-local `.env.local` (auto-loaded)

This is how the CLI is already set up internally.

1. In the project root (`sec-sum/`), create a file:

   ```bash
   touch .env.local
   ```

2. Put your key in it:

   ```bash
   OPENAI_API_KEY="sk-...your-real-key..."
   ```

   or

   ```bash
   export OPENAI_API_KEY="sk-...your-real-key..."
   ```

3. Make sure `.env.local` is **not tracked** by git (add to `.gitignore` if needed):

   ```gitignore
   .env.local
   ```

The CLI (`src/sec_sum/cli.py`) automatically reads `.env.local` at startup and populates `os.environ` if `OPENAI_API_KEY` is not already set.



### Option B — Set environment variable manually

You can also set the variable in your shell:

**macOS / Linux (bash/zsh):**

```bash
export OPENAI_API_KEY="sk-...your-real-key..."
```

**Windows (PowerShell):**

```powershell
$env:OPENAI_API_KEY="sk-...your-real-key..."
```

**Windows (cmd):**

```cmd
set OPENAI_API_KEY=sk-...your-real-key...
```

After setting it, you can run the CLI normally.



## Usage

The CLI entrypoint is `sec-sum` (configured via `pyproject.toml`).

From the project root:

```bash
uv run sec-sum --help
```

You should see subcommands: `fetch`, `parse`, `summarize`.



### 1. Fetch recent filings

Fetch latest filings (default forms: `10-K,10-Q`) for a ticker:

```bash
uv run sec-sum fetch --ticker AAPL --limit 4
```

Example output:

```text
Fetched 4 filings for AAPL
- 10-K 2025-10-31 0000320193-25-000079
- 10-Q 2025-08-01 0000320193-25-000073
- 10-Q 2025-05-02 0000320193-25-000057
- 10-Q 2025-01-31 0000320193-25-000008
```

This will populate a `data/` directory like:

```text
data/
  0000320193/
    000032019325000079/
      aapl-20250927.htm
      index.path
      manifest.json
    ...
  meta/
    ticker_map.json
```

You can also pass a CIK directly:

```bash
uv run sec-sum fetch --ticker 0000320193 --limit 2
```



### 2. Parse a downloaded filing

Use the accession number from the fetch step:

```bash
uv run sec-sum parse --accession 0000320193-25-000079
```

Example output:

```text
Parsed filing written to out/0000320193_000032019325000079.json
```

This JSON contains:

- `meta` (CIK, form, filing date, report period, source path)
- `sections` (keys `item_1`, `item_1a`, `item_2`, `item_3`, `item_4`, `item_7`, `item_7a`, `item_9a` when present)

You can also parse a local HTML file directly:

```bash
uv run sec-sum parse --path data/0000320193/000032019325000079/aapl-20250927.htm
```



### 3. Summarize with an LLM

Given a parsed JSON file in `out/`, generate a Markdown summary:

```bash
uv run sec-sum summarize \
  --input out/0000320193_000032019325000079.json \
  --outdir out
```

Example output:

```text
Summary written to out/0000320193_000032019325000079.summary.md
```

You’ll now have:

```text
out/
  0000320193_000032019325000079.json
  0000320193_000032019325000079.summary.md
```

By default, the summarizer uses the `gpt-5-mini` model (see `src/sec_sum/summarizer.py`).  
If you want another model, you can change the `model` default in `summarize_parsed_file`



## Example summary

A full example Markdown summary (e.g. for Apple’s 2025 10-K) is provided in a separate file:

- See `EXAMPLE_SUMMARY.md` for a complete sample output.



## Development

If you want to hack on this project:

### Install dev tools

```bash
uv sync
```

### Run tests

```bash
uv run pytest
```

### Lint / format / type-check

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run black src
```

Pre-commit hooks (configured in `.pre-commit-config.yaml`) will run `black`, `ruff`, and `mypy` automatically on commit.



## Project structure

High-level layout:

```text
sec-sum/
  data/              # Downloaded filings + manifests
  out/               # Parsed JSON + summaries
  src/
    sec_sum/
      cli.py         # CLI entrypoint (fetch/parse/summarize)
      parse_core.py  # Filing parsing + section extraction
      summarizer.py  # LLM summarization logic
      fetch/         # Filing fetching from CIK/Ticker
        net.py
        ids.py
        submissions.py
        fetcher.py
        storage.py
        archive.py
        models.py
  tests/
    test_cli.py
  pyproject.toml
  README.md
```
