from datetime import datetime
from centris.backend.centris_scraper import CentrisBienParser, CentrisScraper
from centris.backend.db_models import PlexCentrisListingDB
from centris import Session
from loguru import logger
from tqdm import tqdm


def get_existing_centris_ids() -> set[int]:
    with Session.begin() as session:
        existing_ids = {
            id_[0] for id_ in session.query(PlexCentrisListingDB.centris_id).all()
        }
    return existing_ids


# TODO - Add stopping criteria based on existing_ids: if among the URL of a given page, at least 1 is in the DB, we stop (because listings are sorted by date)
def get_urls(**kwargs) -> list[str]:
    scraper = CentrisScraper()
    urls = scraper.scrape_urls(**kwargs)
    return urls


def scrape_content(
    urls: list[str], scrape_date: datetime, existing_ids: set[int]
) -> list[PlexCentrisListingDB]:
    db_entries = []
    for url in tqdm(urls, desc="Scraping content of each listing URL"):
        try:
            centris_parser = CentrisBienParser(url)
            # TODO - we may want to still scrape the content and compare info (e.g. price update)
            if centris_parser.centris_id in existing_ids:
                logger.info(
                    f"Skipping {centris_parser.centris_id} as it already exists in the DB"
                )
                continue
            db_entry = centris_parser.to_db_model(scrape_date)
            db_entries.append(db_entry)
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
    return db_entries


def save_to_db(db_entries: list[PlexCentrisListingDB], existing_ids: set[int]) -> None:
    with Session.begin() as session:
        new_entries = [
            entry for entry in db_entries if entry.centris_id not in existing_ids
        ]

        if new_entries:
            logger.info(f"Saving {len(new_entries)} new listings to the DB")
            session.add_all(new_entries)


if __name__ == "__main__":
    scrape_date = datetime.now()
    existing_ids = get_existing_centris_ids()
    urls = get_urls(num_pages=2, headless=True)
    db_entries = scrape_content(urls, scrape_date, existing_ids)
    save_to_db(db_entries, existing_ids)
