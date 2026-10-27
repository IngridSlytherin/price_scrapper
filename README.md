# Smartphone Trade-in Price Scraper

A Python automation that collects trade-in quotes for used smartphones from an online trade-in site and loads them into a MySQL database for price tracking.

## How it works

1. **Scraping** (`doji_scraper.py`): a headless Chrome session driven by Selenium walks through the site's quote flow for each phone model. It picks the storage capacity, answers the condition questionnaire and reads the final offer.
2. **Three condition scenarios** per model: perfect condition, one problem and all problems, so the dataset shows how condition affects the price.
3. **Local storage**: every quote is appended to `preco_temp.json` with brand, model, condition, price, source and collection timestamp.
4. **Database load** (`inserir_banco.py`): reads the JSON file and inserts the records into a MySQL table (`precos_celulares_doji`).

The model list (`dispositivos.txt`) covers about 100 Samsung and Apple devices.

## Stack

Python · Selenium (headless Chrome) · webdriver-manager · MySQL (mysqlclient)

## Running locally

```bash
pip install selenium webdriver-manager mysqlclient
python doji_scraper.py      # collects quotes into preco_temp.json
python inserir_banco.py     # loads them into MySQL
```

Before loading, fill in the database connection settings in `DB_CONFIG` inside `inserir_banco.py`. Credentials are intentionally not stored in the repository.

---

Built by [Ingrid Padilha](https://www.linkedin.com/in/ingrid-padilha/).
