import logging
from functools import lru_cache
from typing import Tuple

import attr
import requests

log = logging.getLogger(__name__)


@attr.s(hash=True)
class Client:
    __base_url__ = 'https://api.freshbooks.com'
    token = attr.ib(repr=False)

    @property
    def business_roles_identity(self) -> dict:
        endpoint = '/auth/api/v1/users/me'
        res = self._get(endpoint)
        return res['response']

    def list_clients(self, account_id: str, filters: dict=None) -> dict:
        endpoint = f"/accounting/account/{account_id}/users/clients"
        res = self._filtered_get_with_content_type(endpoint, filters)
        return res['response']['result']

    def list_projects(self, business_id: int, filters: dict=None) -> dict:
        endpoint = f"/projects/business/{business_id}/projects"
        return self._filtered_get(endpoint, filters)

    def fetch_time_entries(self, business_id: int, filters: dict=None) -> dict:
        endpoint = f"/timetracking/business/{business_id}/time_entries"
        return self._filtered_get(endpoint, filters)

    def create_time_entry(self, business_id: int, data: dict) -> dict:
        endpoint = f"/timetracking/business/{business_id}/time_entries"
        return self._post(endpoint, {'time_entry': data}, self.__headers__)

    def _get(
            self,
            endpoint: str,
            headers: dict=None,
            params: dict=None,
    ) -> dict:
        url, headers = self._prep_request(endpoint, headers)
        res = requests.get(url, headers=headers, params=params)
        log.debug(res.url)
        return res.json()

    def _post(
            self,
            endpoint: str,
            data: dict,
            headers: dict=None,
    ) -> dict:
        url, headers = self._prep_request(endpoint, headers)
        res = requests.post(url, headers=headers, json=data)
        log.debug(res.url)
        log.debug(res.request.body)
        return res.json()

    def _filtered_get(self, endpoint: str, filters: dict=None) -> dict:
        return self._get(endpoint, self.__headers__, filters)

    def _filtered_get_with_content_type(
            self,
            endpoint: str,
            filters: dict=None,
    ) -> dict:
        searches = None
        if filters:
            searches = {f"search[{k}]": v for k, v in filters.items()}
        return self._get(
            endpoint, self.__headers_with_content_type__, searches
        )

    def _prep_request(self, endpoint, headers) -> Tuple[str, dict]:
        if headers is None:
            headers = self.__headers_with_content_type__
        url = self.__base_url__ + endpoint
        return url, headers

    @property
    @lru_cache()
    def __headers__(self):
        return {
            'Authorization': f"Bearer {self.token}",
            'Api-Version': 'alpha',
        }

    @property
    @lru_cache()
    def __headers_with_content_type__(self):
        return {
            'Content-Type': 'application/json',
            **self.__headers__
        }
