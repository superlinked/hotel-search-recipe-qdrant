import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_ENV_FILENAME = ".env"


class Settings(BaseSettings):
    text_embedder_name: str = "sentence-transformers/all-mpnet-base-v2"
    chunk_size: int = 10
    path_categories: str = (
        "https://storage.googleapis.com/superlinked-recipes-data/hotels-search/categories/categories.json"
    )
    path_dataset: str = (
        "https://storage.googleapis.com/superlinked-recipes-data/hotels-search/dataset/dataset.jsonl"
    )
    openai_model: str = "gpt-4o"
    openai_api_key: SecretStr
    qdrant_url: str = "https://582c83bf-e97f-401a-9ff7-8480522f5e88.europe-west3-0.gcp.cloud.qdrant.io"
    qdrant_api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.0hEkwzpfBRRQxXnDky4G0Hiuou6yfnWmvATWODEnVnM"
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILENAME, env_file_encoding="utf-8"
    )


def get_env_file_path() -> str:
    dirname = os.path.dirname(__file__)
    rel_path = os.path.join(dirname, DEFAULT_ENV_FILENAME)
    abs_path = os.path.abspath(rel_path)
    return abs_path


settings = Settings(_env_file=get_env_file_path())
