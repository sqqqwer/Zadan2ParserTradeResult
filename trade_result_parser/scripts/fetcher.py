import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

import requests
from fake_useragent import UserAgent
from typing_extensions import override

Fetcher_configure_input_type = TypeVar("Fetcher_configure_input_type")


class Fetcher(ABC, Generic[Fetcher_configure_input_type]):
    def __init__(self, session: requests.Session):
        self.user_agent = UserAgent()
        self.current_url: str

        self.request_session = session
        self.request_session.headers.update(self._generate_header())

        self.failed_url: set = set()

    def fetch(self, max_retries=3) -> Iterator[requests.Response | None]:
        for response in self._fetch_generator(max_retries=max_retries):
            if response is None:
                self.failed_url.add(self.current_url)
            yield response

    @abstractmethod
    def configure(self, config: Fetcher_configure_input_type) -> None: ...

    @abstractmethod
    def _fetch_generator(
        self, max_retries: int
    ) -> Iterator[requests.Response | None]: ...

    @abstractmethod
    def _get_class_logger_label(self) -> str:
        return f"Fetcher{0} "

    def print_failed_urls(self) -> None:
        failed_urls_count = len(self.failed_url)

        if failed_urls_count > 0:
            print(f"Не обработано {failed_urls_count} ссылок:")
            for url in self.failed_url:
                print(url)

    def _fetch_one_url(self, url: str, max_retries: int) -> requests.Response | None:
        for current_try in range(1, max_retries + 1):
            try:
                time.sleep(1)
                response = self.request_session.get(
                    url=url,
                    timeout=15,
                )
                response.raise_for_status()
                return response
            except (requests.ConnectionError, requests.Timeout) as exception:
                wait_time = 3 * current_try
                print(
                    self._get_class_logger_label() + f"Исключение: {exception}, "
                    f"Попытка:{current_try}/{max_retries} ждем {wait_time}с"
                )
                time.sleep(wait_time)
            except requests.HTTPError:
                if response.status_code in (404,):
                    print(
                        self._get_class_logger_label()
                        + f"Сервер вернул {response.status_code}, Пропускаем файл"
                    )
                    return None
                elif response.status_code in (429, 502, 503, 504):
                    wait_time = 3 * current_try
                    print(
                        self._get_class_logger_label()
                        + f"Сервер вернул {response.status_code}, "
                        f"Попытка:{current_try}/{max_retries} ждем {wait_time}с"
                    )
                    time.sleep(wait_time)
                else:
                    print(
                        self._get_class_logger_label()
                        + f"Cервер вернул {response.status_code}, Пропускаем файл"
                    )
                    print(url)
                    return None
            except Exception as exception:
                print(
                    self._get_class_logger_label()
                    + f"Неизвестное исключение: {exception}, Пропускаем файл"
                )
                return None
        print(self._get_class_logger_label() + "Исчерпаны все попытки, Пропускаем файл")
        return None

    def _generate_header(self) -> dict:
        header = {
            "user-agent": self.user_agent.random,
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "sec-ch-ua-platform": "Windows",
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            ),
            "upgrade-insecure-requests": "1",
        }
        return header


@dataclass(frozen=True)
class SpimexOilHtmlPageFetcherConfig:
    fetch_pages_start: int
    fetch_pages_end: int


class SpimexOilHtmlPageFetcher(Fetcher[SpimexOilHtmlPageFetcherConfig]):
    def __init__(self, session: requests.Session):
        super().__init__(session=session)
        self.fetch_pages_start = 1
        self.fetch_pages_end = 90

    @override
    def configure(self, config: SpimexOilHtmlPageFetcherConfig) -> None:
        self.fetch_pages_start = config.fetch_pages_start
        self.fetch_pages_end = config.fetch_pages_end

    @override
    def _fetch_generator(self, max_retries=3) -> Iterator[requests.Response | None]:
        for page in range(self.fetch_pages_start, self.fetch_pages_end + 1):
            self.current_url = (
                "https://spimex.com/markets/oil_products/trades/"
                f"results/?page=page-{page}"
                "&bxajaxid=d609bce6ada86eff0b6f7e49e6bae904"
            )
            yield self._fetch_one_url(url=self.current_url, max_retries=max_retries)

    @override
    def _get_class_logger_label(self) -> str:
        return f"Страница {self.current_url}"


class SpimexOilTableFetcher(Fetcher[list[str]]):
    def __init__(self, session: requests.Session):
        super().__init__(session=session)
        self.list_table_links: list = []

    @override
    def configure(self, list_table_links: list[str]) -> None:
        self.list_table_links = list_table_links

    @override
    def _fetch_generator(self, max_retries=3) -> Iterator[requests.Response | None]:
        for url in self.list_table_links:
            self.current_url = url
            yield self._fetch_one_url(url, max_retries)

    @override
    def _get_class_logger_label(self) -> str:
        return f"Таблица с ссылкой {self.current_url}"
