import json
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel
from gpustack.api.exceptions import raise_if_response_error
from gpustack.server.bus import Event
from gpustack.schemas import *

from .generated_http_client import HTTPClient


class ModelInstanceClient:

    def __init__(self, client: HTTPClient):
        self._client = client
        self._url = f"{client._base_url}/v1/model_instances"

    def list(self, params: Dict[str, Any] = None) -> ModelInstancesPublic:
        response = self._client.get_httpx_client().get(self._url, params=params)
        raise_if_response_error(response)

        return ModelInstancesPublic.model_validate(response.json())

    def watch(
        self,
        callback: Callable[[Event], None],
        params: Optional[Dict[str, Any]] = None,
    ):
        if params is None:
            params = {}
        params["watch"] = "true"

        with self._client.get_httpx_client().stream(
            "GET", self._url, params=params, timeout=None
        ) as response:
            raise_if_response_error(response)
            for line in response.iter_lines():
                if line:
                    event_data = json.loads(line)
                    event = Event(**event_data)
                    callback(event)

    def get(self, id: int) -> ModelInstancePublic:
        response = self._client.get_httpx_client().get(f"{self._url}/{id}")
        raise_if_response_error(response)
        return ModelInstancePublic.model_validate(response.json())

    def create(self, model_create: ModelInstanceCreate):
        response = self._client.get_httpx_client().post(
            self._url, json=model_create.model_dump()
        )
        raise_if_response_error(response)
        return ModelInstancePublic.model_validate(response.json())

    def update(self, id: int, model_update: ModelInstanceUpdate):
        response = self._client.get_httpx_client().put(
            f"{self._url}/{id}", json=model_update.model_dump()
        )
        raise_if_response_error(response)
        return ModelInstancePublic.model_validate(response.json())

    def delete(self, id: int):
        response = self._client.get_httpx_client().delete(f"{self._url}/{id}")
        raise_if_response_error(response)
