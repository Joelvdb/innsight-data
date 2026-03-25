# Innsight Data Scraper

A specialized tool for scraping, filtering, and analyzing Israeli planning data (TABA) from the Israel Land Authority (רשות מקרקעי ישראל). This project focuses on identifying hotel-related planning documents.

## Project Structure

- `retrieve_tabas_json.py`: Scrapes the official API to fetch metadata for all plans within a specified date range. Saves the raw metadata to `plans_data.json`.
- `search_hotels.py`: Filters the retrieved plans by searching for keywords like "מלון" (Hotel) within the plan's Takanon (PDF). Results are saved to `hotel_plans.json`.
- `local_storage/`: Local directory containing downloaded plan documents organized by `planId`.

## Getting Started

### Prerequisites

- Python 3.x
- Required libraries:
  ```bash
  pip install requests PyPDF2
  ```

### Usage

1. **Retrieve Raw Data:**
   Run the scraper to fetch recent planning data from the API:
   ```bash
   python3 retrieve_tabas_json.py
   ```
   *Note: You can modify the date range in the `if __name__ == "__main__":` block.*

2. **Filter for Hotels:**
   Analyze the downloaded metadata and search for hotel-related keywords in the associated PDFs:
   ```bash
   python3 search_hotels.py
   ```

## Output

- `plans_data.json`: Comprehensive list of all plans found in the date range.
- `hotel_plans.json`: Filtered list of plans where hotel keywords were found in the takanon text.
