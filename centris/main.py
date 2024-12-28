from datetime import datetime
from centris.centris_scraper import CentrisBienParser
from centris import Session

scrape_date = datetime.now()


def get_urls():
    # getting URL to scrapes
    urls = [
        "https://www.centris.ca/fr/triplex~a-vendre~montreal-ahuntsic-cartierville/19418151?view=Summary"
    ]
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
