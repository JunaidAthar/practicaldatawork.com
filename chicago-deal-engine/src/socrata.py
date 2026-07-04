"""Minimal, dependency-light Socrata (SODA) API client with paging + retries.

Socrata powers both the City of Chicago and Cook County open-data portals. No auth
is required; an optional app token (SOCRATA_APP_TOKEN) raises the rate limit.
"""
from __future__ import annotations

import os
import time
from typing import Optional

import requests


class SocrataError(RuntimeError):
    pass


class SocrataClient:
    def __init__(self, domain: str, app_token: Optional[str] = None,
                 page_size: int = 50000, timeout: int = 90):
        self.domain = domain.rstrip("/")
        self.app_token = app_token or os.getenv("SOCRATA_APP_TOKEN") or None
        self.page_size = page_size
        self.timeout = timeout
        self.session = requests.Session()
        if self.app_token:
            self.session.headers["X-App-Token"] = self.app_token

    def _url(self, dataset_id: str) -> str:
        return f"https://{self.domain}/resource/{dataset_id}.json"

    def _get(self, url: str, params: dict) -> list:
        for attempt in range(5):
            resp = self.session.get(url, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)          # exponential backoff
                continue
            raise SocrataError(f"{resp.status_code} {resp.url} :: {resp.text[:300]}")
        raise SocrataError(f"Gave up after retries: {url}")

    def probe(self, dataset_id: str) -> bool:
        """Cheap check that a dataset exists and responds."""
        self._get(self._url(dataset_id), {"$limit": 1})
        return True

    def query(self, dataset_id: str, **params) -> list:
        """Single request with arbitrary SoQL params (e.g. $select/$group/$where)."""
        return self._get(self._url(dataset_id), params)

    def fetch_all(self, dataset_id: str, select=None, where=None,
                  order: str = ":id", max_records: Optional[int] = None) -> list:
        """Page through an entire (filtered) dataset. `order` must be stable so
        offset paging doesn't skip/duplicate rows."""
        url = self._url(dataset_id)
        rows: list = []
        offset = 0
        while True:
            params = {"$limit": self.page_size, "$offset": offset, "$order": order}
            if select:
                params["$select"] = select if isinstance(select, str) else ",".join(select)
            if where:
                params["$where"] = where
            batch = self._get(url, params)
            if not batch:
                break
            rows.extend(batch)
            offset += self.page_size
            if len(batch) < self.page_size:
                break
            if max_records and len(rows) >= max_records:
                rows = rows[:max_records]
                break
        return rows
