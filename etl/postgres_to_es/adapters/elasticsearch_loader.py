import json
import logging

import requests
from config import ElasticParams
from models import dto


class ElasticsearchLoader:
    """Этот класс забирает данные в подготовленном формате и загружает их в Elasticsearch."""

    def __init__(self, params: ElasticParams, session: requests.Session):
        self.config = params
        self.url = f"http://{params.host}:{params.port}"
        self.session: requests.Session = session
        self.log = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def prepare_bulk_request_data(batch: list[dto.Filmwork]) -> str:
        """Метод генерации тела запроса из переданных данных."""
        bulk_request_data = ""
        for document in batch:
            bulk_request_data += json.dumps({"index": {"_id": document.id}}) + "\n"
            bulk_request_data += json.dumps(document.model_dump()) + "\n"

        return bulk_request_data

    def send_request(
        self,
        index_name: str,
        bulk_request_data: str,
    ) -> requests.Response:
        """Метод для отправки данных в Elasticsearch по REST API."""
        response = self.session.post(
            url=f"{self.url}/{index_name}/_bulk",
            data=bulk_request_data,
            headers={"Content-Type": "application/json"},
        )
        return response

    def save_batch(self, index_name: str, batch: list[dto.Filmwork]) -> None:
        """Основной метод сохранения данных в Elasticsearch."""
        bulk_request_data = self.prepare_bulk_request_data(batch=batch)
        self.send_request(bulk_request_data=bulk_request_data, index_name=index_name)

        self.log.info(f"{len(batch)} rows saved successfully!")
