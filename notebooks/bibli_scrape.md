---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: .venv
    language: python
    name: python3
---

```python
import sys
sys.path.append("../")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
```

```python
def set_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                            options=options)
    driver.implicitly_wait(2)
    return driver

def fill_select_field(driver, field_id, value):
    """Fill a select field with the given value."""
    select = Select(driver.find_element(By.ID, field_id))
    select.select_by_value(value)

def fill_text_field(driver, field_id, value):
    """Fill a text input field with the given value."""
    input_field = driver.find_element(By.ID, field_id)
    input_field.send_keys(value)

def search_library_catalog(driver, search_url, title):
    """Perform a search in the library catalog with the given parameters."""
    driver.get(search_url)

    # Configure search fields
    fill_select_field(driver, 'searchType_0', 't:')
    fill_text_field(driver, 'searchTerm_0', title)

    # Configure filters
    fill_select_field(driver, "limitValue_0", "-") # Format: "Livre"
    fill_select_field(driver, "limitValue_1", "55") # Collection: "Adultes"
    fill_select_field(driver, "limitValue_2", "x33a") # Location: "LE PRÉVOST - Adultes"
    fill_select_field(driver, "limitValue_3", "eng") # Language: "Anglais"
    add_limit_button = driver.find_element(By.CLASS_NAME, 'addLimitButton')
    add_limit_button.click()
    fill_select_field(driver, "limitValue_4", "fre") # Language: "Français"

    # Submit search
    driver.find_element(By.ID, 'searchSubmit').click()
    
    return driver.current_url
```

```python
driver = set_driver()

# Execute search
BASE_URL = "https://nelligandecouverte.ville.montreal.qc.ca/iii/encore"
SEARCH_URL = f"{BASE_URL}/home?lang=frc&suite=cobalt&advancedSearch=true&searchString="

relevant_title = "The Wake"
result_url = search_library_catalog(driver, SEARCH_URL, relevant_title)
print("Search Result URL:", result_url)

driver.quit()
```

```python
driver.page_source
```

```python
previous_searches = {}
```

```python

```
