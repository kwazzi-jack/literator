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

To search for papers, use the `fetcher.py` script:

```bash
# Basic search
python fetcher.py --query "large language models AND astronomy"

# Search with year range and max results
python fetcher.py --query "LLM AND (radio astronomy OR astrophysics)" --start-year 2020 --end-year 2023 --max-results 200

# Specify output file
python fetcher.py --query "transformer models AND science" --output "results/transformer_papers.json"

# Save to vault storage
python fetcher.py --query "LLM applications" --use-vault
```

## API Sources

Currently implemented:
- Scopus

Planned:
- arXiv
- Web of Science
- NASA ADS
- IEEE Xplore
- Others relevant to astronomy and astrophysics

## Data Model

The tool converts all paper information to a standard format, making it easier to combine results from different sources. See `models.py` for details.
