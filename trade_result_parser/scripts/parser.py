import io
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Generic, TypeVar

import pandas
from bs4 import BeautifulSoup
from typing_extensions import override

Parse_parse_input_type = TypeVar("Parse_parse_input_type")
Parse_parse_output_type = TypeVar("Parse_parse_output_type")

logger = logging.getLogger(__name__)


class Parser(ABC, Generic[Parse_parse_input_type, Parse_parse_output_type]):
    @abstractmethod
    def parse(self, source: Parse_parse_input_type) -> Parse_parse_output_type: ...


class SpimexOilLinkHtmlParser(Parser[str, list[str]]):
    def __init__(self):
        super().__init__()

    @override
    def parse(self, html_text: str) -> list[str]:
        base_url = "https://spimex.com"
        result_links: list[str] = []

        beautiful_soup = BeautifulSoup(html_text, "html.parser")
        a_tag_links = beautiful_soup.find_all(
            "a", href=True, class_="accordeon-inner__item-title"
        )

        for a_tag_link in a_tag_links:
            href = a_tag_link.get("href")
            if not isinstance(href, str):
                continue

            if "pdf" in a_tag_link["class"]:
                logger.info(
                    "Ссылка на таблицу с датой "
                    + str(datetime.strptime(href[33:41], "%Y%m%d"))[:10]
                    + " имеет формат .pdf (ПРОПУЩЕНО)"
                )
            elif "xls" in a_tag_link["class"]:
                logger.info(
                    "Ссылка на таблицу с датой "
                    + str(datetime.strptime(href[37:45], "%Y%m%d"))[:10]
                    + " получена"
                )
                result_links.append(base_url + href)

        return result_links


class SpimexOilXlsFileParser(
    Parser[bytes, list[dict[str, str | int | Decimal | datetime]]]
):
    def _parse_decimal(self, value: str) -> Decimal:
        value = value.strip().replace(" ", "")
        if value == "-":
            return Decimal("0")
        value = value.replace(",", ".")

        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise ValueError(f"Некорректное значение для Decimal: {value}") from error

    @override
    def parse(
        self, table_content: bytes
    ) -> list[dict[str, str | int | Decimal | datetime]]:
        df_raw = pandas.read_excel(
            io.BytesIO(table_content),
            engine="xlrd",
            header=None,
            dtype=str,
            keep_default_na=False,
        )
        table_total_date: datetime | None = None
        result: list[dict[str, str | int | Decimal | datetime]] = []
        start_parse_flag = False
        exchange_product_id_length = 11

        for _idx, row in df_raw.iterrows():
            row_values = [str(val).strip() for val in row.values]
            if not start_parse_flag:
                if table_total_date is None and "Дата торгов:" in row_values[1]:
                    table_total_date = datetime.strptime(row_values[1][13:], "%d.%m.%Y")
                if "Единица измерения: Метрическая тонна" in row_values[1]:
                    start_parse_flag = True
            else:
                current_table: dict[str, str | int | Decimal | datetime] = dict()
                if len(row_values[1]) == exchange_product_id_length:
                    current_table["exchange_product_id"] = row_values[1]
                    current_table["exchange_product_name"] = row_values[2]
                    current_table["delivery_basis_name"] = row_values[3]

                    current_table["volume"] = self._parse_decimal(row_values[4])
                    current_table["total"] = self._parse_decimal(row_values[5])

                    current_table["count"] = (
                        0 if row_values[12] == "-" else int(row_values[12])
                    )

                    if table_total_date is not None:
                        current_table["date"] = table_total_date
                    else:
                        continue

                    result.append(current_table)

        return result
