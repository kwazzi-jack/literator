# LLMs in Science Literature Review Tool

This tool helps fetch paper information from multiple API sources for a systematic literature review on "LLMs in Science", with a focus on radio astronomy and astrophysics.

## Setup

1. Install the required packages:
   ```bash
   pip install -e .
   ```

2. Configure your API keys:
   Create a `.env` file in the project root directory based on the provided `.env.template`:
   ```bash
   cp .env.template .env
   ```
   Then edit the `.env` file to add your API keys.

## Usage

The tool provides three main commands:

### Fetching Papers

```bash
# Basic search
python fetcher.py fetch --query "large language models AND astronomy"

# Search with year range and max results
python fetcher.py fetch --query "LLM AND (radio astronomy OR astrophysics)" \
                        --start-year 2020 --end-year 2023 --max-results 200

# Specify output file
python fetcher.py fetch --query "transformer models AND science" \
                        --output "results/transformer_papers.json"

# Save to vault storage
python fetcher.py fetch --query "LLM applications" --use-vault

# Don't save to database
python fetcher.py fetch --query "LLM applications" --no-db
```

### Querying the Database

```bash
# Simple query
python fetcher.py query --query "transformer"

# Filter by source and year
python fetcher.py query --source "scopus" --start-year 2020 --end-year 2022

# Save query results to file
python fetcher.py query --query "astronomy" --output "results/astronomy_papers.json"
```

### Viewing Database Statistics

```bash
python fetcher.py stats
```

## Database

The tool uses SQLModel to store all fetched papers in a SQLite database, making it easy to:
- Avoid duplicate entries
- Query papers using different criteria
- Perform analysis across multiple sources
- Track citation counts over time

The database is stored in the configured vault location.

## API Sources

Currently implemented:
- Scopus

Planned:
- arXiv
- Web of Science
- NASA ADS
- IEEE Xplore
- Others relevant to astronomy and astrophysics
