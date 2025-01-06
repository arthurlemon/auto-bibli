from thinkerview.backend.think_scraper import scrape_page
from thinkerview.backend.database import open_connection, close_connection


def main():
    conn = open_connection()
    base_url = "https://www.thinkerview.com/"
    next_url = base_url

    while next_url:
        print(f"Scraping: {next_url}")
        next_url = scrape_page(next_url, conn)

    close_connection(conn)


if __name__ == "__main__":
    main()
