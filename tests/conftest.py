import pytest
from common.config import load_config
from common.http_client import request

@pytest.fixture
def token():
    cfg = load_config()
    r = request(
        "POST",
        "/wx/auth/login",
        json={"username":cfg["username"], "password":cfg["password"]},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    assert body["data"]["token"]
    return body["data"]["token"]

@pytest.fixture
def clear_cart(token):
    headers = {"X-Litemall-Token": token}
    request(
        "POST",
        "/wx/cart/delete",
        json={"productIds": [1]},
        headers=headers,
    )
    yield
    request(
        "POST",
        "/wx/cart/delete",
        json={"productIds": [1]},
        headers=headers,
    )
