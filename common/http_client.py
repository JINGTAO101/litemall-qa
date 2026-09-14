import allure
import requests

from common.config import load_config

_BASE_URL = load_config()["base_url"].rstrip("/")


def request(method, path, json=None, headers=None):
    url = _BASE_URL + path
    r = requests.request(method, url, json=json, headers=headers, timeout=10)
    allure.attach(
        f"{method} {url}\nheaders={headers}\nbody={json}",
        name="request",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        r.text,
        name="response",
        attachment_type=allure.attachment_type.TEXT,
    )
    return r