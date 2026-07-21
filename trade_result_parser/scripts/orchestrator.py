from datetime import datetime

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from trade_result_parser.core.database import Session as DBSession_factory

from .fetcher import (
    SpimexOilHtmlPageFetcher,
    SpimexOilHtmlPageFetcherConfig,
    SpimexOilTableFetcher,
)
from .loader_to_DB import BulletinLoaderToDB
from .parser import SpimexOilLinkHtmlParser, SpimexOilXlsFileParser


class SpimexOilBulletinOrchestrator:
    def __init__(
        self,
        fetcher_links_html: SpimexOilHtmlPageFetcher,
        fetcher_table_xls: SpimexOilTableFetcher,
        page_parser_html: SpimexOilLinkHtmlParser,
        table_parser_xls: SpimexOilXlsFileParser,
        loader_to_db: BulletinLoaderToDB,
    ):
        self.fetcher_links_html = fetcher_links_html
        self.fetcher_table_xls = fetcher_table_xls
        self.page_parser_html = page_parser_html
        self.table_parser_xls = table_parser_xls
        self.loader_to_db = loader_to_db

    def start_parse(self, start_pages=88, end_pages=89):
        self.fetcher_links_html.configure(
            SpimexOilHtmlPageFetcherConfig(
                fetch_pages_start=start_pages, fetch_pages_end=end_pages
            )
        )
        for page_response in self.fetcher_links_html.fetch():
            if page_response is None:
                continue

            page_links = self.page_parser_html.parse(page_response.text)

            self.fetcher_table_xls.configure(list_table_links=page_links)
            for table_xls_response in self.fetcher_table_xls.fetch():
                try:
                    with DBSession_factory() as session, session.begin():
                        if table_xls_response is None:
                            continue

                        parsed_xls_tables = self.table_parser_xls.parse(
                            table_xls_response.content
                        )
                        if len(parsed_xls_tables) == 0:
                            continue

                        if parsed_xls_tables[0]["date"] < datetime(
                            year=2023, month=1, day=1
                        ):
                            print("ТАБЛИЦА РАНЬШЕ 2023 ГОДА, парсинг останавливается")
                            break

                        print(
                            f"Таблица с датой {str(parsed_xls_tables[0]['date'])[:10]} "
                            "Скачана и распаршена"
                        )

                        for parsed_xls_table in parsed_xls_tables:
                            if parsed_xls_table["count"] <= 0:
                                continue
                            self.loader_to_db.load_model_item(parsed_xls_table, session)
                except IntegrityError as exception:
                    if isinstance(exception.orig, UniqueViolation):
                        print(
                            f"Таблица с датой {str(parsed_xls_tables[0]['date'])[:10]} "
                            "УЖЕ СУЩЕСТВУЕТ в базе данных"
                        )
                else:
                    print(
                        f"Таблица с датой {str(parsed_xls_tables[0]['date'])[:10]} "
                        "СОХРАНЕНА в базе данных"
                    )
            else:
                continue
            break

        print(f"Парсинг страниц {start_pages}-{end_pages} завершён")
        self.fetcher_links_html.print_failed_urls()
        self.fetcher_table_xls.print_failed_urls()
