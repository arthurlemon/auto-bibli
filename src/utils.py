import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


# Function to search for a book
def search_book(title, library, previous_searches):
    base_url = "https://nelligandecouverte.ville.montreal.qc.ca/iii/encore/home?lang=frc&suite=cobalt&advancedSearch=true&searchString="
    search_url = base_url.format(title.replace(" ", "%20"))

    # Use Requests to get the search result page
    response = requests.get(search_url)
    if response.status_code != 200:
        print("Error fetching the search page.")
        return

    # Parse the search result page
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.find_all("a", class_="dpbibTitle")

    # If there are multiple titles, display them to the user
    if len(titles) > 1:
        print("Multiple titles found:")
        for i, title_tag in enumerate(titles):
            print(f"{i + 1}. {title_tag.text.strip()}")

        # Ask user to pick a title
        selected_index = int(input("Select the correct title number: ")) - 1
        selected_url = (
            "https://nelligandecouverte.ville.montreal.qc.ca"
            + titles[selected_index]["href"]
        )
    elif len(titles) == 1:
        selected_url = (
            "https://nelligandecouverte.ville.montreal.qc.ca" + titles[0]["href"]
        )
    else:
        print("No titles found.")
        return

    # Store the selected URL for future searches
    previous_searches[title] = selected_url

    # Go to the selected book's page
    check_availability(selected_url, library)


# Function to check the availability of the book
def check_availability(book_url, library):
    # Use Selenium to navigate to the book's detail page
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(Service(ChromeDriverManager().install())),
        options=chrome_options,
    )
    driver.get(book_url)

    time.sleep(2)  # Allow time for the page to load

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find the table that contains availability info
    table = soup.find("table", class_="bibItems")
    if not table:
        print("Availability information not found.")
        driver.quit()
        return

    # Extract rows from the table
    rows = table.find_all("tr")
    found = False
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 3:
            branch = columns[0].text.strip()
            status = columns[2].text.strip()

            # Check if the branch matches the user's library of interest
            if library.lower() in branch.lower():
                print(f"Library: {branch}, Status: {status}")
                found = True
                break

    if not found:
        print(f"The book is not available at {library}.")

    driver.quit()
