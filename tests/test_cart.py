from common.http_client import request
from common.db import query_one
from common.config import load_config

def test_cart_add_success(token, clear_cart):
    r = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 1, "number": 1},
        headers={"X-Litemall-Token": token},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    assert isinstance(body["data"], int)
    assert body["data"] > 0


def test_cart_index_after_add(token, clear_cart):
    r_add = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 1, "number": 1},
        headers={"X-Litemall-Token": token},
    )
    assert r_add.status_code == 200
    assert r_add.json()["errno"] == 0
    r = request(
        "GET",
        "/wx/cart/index",
        headers={"X-Litemall-Token": token},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    found = None
    for item in body["data"]["cartList"]:
        if item["goodsId"] == 1181000 and item["productId"] == 1:
            found = item
            break
    assert found is not None
    assert found["number"] >= 1

def test_cart_index_without_token():
    r = request("GET", "/wx/cart/index")
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501

def test_cart_index_invalid_token():
    r = request(
        "GET",
        "/wx/cart/index",
        headers={"X-Litemall-Token": "abc"},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501

def test_cart_add_number_zero(token, clear_cart):
    r = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 1, "number": 0},
        headers={"X-Litemall-Token": token},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 401

def test_cart_add_out_of_stock(token, clear_cart):
    r = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 6, "number": 1},
        headers={"X-Litemall-Token": token},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 711


def test_cart_add_same_sku_accumulates(token, clear_cart):
    headers = {"X-Litemall-Token": token}
    payload = {"goodsId": 1181000, "productId": 1, "number": 1}
    r1 = request("POST", "/wx/cart/add", json=payload, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["errno"] == 0
    body1 = request("GET", "/wx/cart/index", headers=headers).json()
    found = None
    for item in body1["data"]["cartList"]:
        if item["goodsId"] == 1181000 and item["productId"] == 1:
            found = item
            break
    assert found is not None
    cart_id = found["id"]
    number_before = found["number"]
    r2 = request("POST", "/wx/cart/add", json=payload, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["errno"] == 0
    body2 = request("GET", "/wx/cart/index", headers=headers).json()
    found2 = None
    for item in body2["data"]["cartList"]:
        if item["goodsId"] == 1181000 and item["productId"] == 1:
            found2 = item
            break
    assert found2 is not None
    assert found2["id"] == cart_id
    assert found2["number"] == number_before + 1

def test_cart_delete_sku(token, clear_cart):
    headers = {"X-Litemall-Token": token}
    r_add = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 1, "number": 1},
        headers=headers,
    )
    assert r_add.status_code == 200
    assert r_add.json()["errno"] == 0
    r_del = request(
        "POST",
        "/wx/cart/delete",
        json={"productIds": [1]},
        headers=headers,
    )
    assert r_del.status_code == 200
    assert r_del.json()["errno"] == 0
    body = request("GET", "/wx/cart/index", headers=headers).json()
    assert body["errno"] == 0
    found = None
    for item in body["data"]["cartList"]:
        if item["productId"] == 1:
            found = item
            break
    assert found is None

def test_cart_add_matches_db(token, clear_cart):
    headers = {"X-Litemall-Token": token}
    r = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 1, "number": 1},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["errno"] == 0
    cfg = load_config()
    user = query_one(
        "SELECT id FROM litemall_user WHERE username=%s",
        (cfg["username"],),
    )
    row = query_one(
        "SELECT id, user_id, goods_id, product_id, number, deleted "
        "FROM litemall_cart WHERE user_id=%s AND product_id=%s AND deleted=0",
        (user["id"], 1),
    )
    assert row is not None
    assert row["goods_id"] == 1181000
    assert row["number"] == 1