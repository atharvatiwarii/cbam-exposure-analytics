
"""
UN Comtrade trade data extraction module.

Initial scope:
- Reporter: India (699)
- Partner: World (0)
- Frequency: Annual
- Commodity: HS 7208
- Flow: Exports
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

API_URL = (
    "https://comtradeapi.un.org/data/v1/get/C/A/HS"
)

SOURCE_NAME = "UN Comtrade"

load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. API session and authentication
# --------------------------------------------------

def create_session(api_key: str) -> requests.Session:
    """Create an authenticated session with retry handling."""

    retry_strategy = Retry(
        total=4,
        connect=3,
        read=3,
        status=4,
        backoff_factor=1.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()

    session.mount("https://", adapter)

    session.headers.update({
        "Ocp-Apim-Subscription-Key": api_key,
        "User-Agent": "cbam-exposure-analytics/0.1",
    })

    return session


# --------------------------------------------------
# 3. Extract trade data
# --------------------------------------------------

def fetch_trade_data(
    reporter_code: int = 699,
    partner_code: int = 0,
    year: int = 2024,
    commodity_code: str = "7208",
    flow_code: str = "X",
    max_records: int = 100000,
) -> dict[str, Any]:
    """Retrieve trade data from the UN Comtrade API."""

    api_key = os.getenv("COMTRADE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "COMTRADE_API_KEY not found. "
            "Check your project-root .env file."
        )

    if not 1 <= max_records <= 100000:
        raise ValueError(
            "max_records must be between 1 and 100000."
        )

    params = {
        "reporterCode": reporter_code,
        "period": year,
        "partnerCode": partner_code,
        "cmdCode": commodity_code,
        "flowCode": flow_code,
        "maxRecords": max_records,
    }

    logger.info(
        "Requesting UN Comtrade data: reporter=%s, "
        "partner=%s, year=%s, commodity=%s",
        reporter_code,
        partner_code,
        year,
        commodity_code,
    )

    with create_session(api_key) as session:

        response = session.get(
            API_URL,
            params=params,
            timeout=(15, 90),
        )

    if response.status_code in (401, 403):
        raise RuntimeError(
            "UN Comtrade authentication failed. "
            "Check whether your API key is valid."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "UN Comtrade rate limit reached after retries. "
            "Wait before trying again."
        )

    response.raise_for_status()

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "The API returned an invalid JSON response."
        ) from exc

    if payload.get("error"):
        raise RuntimeError(
            f"UN Comtrade API error: {payload['error']}"
        )

    logger.info(
        "API request successful. Records returned: %s",
        payload.get("count", 0),
    )

    return payload


# --------------------------------------------------
# 4. Validate and save extracted data
# --------------------------------------------------

def save_trade_data(
    payload: dict[str, Any],
    reporter_code: int,
    partner_code: int,
    year: int,
    commodity_code: str,
    flow_code: str,
) -> None:
    """Preserve raw API data and save processed CSV output."""

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    filename = (
        f"comtrade_{reporter_code}_{partner_code}_"
        f"{year}_{commodity_code}"
    )

    raw_path = RAW_DIR / f"{filename}.json"
    processed_path = PROCESSED_DIR / f"{filename}.csv"
    metadata_path = RAW_DIR / f"{filename}_metadata.json"

    # Preserve the original API response.
    with raw_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)

    records = payload.get("data", [])

    if not records:
        raise RuntimeError(
            "No trade records returned. "
            "Raw API response has been preserved."
        )

    df = pd.DataFrame(records)

    required_columns = {
        "reporterCode",
        "partnerCode",
        "period",
        "cmdCode",
        "primaryValue",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required API columns: {missing_columns}"
        )

    numeric_columns = [
        "primaryValue",
        "netWgt",
        "grossWgt",
        "qty",
        "altQty",
        "fobvalue",
        "cifvalue",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # Add source and extraction metadata.
    df["source"] = SOURCE_NAME
    df["source_endpoint"] = API_URL
    df["extraction_timestamp_utc"] = timestamp

    df.to_csv(
        processed_path,
        index=False,
        encoding="utf-8",
    )

    metadata = {
        "source": SOURCE_NAME,
        "endpoint": API_URL,
        "extracted_at_utc": timestamp,
        "reporter_code": reporter_code,
        "partner_code": partner_code,
        "year": year,
        "commodity_code": commodity_code,
        "flow_code": flow_code,
        "api_reported_count": payload.get("count"),
        "records_saved": len(df),
        "raw_file": str(raw_path.relative_to(PROJECT_ROOT)),
        "processed_file": str(
            processed_path.relative_to(PROJECT_ROOT)
        ),
    }

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    logger.info("Raw data saved: %s", raw_path)
    logger.info("Processed data saved: %s", processed_path)
    logger.info("Records saved: %s", len(df))


# --------------------------------------------------
# 5. Command-line execution
# --------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Extract trade data from UN Comtrade."
    )

    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--reporter", type=int, default=699)
    parser.add_argument("--partner", type=int, default=0)
    parser.add_argument("--commodity", default="7208")
    parser.add_argument("--flow", default="X")

    parser.add_argument(
        "--max-records",
        type=int,
        default=100000,
    )

    args = parser.parse_args()

    try:
        payload = fetch_trade_data(
            reporter_code=args.reporter,
            partner_code=args.partner,
            year=args.year,
            commodity_code=args.commodity,
            flow_code=args.flow,
            max_records=args.max_records,
        )

        save_trade_data(
            payload=payload,
            reporter_code=args.reporter,
            partner_code=args.partner,
            year=args.year,
            commodity_code=args.commodity,
            flow_code=args.flow,
        )

        logger.info("Trade extraction completed successfully.")

    except (requests.RequestException, RuntimeError, ValueError) as exc:
        logger.error("Extraction failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
