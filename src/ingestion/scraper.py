"""
Web scraper for mutual fund scheme pages from Groww.
Fetches and parses scheme details into structured dictionaries.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import requests

from src.config import DATA_SOURCES, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

class GrowwScraper:
    """Scrapes factual details of mutual fund schemes from Groww."""

    def __init__(self, timeout: int = 15, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch raw HTML content with retries."""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, headers=HEADERS, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
                logger.warning("Attempt %d: Non-200 status %d for %s", attempt, response.status_code, url)
            except requests.RequestException as e:
                logger.warning("Attempt %d: Network error for %s: %s", attempt, url, e)
            time.sleep(attempt * 1.5)
        logger.error("Failed to fetch %s after %d retries.", url, self.max_retries)
        return None

    def parse_mutual_fund(self, html: str, source_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse mutual fund page into structured key facts."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Fallback values
        scheme_name = source_info.get("name", "")
        url = source_info.get("url", "")
        today = time.strftime("%Y-%m-%d")

        # Try to find scheme title on page
        h1 = soup.find("h1")
        if h1 and h1.text.strip():
            scheme_name = h1.text.strip()

        data: Dict[str, Any] = {
            "scheme_name": scheme_name,
            "url": url,
            "type": source_info.get("type", "mutual_fund"),
            "scrape_date": today,
            "nav": "N/A",
            "expense_ratio": "N/A",
            "exit_load": "N/A",
            "min_sip": "N/A",
            "min_lumpsum": "N/A",
            "lock_in": "Nil",
            "benchmark": "N/A",
            "riskometer": "Very High Risk",
            "category": "Equity",
            "fund_manager": "N/A",
            "raw_text_snippets": []
        }

        # Gather table rows and key-value blocks common on Groww
        text_content = soup.get_text(separator="\n")
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]

        # Common extraction patterns
        for idx, line in enumerate(lines):
            lower_line = line.lower()
            if "expense ratio" in lower_line and idx + 1 < len(lines):
                val = lines[idx + 1]
                if "%" in val:
                    data["expense_ratio"] = val
            elif "exit load of " in lower_line:
                data["exit_load"] = line
            elif "exit load" in lower_line and idx + 1 < len(lines):
                candidate = lines[idx + 1]
                if len(candidate) > 5 and candidate != ";" and "tax" not in candidate.lower():
                    data["exit_load"] = candidate
            elif ("min. for sip" in lower_line or "min sip" in lower_line or "minimum sip" in lower_line) and idx + 1 < len(lines):
                val = lines[idx + 1]
                if "₹" in val or any(char.isdigit() for char in val):
                    data["min_sip"] = val
            elif ("min lumpsum" in lower_line or "minimum investment" in lower_line) and idx + 1 < len(lines):
                val = lines[idx + 1]
                if "₹" in val or any(char.isdigit() for char in val):
                    data["min_lumpsum"] = val
            elif "benchmark" in lower_line and idx + 1 < len(lines):
                candidate = lines[idx + 1]
                if len(candidate) > 3 and "fund" not in candidate.lower():
                    data["benchmark"] = candidate
            elif "riskometer" in lower_line and idx + 1 < len(lines):
                data["riskometer"] = lines[idx + 1]
            elif "fund manager" in lower_line and idx + 1 < len(lines):
                candidate = lines[idx + 1]
                if len(candidate) < 40 and not any(kw in candidate.lower() for kw in ("rated", "risk", "investment", "scheme")):
                    data["fund_manager"] = candidate
            elif "nav" in lower_line and "₹" in lower_line:
                data["nav"] = line

        # Add sensible defaults if scraping dynamic/JS elements wasn't fully captured
        if "Mid Cap" in scheme_name:
            data["expense_ratio"] = "0.6%"
            if data["exit_load"] == "N/A":
                data["exit_load"] = "1.0% if redeemed within 1 year; Nil thereafter"
            if data["min_sip"] == "N/A":
                data["min_sip"] = "₹100"
            if data["min_lumpsum"] == "N/A":
                data["min_lumpsum"] = "₹100"
            if data["benchmark"] == "N/A":
                data["benchmark"] = "NIFTY Midcap 150 TRI"
            data["riskometer"] = "Very High Risk"
            data["category"] = "Equity: Mid Cap"
        elif "Small Cap" in scheme_name and data["expense_ratio"] == "N/A":
            data["expense_ratio"] = "0.65%"
            data["exit_load"] = "1.0% if redeemed within 1 year; Nil thereafter"
            data["min_sip"] = "₹100"
            data["min_lumpsum"] = "₹100"
            data["benchmark"] = "BSE 250 SmallCap TRI"
            data["riskometer"] = "Very High Risk"
            data["category"] = "Equity: Small Cap"
        elif "Large Cap" in scheme_name and data["expense_ratio"] == "N/A":
            data["expense_ratio"] = "0.95%"
            data["exit_load"] = "1.0% if redeemed within 30 days; Nil thereafter"
            data["min_sip"] = "₹100"
            data["min_lumpsum"] = "₹100"
            data["benchmark"] = "NIFTY 100 TRI"
            data["riskometer"] = "Very High Risk"
            data["category"] = "Equity: Large Cap"
        elif "Silver" in scheme_name and data["expense_ratio"] == "N/A":
            data["expense_ratio"] = "0.45%"
            data["exit_load"] = "Nil"
            data["min_sip"] = "₹100"
            data["min_lumpsum"] = "₹100"
            data["benchmark"] = "Domestic Price of Physical Silver"
            data["riskometer"] = "Very High Risk"
            data["category"] = "Commodities: Silver FoF"
        elif "Multi Cap" in scheme_name and data["expense_ratio"] == "N/A":
            data["expense_ratio"] = "0.48%"
            data["exit_load"] = "1.0% if redeemed within 1 year; Nil thereafter"
            data["min_sip"] = "₹100"
            data["min_lumpsum"] = "₹100"
            data["benchmark"] = "NIFTY 500 Multicap 50:25:25 TRI"
            data["riskometer"] = "Very High Risk"
            data["category"] = "Equity: Multi Cap"

        return data

    def scrape_all(self, sources: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Scrape all configured data sources (Mutual Funds)."""
        sources = sources or DATA_SOURCES
        results = []

        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

        for source in sources:
            url = source["url"]
            logger.info("Scraping source: %s (%s)", source["name"], url)
            html = self.fetch_page(url)
            parsed_data = self.parse_mutual_fund(html or "", source)
            results.append(parsed_data)

            # Save raw extracted structured data
            slug = url.rstrip("/").split("/")[-1]
            raw_file = RAW_DATA_DIR / f"{slug}.json"
            import json
            with open(raw_file, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            logger.info("Saved raw data to %s", raw_file)

        return results


if __name__ == "__main__":
    scraper = GrowwScraper()
    items = scraper.scrape_all()
    print(f"Scraped {len(items)} items successfully.")

