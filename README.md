# Caltech Scraper

A command line tool that displays course information from the Caltech Catalog.
In no way is this project affiliated or endorsed by the California Institute
of Technology.

## Setup

### Install Dependencies

```bash
$ pip3 install -r requirements.txt
```

### Environment Variables

The project uses MySQL to set up the database. The following environment
variables are placed in a `.env` file to connect to the database:

```text
HOST=
USER=
PASSWORD=
DATABASE_NAME=
```

## How to Use

### Scrape the Caltech Catalog

```bash
$ python3 scrape.py
```

### Search Database

```bash
$ python3 caltech-scraper.py
```

## Sources

- Beautiful Soup Documentation: <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>
- MySQL Connector Documentation: <https://dev.mysql.com/doc/connector-python/en/>
- Argparse Documentation: <https://docs.python.org/3/library/argparse.html>
