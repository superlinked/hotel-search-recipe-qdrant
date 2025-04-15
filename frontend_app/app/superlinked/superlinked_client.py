import requests
from typing import Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SuperlinkedClient:
    def __init__(self, host: str | None = None, port: int | None = None):
        if host is None:
            host = settings.server.api_host
        if port is None:
            port = settings.server.api_port
        self.base_url = f"http://{host}:{port}"
        self.headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "x-include-metadata": "true",
        }

    def ingest(self, schema_name: str, data: dict[str, Any]):
        url = f"{self.base_url}/api/v1/ingest/{schema_name}"
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code != 202:
            response.raise_for_status()

    def query(self, query_name: str, data: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/search/{query_name}"
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    def get_data_loaders(self) -> list[str]:
        url = f"{self.base_url}/data-loader"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            response.raise_for_status()
        result = list(response.json()["result"].keys())
        return result

    def run_data_loader(self, name: str):
        url = f"{self.base_url}/data-loader/{name}/run"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 409:
            response_json = response.json()
            info = response_json["result"]
            assert info.startswith("Data load already running"), info
            logger.warning(f"Data loader with name {name} already running")
            return response_json

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()
