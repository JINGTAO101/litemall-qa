from common.http_client import request
from common.db import query_one


def test_order_submit_without_token():
    r = request(
        "POST",
        "/wx/order/submit",
        json={
            "cartId": 0,
            "addressId": 2,
            "couponId": -1,
            "message": "",
            "grouponRulesId": 0,
            "grouponLinkId": 0,
        },
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501


def test_order_submit_success(token, clear_cart):
    headers = {"X-Litemall-Token": token}
    listed = request("GET", "/wx/address/list", headers=headers).json()
    assert listed["errno"] == 0
    addr_list = listed["data"]["list"]
    if addr_list:
        address_id = addr_list[0]["id"]
    else:
        saved = request(
            "POST",
            "/wx/address/save",
            json={
                "id": 0,
                "name": "tester",
                "tel": "13811111111",
                "province": "Zhejiang",
                "city": "Hangzhou",
                "county": "Binjiang",
                "addressDetail": "xueyuan 1",
                "areaCode": "330108",
                "isDefault": True,
            },
            headers=headers,
        )
        assert saved.json()["errno"] == 0
        address_id = saved.json()["data"]
    r_add = request(
        "POST",
        "/wx/cart/add",
        json={"goodsId": 1181000, "productId": 1, "number": 1},
        headers=headers,
    )
    assert r_add.status_code == 200
    assert r_add.json()["errno"] == 0
    stock_before = query_one(
        "SELECT number FROM litemall_goods_product WHERE id=%s",
        (1,),
    )["number"]
    r = request(
        "POST",
        "/wx/order/submit",
        json={
            "cartId": 0,
            "addressId": address_id,
            "couponId": -1,
            "message": "",
            "grouponRulesId": 0,
            "grouponLinkId": 0,
        },
        headers=headers,
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    assert body["data"]["orderId"]
    order_id = body["data"]["orderId"]
    order_row = query_one(
        "SELECT id, user_id, deleted FROM litemall_order WHERE id=%s",
        (order_id,),
    )
    assert order_row is not None
    assert order_row["user_id"] == 1
    assert order_row["deleted"] == 0
    goods_row = query_one(
        "SELECT order_id, goods_id, product_id, number FROM litemall_order_goods WHERE order_id=%s",
        (order_id,),
    )
    assert goods_row["product_id"] == 1
    assert goods_row["goods_id"] == 1181000
    assert goods_row["number"] == 1
    stock_after = query_one(
        "SELECT number FROM litemall_goods_product WHERE id=%s",
        (1,),
    )["number"]
    assert stock_after == stock_before - 1
    r_cancel = request(
        "POST",
        "/wx/order/cancel",
        json={"orderId": order_id},
        headers=headers,
    )
    assert r_cancel.status_code == 200
    assert r_cancel.json()["errno"] == 0
    cancelled = query_one(
        "SELECT order_status, deleted FROM litemall_order WHERE id=%s",
        (order_id,),
    )
    assert cancelled["deleted"] == 0
    assert cancelled["order_status"] == 102
    goods_after = query_one(
        "SELECT order_id FROM litemall_order_goods WHERE order_id=%s",
        (order_id,),
    )
    assert goods_after is not None
    stock_restored = query_one(
        "SELECT number FROM litemall_goods_product WHERE id=%s",
        (1,),
    )["number"]
    assert stock_restored == stock_before