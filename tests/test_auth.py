"""鉴权：登录与 /wx/auth/info。litemall 业务成败看 errno，HTTP 常为 200。"""
from common.config import load_config
from common.http_client import request
from common.db import query_one
import base64
import json


def test_login_success():
    """正确账号密码：errno=0 且返回 JWT。"""
    cfg = load_config()
    r = request(
        "POST",
        "/wx/auth/login",
        json={"username":cfg["username"], "password":cfg["password"]}
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    assert body["data"]["token"]

def test_login_failed():
    """密码错误：业务码 700，无 token。"""
    cfg = load_config()
    f = request(
        "POST",
        "/wx/auth/login",
        json={"username":cfg["username"], "password":"wrongpassword"},
    )
    body = f.json()
    assert f.status_code == 200
    assert body["errno"] == 700
    assert body.get("data") is None

def test_login_empty_password():
    """空密码：与错密相同，errno=700。"""
    cfg = load_config()
    r = request(
        "POST",
        "/wx/auth/login",
        json={"username":cfg["username"], "password":""},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 700
    assert body.get("data") is None

def test_info_without_token():
    """未带头：请登录，errno=501。"""
    r = request("GET","/wx/auth/info")
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501

def test_info_invalid_token():
    """非法 Token：仍是 501，不是 HTTP 401。"""
    r = request(
        "GET",
        "/wx/auth/info",
        headers={"X-Litemall-Token":"invalid_token"},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501

def test_info_with_valid_token(token):
    """有效 Token：info 成功，昵称与登录用户一致。"""
    cfg = load_config()
    r = request(
        "GET",
        "/wx/auth/info",
        headers={"X-Litemall-Token":token},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    assert body["data"]["nickName"] == cfg["username"]

def test_login_missing_username():
    """缺 username：参数不对。此处 401 是业务码，不是 HTTP 401。"""
    cfg = load_config()
    r = request(
        "POST",
        "/wx/auth/login",
        json={"password":cfg["password"]},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 401
    assert body.get("data") is None



def test_login_user_id_matches_db():
    """JWT 里的 userId 与 litemall_user.id 一致。"""
    cfg = load_config()
    r = request(
        "POST",
        "/wx/auth/login",
        json={"username": cfg["username"], "password": cfg["password"]},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
    # JWT 第二段是 payload；base64 长度须补齐为 4 的倍数
    payload = body["data"]["token"].split(".")[1]
    payload += "=" * (-len(payload) % 4)
    user_id = json.loads(base64.urlsafe_b64decode(payload))["userId"]
    row = query_one(
        "SELECT id, username FROM litemall_user WHERE username=%s",
        (cfg["username"],),
    )
    assert row is not None
    assert row["id"] == user_id
    assert row["username"] == cfg["username"]
