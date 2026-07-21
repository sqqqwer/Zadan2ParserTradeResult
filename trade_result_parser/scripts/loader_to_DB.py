from abc import ABC, abstractmethod

from sqlalchemy.orm.session import Session as sqlalchemy_session_type
from typing_extensions import override

from trade_result_parser.models.bulletin import Bulletin


class LoaderToDB(ABC):
    @abstractmethod
    def load_model_item(self, info: dict, session: sqlalchemy_session_type): ...


class BulletinLoaderToDB(LoaderToDB):
    @override
    def load_model_item(self, info: dict, session: sqlalchemy_session_type):
        new_bulletin = Bulletin(
            exchange_product_id=info["exchange_product_id"],
            exchange_product_name=info["exchange_product_name"],
            oil_id=info["exchange_product_id"][:4],
            delivery_basis_id=info["exchange_product_id"][4:7],
            delivery_basis_name=info["delivery_basis_name"],
            delivery_type_id=info["exchange_product_id"][-1],
            volume=info["volume"],
            total=info["total"],
            count=info["count"],
            date=info["date"],
        )
        session.add(new_bulletin)
