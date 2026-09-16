"""用例夹具：登录拿 Token；购物车 SKU=1 在用例前后清理，避免脏数据。"""
import pytest
from common.config import load_config
from common.http_client import request

@pytest.fixture
def token():
    """登录一次，返回 JWT，供需要鉴权的用例使用。"""
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
    """yield 前后都按 productIds=[1] 删除，保证加购类用例起点一致。"""
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
