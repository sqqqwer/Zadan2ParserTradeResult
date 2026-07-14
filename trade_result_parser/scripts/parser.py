import io
from abc import ABC, abstractmethod
from datetime import datetime

import pandas
from bs4 import BeautifulSoup


class Parser(ABC):
    @abstractmethod
    def parse(self):
        ...

class SpimexOilLinkHtmlParser(Parser):
    def __init__(self):
        super().__init__()

    def parse(self, html_text: str) -> tuple[str]:
        base_url = 'https://spimex.com'
        result_links = []

        beautiful_soup = BeautifulSoup(html_text, 'html.parser')
        a_tag_links = beautiful_soup.find_all(
            'a',
            href=True,
            class_='accordeon-inner__item-title'
        )

        for a_tag_link in a_tag_links:
            if 'pdf' in a_tag_link['class']:
                print(
                    'Ссылка на таблицу с датой '
                    + str(datetime.strptime(
                        a_tag_link.get("href")[33:41], "%Y%m%d"
                    ))[:10]
                    + ' имеет формат .pdf (ПРОПУЩЕНО)'
                )
            elif 'xls' in a_tag_link['class']:
                print(
                    'Ссылка на таблицу с датой '
                    + str(datetime.strptime(
                        a_tag_link.get("href")[37:45], "%Y%m%d"
                    ))[:10]
                    + ' получена'
                )
                result_links.append(base_url+a_tag_link.get('href'))

        return result_links

class SpimexOilXlsFileParser(Parser):
    def parse(self, table_content: bytes) -> tuple[dict]:
        df_raw = pandas.read_excel(
            io.BytesIO(table_content),
            engine='xlrd',
            header=None,
            dtype=str,
            keep_default_na=False
        )
        table_total_date: datetime = None
        result = []
        start_parse_flag = False
        exchange_product_id_length = 11

        for _idx, row in df_raw.iterrows():
            row_values = [str(val).strip() for val in row.values]
            if (not start_parse_flag):
                if (table_total_date is None and 'Дата торгов:' in row_values[1]):
                    table_total_date = datetime.strptime(
                        row_values[1][13:], '%d.%m.%Y'
                    )
                if ('Единица измерения: Метрическая тонна' in row_values[1]):
                    start_parse_flag = True
            else:
                current_table = dict()
                if (len(row_values[1]) == exchange_product_id_length):
                    current_table['exchange_product_id'] = row_values[1]
                    current_table['exchange_product_name'] = row_values[2]
                    current_table['delivery_basis_name'] = row_values[3]

                    current_table['volume'] = \
                    0 if row_values[4] == '-' else int(row_values[4])

                    current_table['total'] = \
                    0 if row_values[5] == '-' else int(row_values[5])

                    current_table['count'] = \
                    0 if row_values[12] == '-' else int(row_values[12])

                    current_table['date'] = table_total_date

                    result.append(current_table)

        return result
