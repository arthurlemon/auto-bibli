from datetime import datetime
from centris.backend.centris_scraper import CentrisBienParser, CentrisScraper
from centris.backend.db_models import PlexCentrisListingDB
from centris import Session
from loguru import logger
from tqdm import tqdm
from pathlib import Path


def get_existing_centris_ids(session) -> set[int]:
    existing_ids = {
        id_[0] for id_ in session.query(PlexCentrisListingDB.centris_id).all()
    }
    return existing_ids


# TODO - Add stopping criteria based on existing_ids: if among the URL of a given page, at least 1 is in the DB, we stop (because listings are sorted by date)
def get_urls_from_web(scrape_date: datetime, **kwargs) -> list[str]:
    scraper = CentrisScraper()
    urls = scraper.scrape_urls(**kwargs)
    # Store the URLs in a file
    Path(f"artifacts/{scrape_date.strftime('%Y-%m-%d_%H-%M-%S')}").mkdir(
        parents=True, exist_ok=True
    )
    with open(
        f"artifacts/{scrape_date.strftime('%Y-%m-%d_%H-%M-%S')}/urls.txt", "w"
    ) as f:
        f.write("\n".join(urls))
    return urls


def get_urls_from_file(scrape_time: str, **kwargs) -> list[str]:
    with open(f"artifacts/{scrape_time}/urls.txt", "r") as f:
        urls = f.read().splitlines()
    return urls


def scrape_and_save(
    urls: list[str], scrape_date: datetime, existing_ids: set[int], session
) -> None:
    for url in tqdm(urls, desc="Scraping and saving listings"):
        try:
            centris_parser = CentrisBienParser(url)
            if centris_parser.centris_id in existing_ids:
                logger.info(f"Skipping {centris_parser.centris_id}")
                continue

            db_entry = centris_parser.to_db_model(scrape_date)
            session.add(db_entry)
            session.commit()
            existing_ids.add(centris_parser.centris_id)

        except Exception as e:
            logger.error(f"Error storing {url}: {e}")
            session.rollback()
            continue


if __name__ == "__main__":
    scrape_date = datetime.now()
    scrape_urls = False
    with Session() as session:
        existing_ids = get_existing_centris_ids(session)
        if scrape_urls:
            urls = get_urls_from_web(scrape_date, num_pages=60, headless=True)
        else:
            urls = get_urls_from_file("2025-01-04_09-52-56")
        scrape_and_save(urls, scrape_date, existing_ids, session)
