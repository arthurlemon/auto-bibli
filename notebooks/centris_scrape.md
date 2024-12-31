---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: .venv
    language: python
    name: python3
---

```python
%load_ext autoreload
%autoreload 2

from datetime import datetime
from centris.centris_scraper import CentrisBienParser, AsyncCentrisScraper
from centris.db_models import PlexCentrisListingDB
from centris import Session
from sqlalchemy.sql import select

from pprint import pprint
```

### Scraping 1 listing

```python
plex_start_url="https://www.centris.ca/fr/plex~a-vendre~montreal?view=Thumbnail&uc=1"
url_bien_centris = "https://www.centris.ca/fr/triplex~a-vendre~montreal-ahuntsic-cartierville/19418151?view=Summary"
```

```python
centris_parser = CentrisBienParser(url_bien_centris)
```

```python
scrape_date=datetime.now()
data = centris_parser.get_data(scrape_date)
```

```python
pprint(data.model_dump())

```

saving to DB

```python
db_entry = centris_parser.to_db_model(scrape_date)
with Session.begin() as session:
    session.add_all(
        [
            db_entry
        ]
    )
```

```python
# Query the database for testing
stmt = select(PlexCentrisListingDB)
objects = session.scalars(stmt).all()
```

```python
objects[0].__dict__
```

```python
with Session.begin() as session:
    # Get existing IDs
    existing_ids = {
        id_[0] for id_ in
        session.query(PlexCentrisListingDB.centris_id).all()
    }
```

```python
print(existing_ids)
```

```python
from centris.main import get_existing_centris_ids
existing_ids = get_existing_centris_ids()
```

```python
for el in existing_ids:
    print(el)
    break
```

```python
all_urls = ['https://www.centris.ca/fr/duplex~a-vendre~montreal-ahuntsic-cartierville/11493867?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-cote-des-neiges-notre-dame-de-grace/21712528?view=Summary', 'https://www.centris.ca/fr/quadruplex~a-vendre~montreal-lachine/23406148?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-mercier-hochelaga-maisonneuve/26336120?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-ahuntsic-cartierville/28623760?view=Summary', 'https://www.centris.ca/fr/quadruplex~a-vendre~montreal-l-ile-bizard-sainte-genevieve/19847268?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-ville-marie/11160801?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-riviere-des-prairies-pointe-aux-trembles/18705723?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-mercier-hochelaga-maisonneuve/21586957?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-mercier-hochelaga-maisonneuve/14317746?view=Summary', 'https://www.centris.ca/fr/quadruplex~a-vendre~montreal-villeray-saint-michel-parc-extension/11141292?view=Summary', 'https://www.centris.ca/fr/quintuplex~a-vendre~montreal-le-sud-ouest/16008600?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-saint-laurent/10360074?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-ville-marie/9757519?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-lachine/10149723?view=Summary', 'https://www.centris.ca/fr/quadruplex~a-vendre~montreal-le-plateau-mont-royal/15742000?view=Summary', 'https://www.centris.ca/fr/quadruplex~a-vendre~montreal-riviere-des-prairies-pointe-aux-trembles/19866722?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-verdun-ile-des-soeurs/24411293?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-cote-des-neiges-notre-dame-de-grace/25881718?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-rosemont-la-petite-patrie/14415173?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-riviere-des-prairies-pointe-aux-trembles/12881479?view=Summary', 'https://www.centris.ca/fr/triplex~a-vendre~montreal-ville-marie/19584463?view=Summary', 'https://www.centris.ca/fr/duplex~a-vendre~montreal-ahuntsic-cartierville/22353235?view=Summary', 'https://www.centris.ca/fr/quadruplex~a-vendre~montreal-ahuntsic-cartierville/16027183?view=Summary']
```

```python
from tqdm import tqdm
from centris.centris_scraper import CentrisBienParser
```

```python
for url in tqdm(all_urls, desc="Scraping content of each listing URL"):
    centris_parser = CentrisBienParser(url)
    print(centris_parser.centris_id)
    if centris_parser.centris_id in existing_ids:
        print(f"Skipping {centris_parser.centris_id} as it already exists in the DB")
        continue
    db_entry = centris_parser.to_db_model(scrape_date)
```

```python

```
