import requests

from .fetcher import SpimexOilHtmlPageFetcher, SpimexOilTableFetcher
from .loader_to_DB import BulletinLoaderToDB
from .orchestrator import SpimexOilBulletinOrchestrator
from .parser import SpimexOilLinkHtmlParser, SpimexOilXlsFileParser


def parse_spimex_oil_bulletin_all():
    request_session = requests.Session()

    orchestrator = SpimexOilBulletinOrchestrator(
        fetcher_links_html=SpimexOilHtmlPageFetcher(request_session),
        fetcher_table_xls=SpimexOilTableFetcher(request_session),
        page_parser_html=SpimexOilLinkHtmlParser(),
        table_parser_xls=SpimexOilXlsFileParser(),
        loader_to_db=BulletinLoaderToDB(),
    )
    orchestrator.start_parse(
        start_pages=1,
        end_pages=100,
    )


def parse_spimex_oil_bulletin_two_pages():
    request_session = requests.Session()

    orchestrator = SpimexOilBulletinOrchestrator(
        fetcher_links_html=SpimexOilHtmlPageFetcher(request_session),
        fetcher_table_xls=SpimexOilTableFetcher(request_session),
        page_parser_html=SpimexOilLinkHtmlParser(),
        table_parser_xls=SpimexOilXlsFileParser(),
        loader_to_db=BulletinLoaderToDB(),
    )
    orchestrator.start_parse(
        start_pages=50,
        end_pages=51,
    )
