from common.config import load_config
from common.http_client import request
from common.db import query_one
import base64
import json

def test_login_success():
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
    r = request("GET","/wx/auth/info")
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501

def test_info_invalid_token():
    r = request(
        "GET",
        "/wx/auth/info",
        headers={"X-Litemall-Token":"invalid_token"},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 501

def test_info_with_valid_token(token):
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
    cfg = load_config()
    r = request(
        "POST",
        "/wx/auth/login",
        json={"username": cfg["username"], "password": cfg["password"]},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["errno"] == 0
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