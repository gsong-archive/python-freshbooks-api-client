import logging
from functools import lru_cache

import attr
import requests

log = logging.getLogger(__name__)

BASE_URL = 'https://api.freshbooks.com'
HEADERS = {
    'Authorization': 'Bearer <Bearer Token>',
    'Api-Version': 'alpha',
    'Content-Type': 'application/json'
}


@attr.s(hash=True)
class Client:
    __base_url__ = 'https://api.freshbooks.com'
    __headers__ = attr.ib(init=False, repr=False, hash=False)

    token = attr.ib(repr=False)

    def __attrs_post_init__(self):
        self.__headers__ = {
            'Authorization': f"Bearer {self.token}",
            'Api-Version': 'alpha',
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"{self.__base_url__}{endpoint}"
        res = requests.get(url, headers=self.__headers__, params=params)
        log.debug(res.url)
        return res.json()['response']['result']

    @property
    @lru_cache()
    def business_roles_identity(self) -> dict:
        endpoint = '/auth/api/v1/users/me'
        return self._get(endpoint)

    @lru_cache()
    def list_clients(self, account_id: str, **filters) -> dict:
        endpoint = f"/accounting/account/{account_id}/users/clients"
        if filters:
            searches = {f"search[{k}]": v for k, v in filters.items()}
        return self._get(endpoint, searches)
