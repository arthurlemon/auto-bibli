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
%load_ext autoreload
%autoreload 2

from datetime import datetime
from src.models import CentrisUrl, BienCentrisDuplex, CustomDateFormat
from src.centris_scraper import CentrisBienParser, CentrisScraper
```

```python
plex_start_url="https://www.centris.ca/fr/plex~a-vendre~montreal?view=Thumbnail&uc=1"
url_bien_centris = "https://www.centris.ca/fr/triplex~a-vendre~montreal-mercier-hochelaga-maisonneuve/9094837?view=Summary"
```

```python
centris_parser = CentrisBienParser(url_bien_centris)
```

```python
print("DESCRIPTION\n------\n")
print(f"Centris ID: {centris_parser.centris_id }")
print(f"{centris_parser.title} - Utilisation {centris_parser.utilisation} - {centris_parser.style_batiment}")
print(f"Description: {centris_parser.description}")
print(f"Année de construction: {centris_parser.annee_construction}")
print(f"Superficie:\n-terrain: {centris_parser.superficie_terrain} (pc)\
      \n-batiment: {centris_parser.superficie_batiment} (pc)\
        \n-habitable: {centris_parser.superficie_habitable}(pc)\
        \n-commerce: {centris_parser.superficie_commerce} (pc)")
print(f"Unités: {centris_parser.unites} ({centris_parser.nombre_unites})")
print(f"Stationnement: {centris_parser.stationnement}")
print(f"Autres charactéristiques: {centris_parser.additional_characteristics}")

print("\nLOCALISATION\n------\n")
print(f"Addresse: {centris_parser.addresse}")
print(f"Ville: {centris_parser.ville}")
print(f"Quartier: {centris_parser.quartier}")

print("\nPORTRAIT FINANCIER\n------\n")
print(f"Prix: {centris_parser.prix}")
print(f"Prix au pc: {centris_parser.prix/centris_parser.superficie_terrain}")
print(f"Revenus: {centris_parser.revenus}")
print(f"Taxes: {centris_parser.total_taxes}")
print(f"Evaluation municipale: {centris_parser.eval_municipale}")

```

```python
centris_parser.eval_municipale
```

```python
bien_centris = BienCentrisDuplex(\
    url= CentrisUrl(url=centris_parser.url),
    centris_id = centris_parser.centris_id,
    title = centris_parser.title,
    annee_construction = centris_parser.annee_construction,
    description = centris_parser.description,
    unites = centris_parser.unites,
    nombre_unites = centris_parser.nombre_unites,
    superficie_habitable = centris_parser.superficie_habitable,
    superficie_batiment = centris_parser.superficie_batiment,
    superficie_commerce = centris_parser.superficie_commerce,
    superficie_terrain = centris_parser.superficie_terrain,
    stationnement=centris_parser.stationnement,
    utilisation = centris_parser.utilisation,
    adresse = centris_parser.addresse,
    ville = centris_parser.ville,
    quartier = centris_parser.quartier,
    prix=centris_parser.prix,
    revenus=centris_parser.revenus,
    taxes= centris_parser.total_taxes,
    eval_municipale=centris_parser.eval_municipale,
    date_scrape = CustomDateFormat(date="2024-01-10"))
```

```python
bien_centris
```

```python
from playwright.sync_api import sync_playwright
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page()
page.goto("https://www.centris.ca/fr/plex~a-vendre~montreal?view=Thumbnail")
page.cl(path="example.png")
browser.close()
playwright.stop()
```
