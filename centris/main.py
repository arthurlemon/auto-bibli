from datetime import datetime
from centris.centris_scraper import CentrisBienParser, CentrisScraper
from centris import Session


def get_urls(num_pages=2):
    scraper = CentrisScraper()
    urls = scraper.scrape_urls(headless=False, num_pages=num_pages)
    return urls


def scrape(urls):
    db_entries = []
    for url in urls:
        centris_parser = CentrisBienParser(url)
        db_entry = centris_parser.to_db_model(scrape_date)
        db_entries.append(db_entry)
    return db_entries


def save_to_db(db_entries):
    with Session.begin() as session:
        session.add_all(db_entries)


if __name__ == "__main__":
    scrape_date = datetime.now()
    urls = get_urls(num_pages=3)
    db_entries = scrape(urls)
    save_to_db(db_entries)
